// dotnet run -- <rootPath> <inputFile.md> [outputFile.md] [--stdout]
//
// inputFile.md: elenco righe, una per entry:
//   src/MyLibrary/Class1.cs                     -> intero file
//   src/MyLibrary/Class1.cs:120-180             -> solo le righe 120-180
//   src/MyLibrary/Class1.cs:63-82,133-152       -> piu' estratti non contigui dallo stesso file
// Righe vuote, righe che iniziano con '#' e bullet ('-', '*') vengono ignorati/normalizzati.
//
// --stdout: scrive il bundle su stdout invece che su file (utile per pipe, es. | Set-Clipboard).
//           I messaggi di stato vanno su stderr per non sporcare l'output.
//
// smart-ass mode: se lanciato senza argomenti posizionali, seleziona il file
// context-request*.md piu' recente nella directory corrente e genera automaticamente
// context-out-<desc>.md, dove <desc> e' la parte del nome successiva a "context-request-".
//
// T3.2-prep: logica applicativa spostata in Cli/, Constants/, Models/, Services/
// (vedi Services/BundleGenerator.cs per l'orchestrazione); questo file resta
// l'unico con top-level statements, limitato a parsing CLI e I/O.
using ContextBundler.Cli;
using ContextBundler.Constants;
using ContextBundler.Services;

bool toStdout = args.Contains("--stdout");
var positional = args.Where(a => a != "--stdout").ToArray();

if (positional.Length == 0)
{
    var resolved = SmartAssFileResolver.TryResolve(Console.Error.WriteLine);
    if (resolved is null) return 1;
    positional = resolved;
}

if (positional.Length < 2)
{
    Console.Error.WriteLine("Uso: dotnet run -- <rootPath> <inputFile.md> [outputFile.md] [--stdout]");
    return 1;
}

var rootPath = Path.GetFullPath(positional[0]);
var inputFile = positional[1];
var outputFile = positional.Length > 2 ? positional[2] : Path.Combine(rootPath, "context_bundle.md");

void Log(string msg)
{
    // se il bundle esce su stdout, i messaggi di stato vanno su stderr per non sporcare la pipe
    if (toStdout) Console.Error.WriteLine(msg);
    else Console.WriteLine(msg);
}

if (!File.Exists(inputFile))
{
    Console.Error.WriteLine($"File di input non trovato: {inputFile}");
    return 1;
}

var entries = File.ReadAllLines(inputFile)
    .Select(l => l.Trim())
    .Where(l => l.Length > 0 && !l.StartsWith('#'))
    .Select(l => l.TrimStart('-', '*', ' ').Trim())
    .Where(l => l.Length > 0)
    .Distinct()
    .ToList();

var result = BundleGenerator.Generate(rootPath, Path.GetFileName(inputFile), entries, Log);

if (toStdout)
    Console.Out.Write(result.BundleText);
else
    File.WriteAllText(outputFile, result.BundleText, new System.Text.UTF8Encoding(false));

Log($"Bundle generato{(toStdout ? " (stdout)" : $": {outputFile}")} ({result.IncludedCount}/{result.TotalEntries} entry incluse, {result.TotalBytes / 1024.0:F1} KB)");

if (result.TotalBytes > BundleFormatConstants.SizeWarningBytes)
    Log($"Attenzione: bundle sopra {BundleFormatConstants.SizeWarningBytes / 1024} KB, valuta di ridurre la lista o usare estratti mirati.");

var w = result.Warnings;

if (w.Missing.Count > 0)
{
    Log("File non trovati (verifica i path relativi a rootPath):");
    foreach (var m in w.Missing) Log($"  - {m}");
}

if (w.SkippedBinary.Count > 0)
{
    Log("File binari esclusi automaticamente:");
    foreach (var b in w.SkippedBinary) Log($"  - {b}");
}

if (w.Secret.Count > 0)
{
    Log("Possibili dati sensibili nel bundle (verifica prima di incollarlo in chat):");
    foreach (var s in w.Secret) Log($"  - {s}");
}

if (w.Mojibake.Count > 0)
{
    Log("Possibili sequenze di mojibake rilevate (UTF-8 riletto con encoding errato), verifica manuale consigliata:");
    foreach (var m in w.Mojibake) Log($"  - {m}");
}

if (w.LiteralControl.Count > 0)
{
    Log("Sequenze di controllo letterali (\\r \\n \\t) rilevate in code span, contenuto non alterato:");
    foreach (var l in w.LiteralControl) Log($"  - {l}");
}

if (w.Json.Count > 0)
{
    Log("File .json con validazione JSON fallita (prima e/o dopo l'inclusione nel bundle):");
    foreach (var j in w.Json) Log($"  - {j}");
}

if (w.MdFence.Count > 0)
{
    Log("File .md con possibile fence Markdown non chiuso (numero dispari di marcatori):");
    foreach (var f in w.MdFence) Log($"  - {f}");
}

return 0;
