namespace ContextBundler.Cli;

/// <summary>"smart-ass mode": se lanciato senza argomenti posizionali,
/// seleziona il file context-request*.md piu' recente nella directory
/// corrente (o in Downloads, spostandolo) e genera automaticamente i tre
/// argomenti posizionali equivalenti a un avvio esplicito.</summary>
internal static class SmartAssFileResolver
{
    /// <summary>Ritorna i tre argomenti posizionali risolti, oppure null se
    /// nessun candidato e' stato trovato (in tal caso l'errore e' gia' stato
    /// scritto tramite logError).</summary>
    public static string[]? TryResolve(Action<string> logError)
    {
        //logError("smart-ass mode");
        var cwd = Directory.GetCurrentDirectory();
        var candidate = Directory.GetFiles(cwd, "context-request*.md")
            .OrderByDescending(File.GetLastWriteTimeUtc)
            .FirstOrDefault();

        if (candidate is null)
        {
            var downloadsPath = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),
                "Downloads");

            if (Directory.Exists(downloadsPath))
            {
                var downloadCandidate = Directory.GetFiles(downloadsPath, "context-request*.md")
                    .OrderByDescending(File.GetLastWriteTimeUtc)
                    .FirstOrDefault();

                if (downloadCandidate is not null)
                {
                    var destinationFile = Path.Combine(
                        cwd,
                        Path.GetFileName(downloadCandidate));

                    logError(
                        $"Nessun file trovato in {cwd}. Recupero '{Path.GetFileName(downloadCandidate)}' da Downloads.");

                    if (File.Exists(destinationFile))
                        File.Delete(destinationFile);

                    File.Move(downloadCandidate, destinationFile);

                    candidate = destinationFile;

                    logError($"File spostato in {cwd} e selezionato per l'elaborazione.");
                }
            }
        }

        if (candidate is null)
        {
            logError(
                $"Nessun file 'context-request*.md' trovato né in {cwd} né nella cartella Downloads.");
            return null;
        }

        logError($"File selezionato: {Path.GetFileName(candidate)} (modificato {File.GetLastWriteTime(candidate):yyyy-MM-dd HH:mm:ss})");
        var inputNameWithoutExtension = Path.GetFileNameWithoutExtension(candidate);
        const string requestPrefix = "context-request-";
        var description = inputNameWithoutExtension.StartsWith(requestPrefix, StringComparison.OrdinalIgnoreCase)
            ? inputNameWithoutExtension[requestPrefix.Length..]
            : inputNameWithoutExtension;
        var automaticOutputFile = Path.Combine(cwd, $"context-out-{description}.md");
        return new[] { "..", candidate, automaticOutputFile };
    }
}
