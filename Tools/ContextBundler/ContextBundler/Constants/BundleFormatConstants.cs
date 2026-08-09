using System.Text.RegularExpressions;

namespace ContextBundler.Constants;

internal static class BundleFormatConstants
{
    public const int SizeWarningBytes = 300 * 1024; // soglia solo informativa, non blocca nulla

    // Predisposizione per una futura modalita' di escaping alternativa (non implementata ora):
    // l'unico valore supportato oggi e' "none" - nessuna trasformazione sul Markdown sorgente,
    // il contenuto va tra i delimitatori cosi' com'e' (sezione 2.2 del piano).
    public const string MarkdownEscaping = "none";

    // T3.1: versione del formato del bundle (delimitatori + header dichiarativo),
    // distinta e indipendente dalla versione del programma ContextBundler
    // (riportata subito sotto come "ContextBundler V1.2"). Cambia solo quando
    // cambia la struttura del formato stesso (es. delimitatori, attributi
    // obbligatori dell'header), non ad ogni release del programma.
    public const int BundleFormatVersion = 2;

    // T3.1: dichiara che gli EOL originali dei file sorgente (CRLF/LF/CR) sono
    // preservati cosi' come letti, senza normalizzazione, quando il contenuto
    // finisce tra i delimitatori del bundle (vale per file interi; per gli
    // estratti a range il join tra le righe selezionate usa Environment.NewLine,
    // vedi commento piu' sotto sulla ricostruzione da allLines).
    public const string NewlineRepresentation = "preserved";

    public static readonly Dictionary<string, string> LangMap = new(StringComparer.OrdinalIgnoreCase)
    {
        [".cs"] = "csharp", [".csproj"] = "xml", [".sln"] = "text", [".json"] = "json",
        [".xml"] = "xml", [".config"] = "xml", [".xaml"] = "xml", [".ps1"] = "powershell",
        [".md"] = "markdown", [".yml"] = "yaml", [".yaml"] = "yaml", [".txt"] = "text",
        [".resx"] = "xml", [".props"] = "xml", [".targets"] = "xml", [".editorconfig"] = "ini",
        [".gitignore"] = "text",
    };

    // Avvisi euristici, non redazione automatica: falsi negativi darebbero un falso senso di sicurezza.
    public static readonly (string Label, Regex Pattern)[] SecretPatterns =
    [
        ("password/pwd", new(@"(?i)\b(password|pwd)\s*[:=]\s*['""]?[^\s'""]{3,}")),
        ("connection string", new(@"(?i)(Server|Data Source)\s*=.*(Password|Pwd)\s*=")),
        ("api key", new(@"(?i)\b(api[_-]?key|apikey|secret[_-]?key)\s*[:=]\s*['""]?[A-Za-z0-9_\-]{10,}")),
        ("bearer token", new(@"(?i)Bearer\s+[A-Za-z0-9\-_\.]{10,}")),
        ("private key block", new(@"-----BEGIN (RSA |EC )?PRIVATE KEY-----")),
        ("AWS key", new(@"AKIA[0-9A-Z]{16}")),
    ];

    // Pattern euristici di mojibake tipici di UTF-8 riletto come CP1252/CP850
    // (es. accentate italiane trasformate in "├ê", "novit├á"): solo diagnostica,
    // nessuna correzione automatica, un falso negativo darebbe un falso senso di sicurezza.
    public static readonly Regex MojibakePattern = new("[├┬ÃÂ]");

    // Diagnostica per T2.1 (Anomalia 3): rileva sequenze di controllo letterali
    // (i due caratteri backslash+lettera, non un CR/LF/TAB fisico) dentro code
    // span Markdown, es. testo di documentazione che descrive "rimuove `\r`,
    // sostituisce `\n` con `§`". Il contenuto non viene mai alterato: ne' lettura
    // ne' scrittura toccano queste sequenze (vedi commento su fullText piu' sotto),
    // questo e' solo un avviso in header per rendere visibile che nel file
    // sorgente sono presenti letterali di questo tipo. Limitato ai code span
    // (tra backtick) per non generare falsi positivi su path Windows tipo
    // "C:\temp" o "C:\note".
    public static readonly Regex LiteralControlPattern = new(@"`[^`\r\n]*\\[rnt][^`\r\n]*`");

    // Diagnostica per T2.3 (Anomalia 1): conta i marcatori di fence (righe che
    // iniziano con ``` , con o senza indicazione di linguaggio) nei file .md
    // inclusi nel bundle. Un conteggio dispari indica un fence aperto e mai
    // richiuso nel sorgente stesso - diagnostica solo su file .md, nessuna
    // correzione o normalizzazione applicata al contenuto.
    public static readonly Regex MdFencePattern = new(@"^```", RegexOptions.Multiline);
}
