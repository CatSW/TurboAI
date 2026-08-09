using ContextBundler.Constants;

namespace ContextBundler.Services;

internal static class LiteralControlSequenceScanner
{
    /// <summary>Rileva sequenze di controllo letterali (backslash+lettera, non un
    /// CR/LF/TAB fisico) dentro code span Markdown. Il contenuto non viene mai
    /// alterato, solo segnalato in header (Anomalia 3).</summary>
    public static bool HasLiteralControlSequences(string content) =>
        BundleFormatConstants.LiteralControlPattern.IsMatch(content);
}
