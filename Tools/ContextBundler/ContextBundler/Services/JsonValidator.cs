using System.Text.Json;

namespace ContextBundler.Services;

internal static class JsonValidator
{
    /// <summary>Parse "as-is", nessuna normalizzazione o correzione (T2.2). Un
    /// JsonDocument valido garantisce che il testo sia JSON well-formed.</summary>
    public static bool TryParse(string text, out string? error)
    {
        try
        {
            using var _ = JsonDocument.Parse(text);
            error = null;
            return true;
        }
        catch (JsonException ex)
        {
            error = ex.Message.Replace("\r", " ").Replace("\n", " ");
            return false;
        }
    }
}
