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
                stream.Seek(-1, SeekOrigin.End);
                if (stream.ReadByte() != '\n') throw new InvalidDataException("Incomplete audit journal record");
                stream.Position = 0;
            }
            var technicians = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            var completed = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            using var reader = new StreamReader(stream, new UTF8Encoding(false, true), detectEncodingFromByteOrderMarks: false, leaveOpen: true);
            while (reader.ReadLine() is { } line)
            {
                using var document = JsonDocument.Parse(line);
                if (document.RootElement.ValueKind != JsonValueKind.Object || document.RootElement.EnumerateObject().Count() != 4)
                    throw new InvalidDataException("Invalid audit entry fields");
                var entry = document.Deserialize<Entry>() ?? throw new InvalidDataException("Invalid audit entry");
                if (entry.At == default || (entry.RequestId is not null && !Guid.TryParseExact(entry.RequestId, "D", out _)))
                    throw new InvalidDataException("Invalid audit timestamp or request ID");
                if (entry.Outcome is "accepted" or "completed")
                {
                    if (entry.RequestId is null || !Guid.TryParseExact(entry.TechnicianId, "D", out _))
                        throw new InvalidDataException("Missing audit identity");
                    if (entry.Outcome == "accepted")
                    {
                        if (!accepted.Add(entry.RequestId)) throw new InvalidDataException("Duplicate audit reservation");
                        technicians.Add(entry.RequestId, entry.TechnicianId!);
                    }
                    else if (!technicians.TryGetValue(entry.RequestId, out var technician) || technician != entry.TechnicianId || !completed.Add(entry.RequestId))
                        throw new InvalidDataException("Audit completion without a matching reservation");
                }
                else if (entry.TechnicianId is not null || entry.Outcome is not
                         ("emergency_stop" or "unauthorized" or "json_required" or "invalid_request" or
                          "request_too_large" or "wrong_device" or "replay"))
                    throw new InvalidDataException("Unknown audit outcome");
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
            var bytes = Encoding.UTF8.GetBytes(JsonSerializer.Serialize(
                new Entry(DateTimeOffset.UtcNow, requestId, technicianId, outcome)) + "\n");
            if (stream.Length + bytes.Length > MaximumBytes) throw new IOException("Audit journal full");
            stream.Write(bytes);
            stream.Flush(flushToDisk: true);
        }
    }

    public void Dispose() => stream.Dispose();
    [JsonUnmappedMemberHandling(JsonUnmappedMemberHandling.Disallow)]
    private sealed record Entry(
        [property: JsonRequired] DateTimeOffset At,
        [property: JsonRequired] string? RequestId,
        [property: JsonRequired] string? TechnicianId,
        [property: JsonRequired] string Outcome);
}
