namespace ContextBundler.Services;

/// <summary>Costruisce il blocco &lt;session_directive&gt; da iniettare in coda ai bundle
/// generati da una richiesta start-session (T8.1_Estemporaneo).
/// Testo preso da appsettings.json (DirectiveLines); se assente/malformato/vuoto
/// usa il fallback cablato qui sotto (rete di sicurezza).</summary>
internal static class SessionDirectiveBuilder
{
    /// <summary>Fallback cablato: usato solo se appsettings manca, è malformato
    /// o DirectiveLines è assente/vuoto.</summary>
    private static readonly string[] FallbackDirectiveLines =
    [
        "Read this bundle's governance, the active plan's <next_task> block, and the attached skill in full before asking for anything else.",
        "If the state is clear (no material contradiction), proceed directly per the skill contract - do not wait for a \"go\" or ask for confirmation.",
        "If something is missing or genuinely ambiguous, name the exact missing value or decision and request only that."
    ];

    /// <summary>True se il nome del file di request è una richiesta di inizio sessione
    /// (convenzione: "context-request-start-session-*.md"), il solo caso in cui il blocco
    /// va emesso.</summary>
    internal static bool IsStartSession(string sourceListName) =>
        sourceListName.StartsWith("context-request-start-session-", StringComparison.OrdinalIgnoreCase);

    /// <summary>Restituisce il blocco (senza separatori esterni) se abilitato e la request
    /// è start-session, altrimenti stringa vuota. Usa le linee configurate o il fallback.</summary>
    public static string Build(string sourceListName, bool enabled, string[]? lines)
    {
        if (!enabled || !IsStartSession(sourceListName))
            return "";

        var effective = (lines is { Length: > 0 }) ? lines : FallbackDirectiveLines;
        return "<session_directive>\n" + string.Join("\n", effective) + "\n</session_directive>";
    }
}
