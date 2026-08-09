using ContextBundler.Constants;

namespace ContextBundler.Services;

internal static class MarkdownFenceScanner
{
    /// <summary>Conta i marcatori di fence (righe che iniziano con ```) in un file
    /// .md. Un conteggio dispari indica un fence aperto senza chiusura nel sorgente
    /// stesso (Anomalia 1) - nessuna correzione applicata.</summary>
    public static int CountFenceMarkers(string content) =>
        BundleFormatConstants.MdFencePattern.Matches(content).Count;
}
