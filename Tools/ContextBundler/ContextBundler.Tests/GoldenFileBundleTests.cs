using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using ContextBundler.Models;
using ContextBundler.Services;
using Xunit;

namespace ContextBundler.Tests;

/// <summary>T3.2: genera il bundle su un set golden noto (Markdown con
/// fence/tabelle/link, JSON valido/non valido, C#, PowerShell, testo italiano
/// accentato, file con BOM) e verifica automaticamente hash per file, assenza
/// di escaping, JSON valido, encoding corretto, header presente.
///
/// Gli hash non sono hardcodati: vengono ricalcolati sul contenuto estratto
/// dal bundle e confrontati con l'attributo sha256 dichiarato nel blocco
/// &lt;&lt;&lt;FILE...&gt;&gt;&gt; — verifica equivalente ma non fragile a
/// piccole modifiche dei file fixture.</summary>
public class GoldenFileBundleTests
{
    private static readonly string GoldenRoot = Path.Combine(AppContext.BaseDirectory, "Golden");

    private static readonly string[] ExpectedEntries =
    [
        "Sample.md",
        "sample.json",
        "broken.json",
        "Sample.cs",
        "script.ps1",
        "testo-italiano.txt",
        "con-bom.txt",
        "control-sequence.md",
        "unclosed-fence.md",
        "Sample.xml",
    ];

    // <<<FILE path="..." bytes="123" sha256="...64 hex..." [attributi extra]>>>
    // seguito da newline, contenuto, newline, <<<END FILE>>>
    private static readonly Regex FileBlockPattern = new(
        """^<<<FILE path=\"(?<path>[^\"]+)\" bytes=\"(?<bytes>\d+)\" sha256=\"(?<sha>[0-9a-f]{64})\"(?<attrs>[^>]*)>>>\r?\n(?<content>.*?)\r?\n<<<END FILE>>>""",
        RegexOptions.Multiline | RegexOptions.Singleline);

    private sealed record ParsedBlock(string Content, string DeclaredSha, long DeclaredBytes);

    private static (BundleResult Result, Dictionary<string, ParsedBlock> Blocks) GenerateGolden()
    {
        var result = BundleGenerator.Generate(GoldenRoot, "golden-entries.md", [.. ExpectedEntries], _ => { });

        var blocks = new Dictionary<string, ParsedBlock>();
        foreach (Match m in FileBlockPattern.Matches(result.BundleText))
        {
            blocks[m.Groups["path"].Value] = new ParsedBlock(
                m.Groups["content"].Value,
                m.Groups["sha"].Value,
                long.Parse(m.Groups["bytes"].Value));
        }

        return (result, blocks);
    }

    [Fact]
    public void TuttiIFileGoldenSonoInclusiSenzaAvvisiDiMissingOBinario()
    {
        var (result, blocks) = GenerateGolden();

        Assert.Equal(ExpectedEntries.Length, result.IncludedCount);
        Assert.Empty(result.Warnings.Missing);
        Assert.Empty(result.Warnings.SkippedBinary);

        foreach (var entry in ExpectedEntries)
            Assert.True(blocks.ContainsKey(entry), $"Blocco mancante per {entry}");
    }

    [Fact]
    public void HashELunghezzaDichiaratiCorrispondonoAlContenutoEffettivo()
    {
        var (_, blocks) = GenerateGolden();

        foreach (var (path, block) in blocks)
        {
            var contentBytes = Encoding.UTF8.GetBytes(block.Content);
            var actualSha = Convert.ToHexString(SHA256.HashData(contentBytes)).ToLowerInvariant();

            Assert.True(block.DeclaredBytes == contentBytes.Length, $"{path}: bytes dichiarati {block.DeclaredBytes} != effettivi {contentBytes.Length}");
            Assert.True(block.DeclaredSha == actualSha, $"{path}: sha256 dichiarato {block.DeclaredSha} != ricalcolato {actualSha}");
        }
    }

    [Fact]
    public void NessunEscapingMarkdownDichiaratoInHeader()
    {
        var (result, _) = GenerateGolden();
        Assert.Contains("# MarkdownEscaping: none", result.BundleText);
    }

