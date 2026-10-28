using System.Text;
using System.Text.Json;

namespace WinFix.Agent;

public static class InteractiveConsole
{
    public static bool Russian { get; private set; }
    public static string Text(string english, string russian) => Russian ? russian : english;

    public static string? Select(bool demo)
    {
        Console.OutputEncoding = Encoding.UTF8;
        Console.InputEncoding = Encoding.UTF8;
        Console.WriteLine("WinFix AI - Read-only prototype / Прототип диагностики");
        if (!OperatingSystem.IsWindows() && !demo)
        {
            Console.WriteLine("This application needs Windows. For synthetic developer tests use --demo-menu.");
            Environment.ExitCode = 1;
            return null;
        }
        Console.WriteLine("1. English\n2. Русский\n0. Exit / Выход");
        var language = Console.ReadLine();
        if (language is null or "0") return null;
        if (language != "1" && language != "2") return null;
        Russian = language == "2";
        if (demo) Console.WriteLine("DEMO / ДЕМО: SYNTHETIC DATA ONLY / ТОЛЬКО ТЕСТОВЫЕ ДАННЫЕ");
        var root = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "WinFixAI", "Data");
        // Only the explicit developer demo can redirect its test outputs.
        if (demo && Environment.GetEnvironmentVariable("WINFIX_DEMO_DATA_DIR") is { Length: > 0 } testRoot)
            root = Path.GetFullPath(testRoot);
        while (true)
        {
            Console.WriteLine(Text(
                "\n1. Collect basic diagnostics on this PC\n2. Start a LOCAL read-only test session\n0. Exit\nNo repairs or internet access are started automatically.",
                "\n1. Собрать базовую диагностику этого ПК\n2. Запустить ЛОКАЛЬНЫЙ тестовый сеанс\n0. Выход\nИсправления и доступ через интернет автоматически не запускаются."));
            switch (Console.ReadLine())
            {
                case null: case "0": return null;
                case "1":
                    var directory = PrivateDirectory.Create(Path.Combine(root, "Reports", Guid.NewGuid().ToString()));
                    var report = new { schemaVersion = 1, collectedAt = DateTimeOffset.UtcNow, mock = demo, system = SystemInformation.Collect(demo) };
                    var json = JsonSerializer.Serialize(report, new JsonSerializerOptions { WriteIndented = true });
                    File.WriteAllText(Path.Combine(directory, "system-information.json"), json);
                    Console.WriteLine(json);
                    Console.WriteLine(Text("Private report saved in: ", "Отчёт сохранён в закрытой папке: ") + directory);
                    break;
                case "2":
                    Console.WriteLine(Text(
                        "Only authorize a computer you own or administer. This session is LOCAL ONLY and expires in one hour. Remote setup still needs a technician. Type START to consent, or Enter to cancel:",
                        "Продолжайте только с разрешения владельца ПК. Сеанс доступен ТОЛЬКО ЛОКАЛЬНО и истекает через час. Для удалённого доступа нужна настройка специалистом. Введите СТАРТ для согласия или Enter для отмены:"));
                    var consent = Console.ReadLine();
                    if (consent != "START" && consent != "СТАРТ") break;
                    var session = Path.Combine(root, "Sessions", Guid.NewGuid().ToString());
                    Bootstrap.Create(session);
                    var configPath = Path.Combine(session, "agent.json");
                    if (demo)
                    {
                        var config = JsonSerializer.Deserialize<AgentConfig>(File.ReadAllText(configPath))!;
                        File.WriteAllText(configPath, JsonSerializer.Serialize(config with { Mock = true }));
                    }
                    Console.WriteLine(Text("Private session folder: ", "Закрытая папка сеанса: ") + session);
                    Console.WriteLine(Text("Do not send its private key or token in chat. Close this window to disconnect.",
                        "Не отправляйте закрытый ключ и токен в чат. Закройте окно для отключения."));
                    return configPath;
                default:
                    Console.WriteLine(Text("Choose 1, 2 or 0.", "Выберите 1, 2 или 0."));
                    break;
            }
        }
    }
}
