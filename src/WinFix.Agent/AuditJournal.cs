using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;

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
        try
        {
            if (stream.Length > MaximumBytes) throw new IOException("Audit journal full; archive and rotate credentials.");
            if (stream.Length > 0)
            {
                // ReadLine accepts an unterminated last record. Appending to it would
                // concatenate JSON objects and corrupt history on the next restart.
                stream.Seek(-1, SeekOrigin.End);
                if (stream.ReadByte() != '\n')
                    throw new InvalidDataException("Unterminated audit entry; archive and rotate credentials.");
                stream.Seek(0, SeekOrigin.Begin);
            }
            using var reader = new StreamReader(stream, Encoding.UTF8, leaveOpen: true);
            while (reader.ReadLine() is { } line)
            {
                var entry = JsonSerializer.Deserialize<Entry>(line) ?? throw new InvalidDataException("Invalid audit entry");
                entry.Validate();
                if (entry.Outcome == "accepted") accepted.Add(entry.RequestId!);
            }
            stream.Seek(0, SeekOrigin.End);
        }
        catch
        {
            stream.Dispose();
            throw;
        }
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
            var entry = new Entry(DateTimeOffset.UtcNow, requestId, technicianId, outcome);
            entry.Validate();
            var bytes = Encoding.UTF8.GetBytes(JsonSerializer.Serialize(entry) + "\n");
            if (stream.Length + bytes.Length > MaximumBytes) throw new IOException("Audit journal full");
            stream.Write(bytes);
            stream.Flush(flushToDisk: true);
        }
    }

    public void Dispose() => stream.Dispose();
    private sealed record Entry(
        [property: JsonRequired] DateTimeOffset At,
        [property: JsonRequired] string? RequestId,
        [property: JsonRequired] string? TechnicianId,
        [property: JsonRequired] string Outcome)
    {
        public void Validate()
        {
            // Null identities are intentional only for the relevant denial outcomes.
            // Missing fields, unknown outcomes and malformed IDs must never erase history.
            var validIdentities = Outcome switch
            {
                "accepted" or "completed" => Guid.TryParseExact(RequestId, "D", out _) &&
                    Guid.TryParseExact(TechnicianId, "D", out _),
                "wrong_device" or "replay" => Guid.TryParseExact(RequestId, "D", out _) && TechnicianId is null,
                "emergency_stop" or "unauthorized" or "json_required" or "invalid_request" or "request_too_large"
                    => RequestId is null && TechnicianId is null,
                _ => false
            };
            if (At == default || !validIdentities)
                throw new InvalidDataException("Invalid audit entry; archive and rotate credentials.");
        }
    }
}
