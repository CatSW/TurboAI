namespace ContextBundler.Models;

/// <summary>Intervallo di righe (1-based, inclusivo) richiesto per un estratto
/// parziale di un file, es. "path:120-180".</summary>
internal readonly record struct FileRange(int Start, int End);
