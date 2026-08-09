using System.Diagnostics;
using System.Text;

namespace ContextBundler.Services;

internal static class GitInfoProvider
{
    public static void AppendGitBlock(StringBuilder sb, string rootPath, string gitArgs)
    {
        var output = RunGit(rootPath, gitArgs);
        if (output is null) return; // non e' un repo git o comando fallito: nessun blocco, nessun errore

        sb.AppendLine($"# git {gitArgs}");
        if (output.Length == 0)
            sb.AppendLine("# (nessun output)");
        else
            foreach (var line in output.Split('\n'))
                sb.AppendLine($"# {line.TrimEnd('\r')}");
    }

    public static string? RunGit(string rootPath, string gitArgs)
    {
        try
        {
            var psi = new ProcessStartInfo("git", gitArgs)
            {
                WorkingDirectory = rootPath,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
            };
            using var p = Process.Start(psi)!;
            var output = p.StandardOutput.ReadToEnd().TrimEnd();
            p.WaitForExit();
            return p.ExitCode == 0 ? output : null;
        }
        catch
        {
            return null;
        }
    }
}
