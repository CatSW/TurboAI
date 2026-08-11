#!/usr/bin/env pwsh
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.0
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
    $width  = $rect.Right - $rect.Left
    $height = $rect.Bottom - $rect.Top

    Write-Output 'rem Parametri di posizionamento e dimensione per Windows Terminal'
    Write-Output "set `"WT_POS=$($rect.Left),$($rect.Top)`""
    Write-Output "set `"WT_SIZE=$width,$height`""
}
