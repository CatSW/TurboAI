using ContextBundler.Constants;
using ContextBundler.Models;

namespace ContextBundler.Services;

internal static class SecretScanner
{
    /// <summary>Aggiunge a warnings.Secret un avviso per ogni pattern di possibile
    /// dato sensibile trovato nel contenuto. Avvisi euristici, non redazione
    /// automatica: falsi negativi darebbero un falso senso di sicurezza.</summary>
    public static void Scan(string label, string content, BundleWarnings warnings)
    {
        foreach (var (secLabel, pattern) in BundleFormatConstants.SecretPatterns)
            if (pattern.IsMatch(content))
                warnings.Secret.Add($"{label}: possibile {secLabel}");
    }
}
