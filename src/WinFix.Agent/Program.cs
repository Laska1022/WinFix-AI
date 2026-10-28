using System.Net;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using System.Text;
using System.Text.Json;
using WinFix.Agent;

var interactive = args.Length == 0 || (args.Length == 1 && args[0] == "--demo-menu");
if (interactive)
{
    try
    {
        var path = InteractiveConsole.Select(args.Length == 1);
        if (path is null) return;
        args = new[] { "serve", path };
    }
    catch (Exception error) when (error is IOException or UnauthorizedAccessException or System.ComponentModel.Win32Exception)
    {
        Console.WriteLine(InteractiveConsole.Text("Setup failed. Check folder permissions and available disk space. Press Enter to close.",
            "Ошибка настройки. Проверьте права доступа к папке и свободное место. Нажмите Enter для выхода."));
        Console.ReadLine();
        Environment.ExitCode = 1;
        return;
    }
}

if (args.Length == 2 && args[0] == "init")
{
    Bootstrap.Create(args[1]);
    return;
}
if (args.Length != 2 || args[0] != "serve")
    throw new ArgumentException("Usage: WinFix.Agent init NEW_PRIVATE_DIRECTORY | serve CONFIG_PATH");

var config = JsonSerializer.Deserialize<AgentConfig>(File.ReadAllText(args[1]))
    ?? throw new InvalidDataException("Missing configuration");
config.Validate();
if (!OperatingSystem.IsWindows() && !config.Mock)
    throw new PlatformNotSupportedException("Real diagnostics require Windows; Mock must be explicit for tests.");
using var certificate = X509CertificateLoader.LoadPkcs12FromFile(config.CertificatePath, null);
using var audit = new AuditJournal(config.AuditPath);
var tokenHash = Convert.FromHexString(config.TokenSha256);
var builder = WebApplication.CreateBuilder(Array.Empty<string>());
// Do not read ASPNETCORE_URLS or enable an incidental HTTP listener.
builder.Logging.ClearProviders();
builder.WebHost.ConfigureKestrel(server =>
{
    server.AddServerHeader = false;
    server.Limits.MaxRequestBodySize = 4096;
    server.Limits.RequestHeadersTimeout = TimeSpan.FromSeconds(10);
    server.Limits.KeepAliveTimeout = TimeSpan.FromSeconds(15);
    server.Limits.MaxConcurrentConnections = 32;
    server.Listen(IPAddress.Parse(config.BindAddress), config.Port, listen => listen.UseHttps(certificate));
});
await using var app = builder.Build();
app.MapPost("/v1/diagnostics/system", async (HttpContext context) =>
{
    context.Response.Headers.CacheControl = "no-store";
    string? requestId = null;
    IResult Reject(int status, string code)
    {
        audit.Record(requestId, null, code);
        return Results.Json(new { error = code }, statusCode: status);
    }
    try
    {
        if (File.Exists(config.StopFile)) return Reject(503, "emergency_stop");
        var authorization = context.Request.Headers.Authorization.ToString();
        if (!authorization.StartsWith("Bearer ", StringComparison.Ordinal) ||
            !CryptographicOperations.FixedTimeEquals(
                SHA256.HashData(Encoding.UTF8.GetBytes(authorization[7..])), tokenHash) ||
            DateTimeOffset.UtcNow >= config.ExpiresAt)
            return Reject(401, "unauthorized");

        if (!context.Request.HasJsonContentType()) return Reject(415, "json_required");
        DiagnosticRequest? request;
        try { request = await context.Request.ReadFromJsonAsync<DiagnosticRequest>(context.RequestAborted); }
        catch (JsonException) { return Reject(400, "invalid_request"); }
        catch (BadHttpRequestException) { return Reject(413, "request_too_large"); }
        if (request is null || !Guid.TryParseExact(request.RequestId, "D", out _) ||
            Math.Abs((DateTimeOffset.UtcNow - request.IssuedAt).TotalSeconds) > 60)
            return Reject(400, "invalid_request");
        requestId = request.RequestId!.ToLowerInvariant();
        if (request.DeviceId != config.DeviceId) return Reject(403, "wrong_device");
        if (!audit.TryAccept(requestId, config.TechnicianId)) return Reject(409, "replay");

        // No shell, supplied commands, registry writes, or privilege elevation.
        var result = new
        {
            schemaVersion = 1,
            requestId,
            deviceId = config.DeviceId,
            collectedAt = DateTimeOffset.UtcNow,
            mock = config.Mock,
            system = SystemInformation.Collect(config.Mock)
        };
        audit.Record(requestId, config.TechnicianId, "completed");
        return Results.Json(result);
    }
    catch (IOException) { return Results.Json(new { error = "audit_unavailable" }, statusCode: 503); }
    catch (UnauthorizedAccessException) { return Results.Json(new { error = "audit_unavailable" }, statusCode: 503); }
});
if (interactive)
{
    try
    {
        await app.StartAsync();
        Console.WriteLine(InteractiveConsole.Text("LOCAL SESSION ACTIVE. Press Enter to STOP and disconnect.",
            "ЛОКАЛЬНЫЙ СЕАНС АКТИВЕН. Нажмите Enter для ОСТАНОВКИ и отключения."));
        Console.WriteLine($"https://127.0.0.1:{config.Port} | Device: {config.DeviceId} | Expires: {config.ExpiresAt:O}");
        await Task.WhenAny(app.WaitForShutdownAsync(), Task.Run(() => Console.ReadLine()));
        File.WriteAllText(config.StopFile, "Stopped by owner");
        await app.StopAsync();
    }
    catch (IOException)
    {
        Console.WriteLine(InteractiveConsole.Text("Could not start or finish the session. Close any other WinFix session and check disk access. Press Enter to exit.",
            "Не удалось запустить или завершить сеанс. Закройте другой сеанс WinFix и проверьте доступ к диску. Нажмите Enter для выхода."));
        Console.ReadLine();
        Environment.ExitCode = 1;
    }
}
else
{
    Console.WriteLine($"WinFix READ ONLY active; device={config.DeviceId}; mock={config.Mock}. Create the configured stop file or press Ctrl+C to disconnect.");
    await app.RunAsync();
}

namespace WinFix.Agent
{
    public sealed record DiagnosticRequest(string? DeviceId, string? RequestId, DateTimeOffset IssuedAt);
    public sealed record AgentConfig(
        string DeviceId, string TechnicianId, string TokenSha256, DateTimeOffset ExpiresAt,
        string BindAddress, int Port, string CertificatePath, string AuditPath, string StopFile, bool Mock)
    {
        public void Validate()
        {
            if (!Guid.TryParseExact(DeviceId, "D", out _) || !Guid.TryParseExact(TechnicianId, "D", out _) ||
                TokenSha256.Length != 64 || !TokenSha256.All(Uri.IsHexDigit) ||
                !IPAddress.TryParse(BindAddress, out _) || Port is < 1 or > 65535 ||
                ExpiresAt > DateTimeOffset.UtcNow.AddHours(1) ||
                !Path.IsPathFullyQualified(CertificatePath) || !Path.IsPathFullyQualified(AuditPath) ||
                !Path.IsPathFullyQualified(StopFile))
                throw new InvalidDataException("Invalid configuration; credentials must expire within one hour.");
        }
    }
}
