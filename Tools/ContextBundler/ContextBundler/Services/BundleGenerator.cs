using System.Text;

namespace ContextBundler.Services;

/// <summary>Orchestratore: per ogni entry richiesta invoca FileBlockBuilder,
/// accumula i blocchi prodotti e i byte totali, poi chiude il bundle con
/// l'header prodotto da BundleHeaderBuilder. Nessuna logica di parsing,
/// diagnostica o formattazione vive qui (vedi i singoli servizi in questo
/// namespace).</summary>
internal static class BundleGenerator
{
    public static Models.BundleResult Generate(
        string rootPath,
        string sourceListName,
        List<string> entries,
        Action<string> log,
        bool toBase64 = false)
    {
        var warnings = new Models.BundleWarnings();
        var bomFiles = new List<string>();
        long totalBytes = 0;
        var fileBlocks = new StringBuilder();

        foreach (var rawEntry in entries)
        {
            var processed = FileBlockBuilder.Build(rootPath, rawEntry, warnings, log);
            if (processed is null)
                continue; // missing o binario: gia' registrato in warnings

            if (processed.HadBom)
                bomFiles.Add(processed.Rel);
            fileBlocks.Append(processed.FileBlockText);
            totalBytes += processed.ContentBytesLength;
        }

        var header = BundleHeaderBuilder.Build(rootPath, sourceListName, bomFiles, warnings);
        var bundleText = header + fileBlocks.ToString();
        var includedCount = entries.Count - warnings.Missing.Count - warnings.SkippedBinary.Count;

        // T2.1: flag propagato. Conversione base64 reale in T2.2.
        return new Models.BundleResult
        {
            BundleText = bundleText,
            IncludedCount = includedCount,
            TotalEntries = entries.Count,
            TotalBytes = totalBytes,
            Warnings = warnings,
            ToBase64 = toBase64,
        };
    }
}
