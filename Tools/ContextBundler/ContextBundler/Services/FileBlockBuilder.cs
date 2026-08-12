using System.Security.Cryptography;
using System.Text;
using ContextBundler.Models;

namespace ContextBundler.Services;

internal static class FileBlockBuilder
{
    /// <summary>Elabora una singola entry: legge il file, applica gli estratti a
    /// range se richiesti, esegue le diagnostiche (secret/mojibake/control/json/
    /// fence) e costruisce il blocco &lt;&lt;&lt;FILE...&gt;&gt;&gt; da inserire nel
    /// bundle. Ritorna null se il file e' mancante o binario (gia' registrato in
    /// warnings), senza produrre alcun blocco per quella entry.</summary>
    public static ProcessedFile? Build(string rootPath, string rawEntry, BundleWarnings warnings, Action<string> log)
    {
        var (rel, ranges) = EntryParser.Parse(rawEntry);
        var fullPath = Path.GetFullPath(Path.Combine(rootPath, rel));

        if (!File.Exists(fullPath))
        {
            warnings.Missing.Add(rawEntry);
            return null;
        }

        var bytes = File.ReadAllBytes(fullPath);
        if (FileTypeClassifier.IsLikelyBinary(bytes))
        {
            warnings.SkippedBinary.Add(rel);
            return null;
        }

        var ext = Path.GetExtension(fullPath);
        _ = FileTypeClassifier.GetLanguage(ext); // calcolato per parita' col codice originale, non ancora usato nel blocco

        var label = rel.Replace('\\', '/');

        // Lettura sempre in UTF-8 esplicito, stesso path sia per file interi sia per estratti a
        // range: nessuna doppia conversione tra lettura del sorgente e scrittura del bundle
        // (sezione 2.3).
        var (sourceBytes, hasBom) = EncodingDiagnostics.StripBom(bytes);
        var fullText = Encoding.UTF8.GetString(sourceBytes);

        string content;
        string? rangeLabel = null;

        if (ranges.Count > 0)
        {
            var allLines = fullText.Split(["\r\n", "\r", "\n"], StringSplitOptions.None);
            var clamped = new List<(int From, int To)>();

            foreach (var r in ranges)
            {
                var from = Math.Max(1, r.Start);
                var to = Math.Min(allLines.Length, r.End);
                if (from != r.Start || to != r.End)
                    log($"Attenzione: range richiesto {r.Start}-{r.End} per {label} troncato a {from}-{to} (file di {allLines.Length} righe)");
                if (from > to)
                    continue; // fuori dai limiti del file, salto questo segmento
                clamped.Add((from, to));
            }

            var pieces = new List<string>();
            (int From, int To)? prev = null;
            foreach (var (from, to) in clamped)
            {
                if (prev is (int pFrom, int pTo) && from > pTo + 1)
                    pieces.Add($">>>> [righe {pTo + 1}-{from - 1} omesse] <<<<");
                pieces.Add(string.Join(Environment.NewLine, allLines.Skip(from - 1).Take(to - from + 1)));
                prev = (from, to);
            }

            content = string.Join(Environment.NewLine, pieces);
            rangeLabel = string.Join(", ", clamped.Select(r => $"{r.From}-{r.To}"));
            label += $" (righe {rangeLabel} di {allLines.Length})";
        }
        else
        {
            content = fullText;
        }

        SecretScanner.Scan(label, content, warnings);

        if (EncodingDiagnostics.HasMojibake(content))
            warnings.Mojibake.Add(label);

        if (LiteralControlSequenceScanner.HasLiteralControlSequences(content))
            warnings.LiteralControl.Add(label);

        // T2.2: validazione JSON prima/dopo l'inclusione nel bundle, solo per file
        // .json. "Prima" e' il testo sorgente cosi' come letto dal file (fullText);
        // "dopo" e' esattamente il contenuto che finira' tra i delimitatori
        // <<<FILE ...>>> / <<<END FILE>>> (content, identico a quanto usato per
        // l'hash subito sotto).
        string? jsonParseBefore = null;
        string? jsonParseAfter = null;
        var isJsonFile = FileTypeClassifier.IsJsonFile(ext);
        if (isJsonFile)
        {
            jsonParseBefore = JsonValidator.TryParse(fullText, out var beforeError) ? "ok" : $"invalid ({beforeError})";
            jsonParseAfter = JsonValidator.TryParse(content, out var afterError) ? "ok" : $"invalid ({afterError})";
            if (jsonParseBefore != "ok" || jsonParseAfter != "ok")
                warnings.Json.Add($"{label}: json_parse_before={jsonParseBefore}, json_parse_after={jsonParseAfter}");
        }

        // T2.3: conteggio dei marcatori di fence Markdown, solo per file .md.
        if (FileTypeClassifier.IsMarkdownFile(ext))
        {
            var fenceCount = MarkdownFenceScanner.CountFenceMarkers(content);
            if (fenceCount % 2 != 0)
                warnings.MdFence.Add($"{label}: {fenceCount} marcatori fence trovati (numero dispari, possibile fence non chiuso)");
        }

        // Hash e lunghezza sono calcolati sul contenuto UTF-8 effettivamente inserito nel bundle.
        var contentBytes = Encoding.UTF8.GetBytes(content);
        var sha256 = Convert.ToHexString(SHA256.HashData(contentBytes)).ToLowerInvariant();

        var pathAttr = rel.Replace('\\', '/');
        var linesAttr = rangeLabel is null ? "" : $" lines=\"{rangeLabel}\"";
        var jsonAttr = isJsonFile
            ? $" json_parse_before=\"{jsonParseBefore}\" json_parse_after=\"{jsonParseAfter}\""
            : "";

        var fileBlock = new StringBuilder();
        fileBlock.Append($"<<<FILE path=\"{pathAttr}\" bytes=\"{contentBytes.Length}\" sha256=\"{sha256}\"{linesAttr}{jsonAttr}>>>");
        fileBlock.Append(Environment.NewLine);
        fileBlock.Append(content);
        fileBlock.Append(Environment.NewLine);
        fileBlock.Append("<<<END FILE>>>");
        fileBlock.Append(Environment.NewLine);
        fileBlock.Append(Environment.NewLine);

        return new ProcessedFile
        {
            Rel = rel,
            FileBlockText = fileBlock.ToString(),
            ContentBytesLength = contentBytes.Length,
            HadBom = hasBom,
        };
    }
}
