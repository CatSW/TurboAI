namespace ContextBundler.Models;

/// <summary>Esito dell'elaborazione di una singola entry del bundle: il blocco
/// &lt;&lt;&lt;FILE...&gt;&gt;&gt; gia' pronto da accodare, piu' i dati necessari
/// all'orchestratore per il totale byte e per la lista dei file con BOM rimosso.</summary>
internal sealed class ProcessedFile
{
    public required string Rel { get; init; }
    public required string FileBlockText { get; init; }
    public required long ContentBytesLength { get; init; }
    public required bool HadBom { get; init; }
}
