#!/usr/bin/env pwsh
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.2

param(
    [Parameter(Position = 0, Mandatory = $false)]
    [string]$FilePath,

    [Parameter(Position = 1, Mandatory = $false)]
    [int]$OffsetX = 0,

    [Parameter(Position = 2, Mandatory = $false)]
    [int]$OffsetY = 0
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

$hwnd = [Win]::GetForegroundWindow()
$rect = New-Object RECT

if ([Win]::GetWindowRect($hwnd, [ref]$rect)) {
    try {
        $cols = $host.UI.RawUI.WindowSize.Width
        $rows = $host.UI.RawUI.WindowSize.Height
    } catch {
        $cols = 110
        $rows = 28
    }

    if ($cols -le 0) { $cols = 110 }
    if ($rows -le 0) { $rows = 28 }

    $posX = [Math]::Max(0, $rect.Left + $OffsetX)
    $posY = [Math]::Max(0, $rect.Top + $OffsetY)

    if ([string]::IsNullOrWhiteSpace($FilePath)) {
        Write-Output 'rem Parametri di posizionamento e dimensione per Windows Terminal'
        Write-Output "set `"WT_POS=$posX,$posY`""
        Write-Output "set `"WT_SIZE=$cols,$rows`""
    } else {
        $resolvedPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($FilePath)

        $config = [ordered]@{
            "x-win-pos" = $posX
            "y-win-pos" = $posY
            "width"     = $cols
            "height"    = $rows
        }

        $json = $config | ConvertTo-Json
        
        # Scrive in UTF-8 senza BOM per evitare problemi di parsing in Python
        $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($resolvedPath, $json, $utf8NoBom)
    }
}
