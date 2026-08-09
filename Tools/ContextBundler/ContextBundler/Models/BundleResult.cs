namespace ContextBundler.Models;

internal sealed class BundleResult
{
    public required string BundleText { get; init; }
    public required int IncludedCount { get; init; }
    public required int TotalEntries { get; init; }
    public required long TotalBytes { get; init; }
    public required BundleWarnings Warnings { get; init; }
}
