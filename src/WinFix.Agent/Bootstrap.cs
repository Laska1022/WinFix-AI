using System.Diagnostics;
using System.Net;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using System.Security.Principal;
using System.Text;
using System.Text.Json;

namespace WinFix.Agent;

public static class Bootstrap
{
    public static void Create(string directory)
    {
        var path = Path.GetFullPath(directory);
        if (Directory.Exists(path) || File.Exists(path)) throw new IOException("Choose a new private directory; refusing to overwrite credentials.");
        Directory.CreateDirectory(path);
        // Protect credentials BEFORE writing. Init must be run by the authorizing owner.
        if (OperatingSystem.IsWindows())
        {
            var sid = WindowsIdentity.GetCurrent().User?.Value ?? throw new InvalidOperationException("No Windows identity");
            var start = new ProcessStartInfo("icacls.exe") { UseShellExecute = false, RedirectStandardOutput = true, RedirectStandardError = true };
            foreach (var arg in new[] { path, "/inheritance:r", "/grant:r", $"*{sid}:(OI)(CI)F", "*S-1-5-18:(OI)(CI)F" }) start.ArgumentList.Add(arg);
            using var process = Process.Start(start) ?? throw new IOException("Cannot secure credential directory");
            process.WaitForExit();
            if (process.ExitCode != 0) throw new IOException("Cannot secure credential directory; no credentials written");
        }
        else File.SetUnixFileMode(path, UnixFileMode.UserRead | UnixFileMode.UserWrite | UnixFileMode.UserExecute);

        using var rsa = RSA.Create(3072);
        var request = new CertificateRequest("CN=localhost", rsa, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
        var san = new SubjectAlternativeNameBuilder();
        san.AddDnsName("localhost"); san.AddIpAddress(IPAddress.Loopback);
        request.CertificateExtensions.Add(san.Build());
        request.CertificateExtensions.Add(new X509BasicConstraintsExtension(false, false, 0, true));
        request.CertificateExtensions.Add(new X509KeyUsageExtension(X509KeyUsageFlags.DigitalSignature | X509KeyUsageFlags.KeyEncipherment, true));
        request.CertificateExtensions.Add(new X509EnhancedKeyUsageExtension(new OidCollection { new("1.3.6.1.5.5.7.3.1") }, true));
        using var cert = request.CreateSelfSigned(DateTimeOffset.UtcNow.AddMinutes(-1), DateTimeOffset.UtcNow.AddDays(7));
        File.WriteAllBytes(Path.Combine(path, "server.pfx"), cert.Export(X509ContentType.Pfx));
        File.WriteAllText(Path.Combine(path, "server-cert.pem"), cert.ExportCertificatePem());
        var token = Convert.ToHexString(RandomNumberGenerator.GetBytes(32));
        File.WriteAllText(Path.Combine(path, "client-token.txt"), token);
        var config = new AgentConfig(Guid.NewGuid().ToString(), Guid.NewGuid().ToString(),
            Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(token))), DateTimeOffset.UtcNow.AddHours(1),
            "127.0.0.1", 8443, Path.Combine(path, "server.pfx"), Path.Combine(path, "audit.jsonl"), Path.Combine(path, "STOP"), false);
        File.WriteAllText(Path.Combine(path, "agent.json"), JsonSerializer.Serialize(config, new JsonSerializerOptions { WriteIndented = true }));
        Console.WriteLine("Owner-authorized, one-hour read-only session initialized. Credentials are in the private directory, never printed. See docs/SETUP.md before starting.");
    }
}
