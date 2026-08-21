using System.Text.Json.Nodes;

namespace ContextBundler.Services;

/// <summary>Carica (e crea se assente) appsettings.json accanto all'eseguibile.
/// Espone Enabled + DirectiveLines per il blocco &lt;session_directive&gt; (T8.1_Estemporaneo).
/// Se il file manca viene creato con i default operativi. Se manca/malformato/vuoto
/// il nodo DirectiveLines, si usa il testo di fallback cablato in SessionDirectiveBuilder
/// (rete di sicurezza, non il default operativo). JsonNode per compatibilità PublishAot.</summary>
internal static class SessionDirectiveConfig
{
    private const string DefaultContent =
        "{\n" +
        "  \"SessionDirective\": {\n" +
        "    \"Enabled\": true,\n" +
        "    \"DirectiveLines\": [\n" +
        "      \"Read this bundle's governance, the active plan's <next_task> block, and the attached skill in full before asking for anything else.\",\n" +
        "      \"If the state is clear (no material contradiction), proceed directly per the skill contract - do not wait for a \\\"go\\\" or ask for confirmation.\",\n" +
        "      \"If something is missing or genuinely ambiguous, name the exact missing value or decision and request only that.\"\n" +
        "    ]\n" +
        "  }\n" +
        "}\n";

    /// <summary>Restituisce (Enabled, DirectiveLines). DirectiveLines può essere null
    /// → il chiamante userà il fallback cablato.</summary>
    public static (bool Enabled, string[]? Lines) Load(Action<string> log)
    {
        var path = Path.Combine(AppContext.BaseDirectory, "appsettings.json");

        if (!File.Exists(path))
        {
            try
            {
                File.WriteAllText(path, DefaultContent, new System.Text.UTF8Encoding(false));
                log($"appsettings.json non trovato, creato con default (Enabled=true + DirectiveLines): {path}");
            }
            catch (Exception ex)
            {
                log($"Impossibile creare appsettings.json ({ex.Message}), uso default Enabled=true + fallback testo cablato.");
                return (true, null);
            }
            // appena creato: leggiamo i default appena scritti
            return Parse(path, log);
        }

        return Parse(path, log);
    }

    private static (bool Enabled, string[]? Lines) Parse(string path, Action<string> log)
    {
        try
        {
            var node = JsonNode.Parse(File.ReadAllText(path));
            var section = node?["SessionDirective"];
            var enabled = section?["Enabled"]?.GetValue<bool>() ?? true;

            string[]? lines = null;
            var linesNode = section?["DirectiveLines"] as JsonArray;
            if (linesNode is { Count: > 0 })
            {
                var list = new List<string>(linesNode.Count);
                foreach (var item in linesNode)
                {
                    var s = item?.GetValue<string>();
                    if (!string.IsNullOrWhiteSpace(s))
                        list.Add(s);
                }
                if (list.Count > 0)
                    lines = list.ToArray();
            }

            if (lines is null)
                log("appsettings.json: DirectiveLines assente o vuoto, uso fallback testo cablato.");

            return (enabled, lines);
        }
        catch (Exception ex)
        {
            log($"appsettings.json illeggibile ({ex.Message}), uso default Enabled=true + fallback testo cablato.");
            return (true, null);
        }
    }
}
