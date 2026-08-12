namespace ContextBundler.Models;

internal sealed class BundleResult
{
    public required string BundleText { get; init; }
    public required int IncludedCount { get; init; }
    public required int TotalEntries { get; init; }
    public required long TotalBytes { get; init; }
    public required BundleWarnings Warnings { get; init; }
    /// <summary>T2.1: true se e' stato richiesto output in base64 (conversione reale in T2.2).</summary>
    public required bool ToBase64 { get; init; }
}
