using ContextBundler.Constants;

namespace ContextBundler.Services;

internal static class FileTypeClassifier
{
    public static bool IsLikelyBinary(byte[] bytes)
    {
        var checkLength = Math.Min(bytes.Length, 8000);
        for (int i = 0; i < checkLength; i++)
            if (bytes[i] == 0) return true;
        return false;
    }

    public static string GetLanguage(string ext) =>
        BundleFormatConstants.LangMap.TryGetValue(ext, out var mapped)
            ? mapped
            : ext.Length > 0 ? ext.TrimStart('.') : "text";

    public static bool IsJsonFile(string ext) =>
        string.Equals(ext, ".json", StringComparison.OrdinalIgnoreCase);

    public static bool IsMarkdownFile(string ext) =>
        string.Equals(ext, ".md", StringComparison.OrdinalIgnoreCase);
}
