using System.Reflection;
using System.Text;
using ContextBundler.Constants;
using ContextBundler.Models;

namespace ContextBundler.Services;

internal static class BundleHeaderBuilder
{
    public static string Build(string rootPath, string sourceListName, List<string> bomFiles, BundleWarnings warnings)
    {
        string ver = Assembly.GetExecutingAssembly().GetName().Version?.ToString() ?? "N/A";
        var header = new StringBuilder();
        header.AppendLine("# CONTEXT BUNDLE");
        header.AppendLine($"# BundleFormatVersion: {BundleFormatConstants.BundleFormatVersion}");
        header.AppendLine($"# ContextBundler V{ver} by IK0VCK @ CatSW");
        header.AppendLine($"# Repository root: {rootPath}");
        header.AppendLine($"# Generated: {DateTime.Now:yyyy-MM-dd HH:mm:ss}");
        header.AppendLine($"# Source list: {sourceListName}");
        header.AppendLine($"# MarkdownEscaping: {BundleFormatConstants.MarkdownEscaping}");
        header.AppendLine("# ContentEncoding: UTF-8");
        header.AppendLine($"# NewlineRepresentation: {BundleFormatConstants.NewlineRepresentation}");
        header.AppendLine(bomFiles.Count == 0
            ? "# SourceBOM: nessun file sorgente aveva BOM"
            : $"# SourceBOM: BOM rilevato e rimosso in {bomFiles.Count} file: {string.Join(", ", bomFiles.Select(f => f.Replace('\\', '/')))}");
        header.AppendLine(warnings.LiteralControl.Count == 0
            ? "# LiteralControlSequences: nessuna sequenza di controllo letterale (\\r \\n \\t) rilevata in code span"
            : $"# LiteralControlSequences: rilevate in {warnings.LiteralControl.Count} file (contenuto non alterato, verifica manuale consigliata): {string.Join(", ", warnings.LiteralControl)}");
        GitInfoProvider.AppendGitBlock(header, rootPath, "log -1 --oneline");
        GitInfoProvider.AppendGitBlock(header, rootPath, "status --short");
        header.AppendLine();

        return header.ToString();
    }
}
