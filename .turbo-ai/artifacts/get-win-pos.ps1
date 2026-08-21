#!/usr/bin/env pwsh
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.1

param(
    [Parameter(Position = 0, Mandatory = $false)]
    [string]$FilePath
)

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

public class Win {
    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();

    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
}

public struct RECT {
    public int Left;
    public int Top;
    public int Right;
    public int Bottom;
}
'@

if ([string]::IsNullOrWhiteSpace($FilePath)) {
    $hwnd = [Win]::GetForegroundWindow()
    $rect = New-Object RECT

    if ([Win]::GetWindowRect($hwnd, [ref]$rect)) {
        $cols = $host.UI.RawUI.WindowSize.Width
        $rows = $host.UI.RawUI.WindowSize.Height

        Write-Output 'rem Parametri di posizionamento e dimensione per Windows Terminal'
        Write-Output "set `"WT_POS=$($rect.Left),$($rect.Top)`""
        Write-Output "set `"WT_SIZE=$cols,$rows`""
    }
} else {
    $name = [System.IO.Path]::GetFileNameWithoutExtension($FilePath)
    Read-Host "${name}: posiziona e ridimensiona nella posizione desiderata e premi INVIO"

    $hwnd = [Win]::GetForegroundWindow()
    $rect = New-Object RECT

    if ([Win]::GetWindowRect($hwnd, [ref]$rect)) {
        $cols = $host.UI.RawUI.WindowSize.Width
        $rows = $host.UI.RawUI.WindowSize.Height

        $resolvedPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($FilePath)

        $config = [ordered]@{
            "x-win-pos" = $rect.Left
            "y-win-pos" = $rect.Top
            "width"     = $cols
            "height"    = $rows
        }

        $json = $config | ConvertTo-Json
        
        # Scrive in UTF-8 senza BOM per evitare problemi di parsing in Python
        $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($resolvedPath, $json, $utf8NoBom)
    }
}