    [Fact]
    public void JsonValidoNonGeneraAvvisi()
    {
        var (result, _) = GenerateGolden();
        Assert.DoesNotContain(result.Warnings.Json, w => w.StartsWith("sample.json"));
    }

    [Fact]
    public void JsonNonValidoGeneraAvviso()
    {
        var (result, _) = GenerateGolden();
        Assert.Contains(result.Warnings.Json, w => w.StartsWith("broken.json"));
    }

    [Fact]
    public void EncodingUtf8PreservaAccentateItaliane()
    {
        var (result, blocks) = GenerateGolden();

        // Diagnostic: if the block is missing, include warnings and bundle text
        // in the test output to aid debugging of missing fixtures.
        if (!blocks.ContainsKey("testo-italiano.txt"))
        {
            // Fail with helpful context
            var warnings = new StringBuilder();
            warnings.AppendLine("Missing block 'testo-italiano.txt'. Diagnostics:");
            warnings.AppendLine("Warnings.Missing:");
            foreach (var w in result.Warnings.Missing)
                warnings.AppendLine(w);
            warnings.AppendLine("Warnings.SkippedBinary:");
            foreach (var w in result.Warnings.SkippedBinary)
                warnings.AppendLine(w);
            warnings.AppendLine("BundleText (truncated to 2000 chars):");
            warnings.AppendLine(result.BundleText.Length <= 2000 ? result.BundleText : result.BundleText.Substring(0, 2000));
            Assert.True(false, warnings.ToString());
        }

        var content = blocks["testo-italiano.txt"].Content;

        foreach (var accentata in new[] { "è", "à", "ò", "ù", "ì", "É", "È" })
            Assert.Contains(accentata, content);
    }

    [Fact]
    public void BomRilevatoESegnalatoInHeaderMaAssenteDalContenuto()
    {
        var (result, blocks) = GenerateGolden();

        var sourceBomLine = result.BundleText
            .Split('\n')
            .First(l => l.StartsWith("# SourceBOM"));
        Assert.Contains("con-bom.txt", sourceBomLine);

        Assert.DoesNotContain('\uFEFF', blocks["con-bom.txt"].Content);
    }

    [Fact]
    public void SequenzeDiControlloLetteraliRilevateInCodeSpan()
    {
        var (result, _) = GenerateGolden();
        Assert.Contains(result.Warnings.LiteralControl, w => w.StartsWith("control-sequence.md"));
    }

    [Fact]
    public void FenceMarkdownNonChiusoGeneraAvviso()
    {
        var (result, _) = GenerateGolden();
        Assert.Contains(result.Warnings.MdFence, w => w.StartsWith("unclosed-fence.md"));
    }

    [Fact]
    public void FenceMarkdownChiusoNonGeneraAvviso()
    {
        var (result, _) = GenerateGolden();
        Assert.DoesNotContain(result.Warnings.MdFence, w => w.StartsWith("Sample.md"));
    }

    [Fact]
    public void HeaderContieneTuttiICampiDichiarativiAttesi()
    {
        var (result, _) = GenerateGolden();
        var header = result.BundleText;

        Assert.Contains("# CONTEXT BUNDLE", header);
        Assert.Contains("# BundleFormatVersion:", header);
        Assert.Contains("# ContextBundler V", header);
        Assert.Contains("# Repository root:", header);
        Assert.Contains("# Generated:", header);
        Assert.Contains("# Source list: golden-entries.md", header);
        Assert.Contains("# MarkdownEscaping:", header);
        Assert.Contains("# ContentEncoding: UTF-8", header);
        Assert.Contains("# NewlineRepresentation:", header);
        Assert.Contains("# SourceBOM:", header);
        Assert.Contains("# LiteralControlSequences:", header);
    }

    [Fact]
    public void XmlConCdataContenenteChiusuraSimilAlDelimitatoreNonVieneAlterato()
    {
        var (_, blocks) = GenerateGolden();
        Assert.Contains(
            "<![CDATA[Testo con <tag> non interpretati e ]]> incluso qui.]]>",
            blocks["Sample.xml"].Content);
    }
}
