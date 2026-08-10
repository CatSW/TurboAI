#!/usr/bin/env pwsh
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.0
# Eseguire tramite il relativo launcher .cmd.
# Produce ls.txt nella cartella Download dell'utente corrente,
# con informazioni Git e con l'elenco ricorsivo dei file:
# path relativo + dimensione file (KB), escludendo cartelle di build/tooling.
# La dimensione serve a valutare a colpo d'occhio se un file
# e' abbastanza grande da giustificare un estratto mirato invece del bundle intero.
cls

$ErrorActionPreference = 'Stop'

try {
    $exclude = 'bin', 'obj', '\.git', '\.vs', 'packages', 'TestResults', 'node_modules', 'artifacts', '\.idea'
    $pattern = ($exclude -join '|')

    # Lo script si trova in:
    # <solution-root>\.catsw-utility\artefacts\list-files.ps1
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

    "Solution root: $solutionRoot" |
        Set-Content -Path $outputFile -Encoding UTF8

    " " |
        Add-Content -Path $outputFile -Encoding UTF8

    "git status --short" |
        Add-Content -Path $outputFile -Encoding UTF8

    $gitStatus = git -C $solutionRoot status --short 2>&1

    if ($LASTEXITCODE -ne 0) {
        throw "Errore durante l'esecuzione di 'git status --short':`n$($gitStatus -join [System.Environment]::NewLine)"
    }

    $gitStatus |
        Add-Content -Path $outputFile -Encoding UTF8

    " " |
        Add-Content -Path $outputFile -Encoding UTF8

    "git log -1 --oneline" |
        Add-Content -Path $outputFile -Encoding UTF8

    $gitLog = git -C $solutionRoot log -1 --oneline 2>&1

    if ($LASTEXITCODE -ne 0) {
        throw "Errore durante l'esecuzione di 'git log -1 --oneline':`n$($gitLog -join [System.Environment]::NewLine)"
    }

    $gitLog |
        Add-Content -Path $outputFile -Encoding UTF8

    " " |
        Add-Content -Path $outputFile -Encoding UTF8

    Get-ChildItem -LiteralPath $solutionRoot -Recurse -File |
        Where-Object {
            $_.FullName -notmatch "\\($pattern)\\"
        } |
        ForEach-Object {
            $relativePath = [System.IO.Path]::GetRelativePath(
                $solutionRoot,
                $_.FullName
            )

            $kb = [System.Math]::Round($_.Length / 1KB, 1)

            "{0} ({1} KB)" -f $relativePath, $kb
        } |
        Sort-Object |
        Add-Content -Path $outputFile -Encoding UTF8

    Write-Host ""
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
