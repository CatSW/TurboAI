#!/usr/bin/env pwsh
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.0
# Crea context-request-fagotto-pronto.md con tutti i file sotto BundleThisPlease,
# invoca ContextBundler.cmd, sposta context-out-fagotto-pronto.md nella root
# e rimuove il request. Fail-fast. Nessun Download / ToLlm.txt.
# Portabile: ricava root da $PSScriptRoot (artefacts -> .catsw-utility -> repo).
# Non modifica/cancella il contenuto di BundleThisPlease.

$ErrorActionPreference = 'Stop'

function Write-Fail([string]$Message) {
    Write-Host "[ERRORE] $Message" -ForegroundColor Red
    exit 1
}

try {
    $ArtefactsDir   = $PSScriptRoot
    $UtilityRoot    = Split-Path -Parent $ArtefactsDir
    $RepositoryRoot = Split-Path -Parent $UtilityRoot

    if (-not (Test-Path -LiteralPath $UtilityRoot -PathType Container)) {
        Write-Fail "UtilityRoot non trovato: $UtilityRoot"
    }
    if (-not (Test-Path -LiteralPath $RepositoryRoot -PathType Container)) {
        Write-Fail "RepositoryRoot non trovato: $RepositoryRoot"
    }

    $SourceFolder = Join-Path $RepositoryRoot 'BundleThisPlease'
    $RequestName  = 'context-request-fagotto-pronto.md'
    $OutName      = 'context-out-fagotto-pronto.md'
    $RequestPath  = Join-Path $UtilityRoot $RequestName
    $OutPath      = Join-Path $UtilityRoot $OutName
    $OutDest      = Join-Path $RepositoryRoot $OutName
    $BundlerCmd   = Join-Path $UtilityRoot 'ContextBundler.cmd'

    if (-not (Test-Path -LiteralPath $SourceFolder -PathType Container)) {
        Write-Fail "Cartella sorgente assente: $SourceFolder"
    }
    if (-not (Test-Path -LiteralPath $BundlerCmd -PathType Leaf)) {
        Write-Fail "ContextBundler.cmd non trovato: $BundlerCmd"
    }

    $files = @(Get-ChildItem -LiteralPath $SourceFolder -Recurse -File -ErrorAction Stop)
    if ($files.Count -eq 0) {
        Write-Fail "Nessun file trovato sotto: $SourceFolder"
    }

    $sb = New-Object System.Text.StringBuilder
    [void]$sb.Append("# Files to bundle`n")

    foreach ($f in $files) {
        $rel = $f.FullName.Substring($RepositoryRoot.Length).TrimStart('\', '/')
        $rel = $rel -replace '\\', '/'
        [void]$sb.Append($rel)
        [void]$sb.Append("`n")
    }

    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($RequestPath, $sb.ToString(), $utf8NoBom)

    if (-not (Test-Path -LiteralPath $RequestPath -PathType Leaf)) {
        Write-Fail "Impossibile creare il manifest: $RequestPath"
    }

    Write-Host "Manifest creato: $RequestPath ($($files.Count) file)"
    Write-Host "Invoco ContextBundler.cmd ..."

    $p = Start-Process -FilePath $BundlerCmd -WorkingDirectory $UtilityRoot -Wait -PassThru -NoNewWindow
    if ($null -eq $p -or $p.ExitCode -ne 0) {
        $code = if ($null -eq $p) { 'null' } else { $p.ExitCode }
        Write-Fail "ContextBundler.cmd fallito (exit $code)"
    }

    if (-not (Test-Path -LiteralPath $OutPath -PathType Leaf)) {
        Write-Fail "Output atteso non generato: $OutPath"
    }

    if (Test-Path -LiteralPath $OutDest) {
        Remove-Item -LiteralPath $OutDest -Force
    }
    Move-Item -LiteralPath $OutPath -Destination $OutDest -Force
    Write-Host "Output spostato in: $OutDest"

    if (Test-Path -LiteralPath $RequestPath) {
        Remove-Item -LiteralPath $RequestPath -Force
        Write-Host "Request rimosso: $RequestPath"
    }

    Write-Host "OK - FolderBundler completato."
    exit 0
}
catch {
    Write-Fail $_.Exception.Message
}
