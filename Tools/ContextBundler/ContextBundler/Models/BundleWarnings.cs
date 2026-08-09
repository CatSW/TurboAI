namespace ContextBundler.Models;

internal sealed class BundleWarnings
{
    public List<string> Missing { get; } = [];
    public List<string> SkippedBinary { get; } = [];
    public List<string> Secret { get; } = [];
    public List<string> Mojibake { get; } = [];
    public List<string> LiteralControl { get; } = [];
    public List<string> Json { get; } = [];
    public List<string> MdFence { get; } = [];
}
