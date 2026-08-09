using ContextBundler.Models;

namespace ContextBundler.Services;

/// <summary>Analizza una riga di entry ("path" oppure "path:120-180,133-152")
/// separando il path relativo dagli eventuali estratti a range richiesti.</summary>
internal static class EntryParser
{
    public static (string Path, List<FileRange> Ranges) Parse(string entry)
    {
        var idx = entry.LastIndexOf(':');
        if (idx > 1) // idx > 1 evita falsi positivi su lettere di drive Windows tipo "C:\..."
        {
            var rangePart = entry[(idx + 1)..];
            var segments = rangePart.Split(',', StringSplitOptions.TrimEntries | StringSplitOptions.RemoveEmptyEntries);
            var ranges = new List<FileRange>();
            var allValid = segments.Length > 0;

            foreach (var seg in segments)
            {
                var dash = seg.IndexOf('-');
                if (dash > 0 &&
                    int.TryParse(seg[..dash], out var s) &&
                    int.TryParse(seg[(dash + 1)..], out var e))
                {
                    ranges.Add(new FileRange(s, e));
                }
                else
                {
                    allValid = false;
                    break;
                }
            }

            if (allValid)
                return (entry[..idx], ranges);
        }
        return (entry, []);
    }
}
