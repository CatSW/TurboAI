#!/usr/bin/env pwsh
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 2.0

param (
    [string]$Target
)

cls
$ErrorActionPreference = 'Stop'

try {
    $solutionRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path

    if (-not (Test-Path -LiteralPath (Join-Path $solutionRoot '.git'))) {
        throw "La directory individuata non sembra essere la root del repository Git: $solutionRoot"
    }

    # 1. Costruzione dinamica dei target disponibili
    $dynamicModes = [ordered]@{
        '1' = [PSCustomObject]@{
            Name      = 'Solution (Intera Repository)'
            TargetDir = $solutionRoot
            Type      = 'Standard'
        }
    }

    $idx = 2

    # Rilevamento strumenti TurboAi / Utility
    $turboAiDir = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
    if (Test-Path -LiteralPath $turboAiDir) {
        $dynamicModes["$idx"] = [PSCustomObject]@{
            Name      = 'TurboAi-Tools'
            TargetDir = $turboAiDir
            Type      = 'Tools'
        }
        $idx++
    }

    # Auto-discovery dinamica di tutti i progetti C# e solution nella repository
    $projectFiles = Get-ChildItem -LiteralPath $solutionRoot -Recurse -File -Include '*.csproj', '*.slnx' |
        Where-Object { $_.FullName -notmatch '\\(bin|obj|packages|node_modules|\.git|\.vs|artifacts|\.ai-context|\.turbo-ai)\\' }

    $discoveredDirs = $projectFiles | ForEach-Object { $_.Directory } | Select-Object -Unique

    foreach ($dir in $discoveredDirs) {
        $relPath = [System.IO.Path]::GetRelativePath($solutionRoot, $dir.FullName)
        if ($relPath -ne '.') {
            $dynamicModes["$idx"] = [PSCustomObject]@{
                Name      = $relPath
                TargetDir = $dir.FullName
                Type      = 'Project'
            }
            $idx++
        }
    }

    # 2. Selezione interattiva o risoluzione parametro
    $selectedOption = $null

    if ([string]::IsNullOrWhiteSpace($Target)) {
        Write-Host "===================================" -ForegroundColor Cyan
        Write-Host "  List Files - Selezione Modalita" -ForegroundColor Cyan
        Write-Host "===================================" -ForegroundColor Cyan
        
        foreach ($key in $dynamicModes.Keys) {
            Write-Host ("  {0}) {1}" -f $key, $dynamicModes[$key].Name)
        }
        Write-Host "===================================" -ForegroundColor Cyan
        Write-Host ""

        $choice = Read-Host ("Seleziona un'opzione [1-{0}]" -f $dynamicModes.Count)

        if (-not $dynamicModes.Contains($choice)) {
            throw "Opzione non valida: '$choice'."
        }
        $selectedOption = $dynamicModes[$choice]
    }
    else {
        # Ricerca per corrispondenza esatta o parziale tra i target rilevati
        $foundKey = $dynamicModes.Keys | Where-Object { 
            $dynamicModes[$_].Name -eq $Target -or $dynamicModes[$_].Name -like "*$Target*" 
        } | Select-Object -First 1

        if ($foundKey) {
            $selectedOption = $dynamicModes[$foundKey]
        }
        else {
            $resolvedPath = Join-Path $solutionRoot $Target
            if (Test-Path -LiteralPath $resolvedPath) {
                $selectedOption = [PSCustomObject]@{
                    Name      = $Target
                    TargetDir = (Resolve-Path $resolvedPath).Path
                    Type      = 'CustomPath'
                }
            }
            else {
                throw "Target '$Target' non riconosciuto e percorso non esistente."
            }
        }
    }

    # 3. Estrazione ed elaborazione file
    $downloadsFolder = (New-Object -ComObject Shell.Application).Namespace('shell:Downloads')
    if ($null -eq $downloadsFolder) {
        throw "Impossibile individuare la cartella Download dell'utente corrente."
    }
    $downloadsPath = $downloadsFolder.Self.Path
    $outputFile = Join-Path $downloadsPath 'ls.txt'
    $cultureInfo = [System.Globalization.CultureInfo]::GetCultureInfo('it-IT')

    $filesToInclude = @()

    if ($selectedOption.Type -eq 'Tools') {
        $cmdFiles = Get-ChildItem -LiteralPath $selectedOption.TargetDir -File -Filter "*.cmd"
        $artifactFiles = Get-ChildItem -LiteralPath $PSScriptRoot -File | 
            Where-Object { $_.Extension -match '^\.(py|ps1)$' }
        $filesToInclude = $cmdFiles + $artifactFiles
    }
    else {
        $allowedExtensions = @('.slnx', '.sln', '.csproj', '.csprj', '.json', '.xml', '.md', '.cs', '.py', '.ps1', '.cmd', '.yml', '.yaml')
        $excludeFolders = @('bin', 'obj', 'packages', 'TestResults', 'node_modules', 'artifacts', '.ai-context', '.turbo-ai', 'old.*')
        $pattern = ($excludeFolders | ForEach-Object { [regex]::Escape($_) }) -join '|'

        $filesToInclude = Get-ChildItem -LiteralPath $selectedOption.TargetDir -Recurse -File | Where-Object {
            $ext = $_.Extension.ToLower()
            $isAllowed = $allowedExtensions -contains $ext
            $isNotExcluded = $_.FullName -notmatch "\\($pattern)(\\|`$)"
            return $isAllowed -and $isNotExcluded
        }
    }

    # 4. Formattazione e scrittura output
    $lines = @("Solution root: $solutionRoot", "Target selezionato: $($selectedOption.Name)", "")

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
    Write-Host "Modalita: $($selectedOption.Name)" -ForegroundColor Cyan
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
