using System.Runtime.InteropServices;

namespace WinFix.Agent;

public static class SystemInformation
{
    public static object Collect(bool mock)
    {
        if (!OperatingSystem.IsWindows() && !mock)
            throw new PlatformNotSupportedException("Real diagnostics require Windows.");
        return new
        {
            platform = mock ? "Mock" : "Windows",
            computerName = mock ? "MOCK-PC" : Environment.MachineName,
            osDescription = mock ? "Synthetic test fixture" : RuntimeInformation.OSDescription,
            osVersion = mock ? "fixture" : Environment.OSVersion.Version.ToString(),
            architecture = RuntimeInformation.OSArchitecture.ToString(),
            uptimeMilliseconds = Environment.TickCount64,
            timeZone = TimeZoneInfo.Local.Id
        };
    }
}
