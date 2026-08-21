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
        bool toBase64 = false,
        bool sessionDirectiveEnabled = true,
        string[]? sessionDirectiveLines = null)
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

        // T8.1_Estemporaneo: blocco <session_directive> in coda, solo per request
        // start-session e solo se abilitato in appsettings.json. Testo da config
        // (DirectiveLines) o fallback cablato. TrimEnd/newline espliciti per
        // garantire una singola riga vuota di separazione dall'ultimo
        // <<<END FILE>>>, indipendentemente dal whitespace finale di fileBlocks.
        var directive = SessionDirectiveBuilder.Build(sourceListName, sessionDirectiveEnabled, sessionDirectiveLines);
        var bundleText = directive.Length == 0
            ? header + fileBlocks.ToString()
            : header + fileBlocks.ToString().TrimEnd() + "\n\n" + directive + "\n";

        var includedCount = entries.Count - warnings.Missing.Count - warnings.SkippedBinary.Count;

        // T2.2: se richiesto, converte l'intero bundle in base64 (UTF-8 → base64 standard senza line-break)
        if (toBase64)
        {
            var utf8 = Encoding.UTF8.GetBytes(bundleText);
            bundleText = Convert.ToBase64String(utf8);
        }

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
