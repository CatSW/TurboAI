#!/usr/bin/env pwsh
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.3

param (
    [Parameter(Mandatory = $true)]
    [ValidateSet('TurboAi-Tools', 'ContextBundler')]
    [string]$Mode
)

cls
$ErrorActionPreference = 'Stop'

try {
    $solutionRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path

    if (-not (Test-Path -LiteralPath (Join-Path $solutionRoot '.git'))) {
        throw "La directory individuata non sembra essere la root del repository Git: $solutionRoot"
    }

    $downloadsFolder = (New-Object -ComObject Shell.Application).Namespace('shell:Downloads')
    if ($null -eq $downloadsFolder) {
        throw "Impossibile individuare la cartella Download dell'utente corrente."
    }

    $downloadsPath = $downloadsFolder.Self.Path
    $outputFile = Join-Path $downloadsPath 'ls.txt'

    $cultureInfo = [System.Globalization.CultureInfo]::GetCultureInfo('it-IT')
    $filesToInclude = @()

    if ($Mode -eq 'TurboAi-Tools') {
        $utilityFolder = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
        
        # File .cmd nel folder principale (.catsw-utility)
        $cmdFiles = Get-ChildItem -LiteralPath $utilityFolder -File -Filter "*.cmd"
        
        # File .py e .ps1 nella sottocartella artifacts
        $artifactFiles = Get-ChildItem -LiteralPath $PSScriptRoot -File | 
            Where-Object { $_.Extension -match '^\.(py|ps1)$' }

        $filesToInclude = $cmdFiles + $artifactFiles
    }
    elseif ($Mode -eq 'ContextBundler') {
        $targetDir = Join-Path $solutionRoot 'Tools\ContextBundler'

        if (-not (Test-Path -LiteralPath $targetDir)) {
            throw "La directory $targetDir non esiste."
        }

        $allowedExtensions = @('.slnx', '.csproj', '.csprj', '.json', '.xml', '.md', '.cs')
        $excludeFolders = @('bin', 'obj', 'packages', 'TestResults', 'node_modules', 'artifacts', '.catsw-utility', '.ai-context', '.turbo-ai')

        $pattern = ($excludeFolders | ForEach-Object { [regex]::Escape($_) }) -join '|'

        $filesToInclude = Get-ChildItem -LiteralPath $targetDir -Recurse -File | Where-Object {
            $ext = $_.Extension.ToLower()
            $isAllowed = $allowedExtensions -contains $ext
            $isNotExcluded = $_.FullName -notmatch "\\($pattern)(\\|$)"
            return $isAllowed -and $isNotExcluded
        }
    }

    $lines = @("Solution root: $solutionRoot", "")

    # Ordinamento per LastWriteTime decrescente
    $fileLines = $filesToInclude | Sort-Object LastWriteTime -Descending | ForEach-Object {
        $relativePath = [System.IO.Path]::GetRelativePath($solutionRoot, $_.FullName)
        $kb = [System.Math]::Round($_.Length / 1KB, 1)
        $kbFormatted = $kb.ToString("0.0", $cultureInfo)
        $dateFormatted = $_.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
        
        "{0}  {1} ({2} KB)" -f $dateFormatted, $relativePath, $kbFormatted
    }

    $lines += $fileLines
    $lines | Set-Content -Path $outputFile -Encoding UTF8

    Write-Host ""
    Write-Host "Modalita: $Mode" -ForegroundColor Cyan
    Write-Host "Root della solution: $solutionRoot" -ForegroundColor DarkGray
    Write-Host "Elenco generato in: $outputFile" -ForegroundColor Green
}
catch {
    Write-Host ""
    Write-Host "ERRORE durante la generazione dell'elenco:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Read-Host "Premere INVIO per chiudere"

    exit 1
}