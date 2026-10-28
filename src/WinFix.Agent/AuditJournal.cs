using System.Text;
using System.Text.Json;

namespace WinFix.Agent;

// Persist reservations before diagnostics; restarting the agent cannot replay a request.
public sealed class AuditJournal : IDisposable
{
    private readonly FileStream stream;
    private readonly HashSet<string> accepted = new(StringComparer.OrdinalIgnoreCase);
    private readonly object gate = new();
    private const long MaximumBytes = 10 * 1024 * 1024;

    public AuditJournal(string path)
    {
        stream = new FileStream(path, FileMode.OpenOrCreate, FileAccess.ReadWrite, FileShare.Read);
        if (stream.Length > MaximumBytes) throw new IOException("Audit journal full; archive and rotate credentials.");
        using var reader = new StreamReader(stream, Encoding.UTF8, leaveOpen: true);
        while (reader.ReadLine() is { } line)
        {
            var entry = JsonSerializer.Deserialize<Entry>(line) ?? throw new InvalidDataException("Invalid audit entry");
            if (entry.Outcome == "accepted") accepted.Add(entry.RequestId ?? throw new InvalidDataException("Missing request ID"));
        }
        stream.Seek(0, SeekOrigin.End);
    }

    public bool TryAccept(string requestId, string technicianId)
    {
        lock (gate)
        {
            if (accepted.Contains(requestId)) return false;
            Record(requestId, technicianId, "accepted");
            accepted.Add(requestId);
            return true;
        }
    }

    public void Record(string? requestId, string? technicianId, string outcome)
    {
        lock (gate)
        {
            var bytes = Encoding.UTF8.GetBytes(JsonSerializer.Serialize(
                new Entry(DateTimeOffset.UtcNow, requestId, technicianId, outcome)) + "\n");
            if (stream.Length + bytes.Length > MaximumBytes) throw new IOException("Audit journal full");
            stream.Write(bytes);
            stream.Flush(flushToDisk: true);
        }
    }

    public void Dispose() => stream.Dispose();
    private sealed record Entry(DateTimeOffset At, string? RequestId, string? TechnicianId, string Outcome);
}
