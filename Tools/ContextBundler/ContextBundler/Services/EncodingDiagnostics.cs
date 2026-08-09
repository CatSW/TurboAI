using ContextBundler.Constants;

namespace ContextBundler.Services;

internal static class EncodingDiagnostics
{
    /// <summary>Rileva ed elimina il BOM UTF-8 (EF BB BF) se presente, cosi' che non
    /// finisca nel bundle come carattere U+FEFF invisibile. Il BOM viene dichiarato
    /// in header ma mai ricreato in scrittura (sezione 2.3).</summary>
    public static (byte[] Content, bool HadBom) StripBom(byte[] bytes)
    {
        var hasBom = bytes.Length >= 3 && bytes[0] == 0xEF && bytes[1] == 0xBB && bytes[2] == 0xBF;
        return (hasBom ? bytes[3..] : bytes, hasBom);
    }

    /// <summary>Pattern euristici di mojibake tipici di UTF-8 riletto come CP1252/CP850
    /// (es. accentate italiane trasformate in "├ê", "novit├á"): solo diagnostica,
    /// nessuna correzione automatica.</summary>
    public static bool HasMojibake(string content) =>
        BundleFormatConstants.MojibakePattern.IsMatch(content);
}
