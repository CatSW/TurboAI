#!/usr/bin/env pwsh
# Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
# Version 1.0
# FromLlm-Unbundler.ps1
# Estrae i file da un .\context-out-*.md (o context-request-*.md) prodotto da ContextBundler
# e li ricrea sotto .\output mantenendo la struttura relativa alla root del repository.
#
# Uso (dalla cartella che contiene il context-out):
#   .\Unbundler.ps1
#   .\Unbundler.ps1 -ContextFile "C:\path\context-out-test-cb.md"
#   .\Unbundler.ps1 -OutputDir "C:\temp\extracted"
#
# Fix T1: rimozione robusta del fence di chiusura ``` anche quando seguito da righe vuote.

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string] $ContextFile,

    [Parameter(Mandatory = $false)]
    [string] $OutputDir
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Resolve-ContextFile {
    param([string] $ExplicitPath)

    if (-not [string]::IsNullOrWhiteSpace($ExplicitPath)) {
        if (-not (Test-Path -LiteralPath $ExplicitPath -PathType Leaf)) {
            throw "File di contesto non trovato: $ExplicitPath"
        }
        return (Resolve-Path -LiteralPath $ExplicitPath).Path
    }

    $searchRoot = if (-not [string]::IsNullOrWhiteSpace($PSScriptRoot)) {
        (Get-Item -LiteralPath $PSScriptRoot).Parent.Parent.FullName
    } else {
        (Get-Location).Path
    }
    
    $candidates = @(Get-ChildItem -LiteralPath $searchRoot -Filter 'context-out-*.md' -File -ErrorAction SilentlyContinue)

    if ($candidates.Count -eq 0) {
        throw "Nessun file context-out-*.md trovato in: $searchRoot"
    }
    if ($candidates.Count -gt 1) {
        $names = ($candidates | Select-Object -ExpandProperty Name) -join ', '
        throw "Trovati piu' file di contesto ($names). Specifica -ContextFile oppure lascia un solo file nella cartella."
    }

    return $candidates[0].FullName
}

function Save-ExtractedFile {
    param(
        [string] $RelativePath,
        [System.Collections.Generic.List[string]] $Lines,
        [string] $BaseOutputDir
    )

    if ([string]::IsNullOrWhiteSpace($RelativePath)) {
        return $false
    }

    # Normalizza separatori e rifiuta path traversal
    $safeRel = $RelativePath.Trim() -replace '\\', '/'
    if ($safeRel.StartsWith('/') -or $safeRel -match '(^|/)\.\.(/|$)') {
        Write-Warning "Path non sicuro ignorato: $RelativePath"
        return $false
    }

    # Rimuove in coda qualsiasi combinazione di:
    # - righe vuote / solo whitespace
    # - fence di chiusura puri (``` con eventuali spazi)
    # L'ordine unico evita il bug in cui i blank dopo il fence impedivano la rimozione del fence.
    while ($Lines.Count -gt 0) {
        $last = $Lines[$Lines.Count - 1]
        if ([string]::IsNullOrWhiteSpace($last) -or $last -match '^\s*```[a-zA-Z0-9_+-]*\s*$') {
            $Lines.RemoveAt($Lines.Count - 1)
        }
        else {
            break
        }
    }

    $targetFile = Join-Path -Path $BaseOutputDir -ChildPath ($safeRel -replace '/', [IO.Path]::DirectorySeparatorChar)
    $targetDir = Split-Path -Path $targetFile -Parent

    if (-not (Test-Path -LiteralPath $targetDir)) {
        New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
    }

    # UTF-8 senza BOM; preserva i line ending usati da Get-Content via NewLine di piattaforma
    $content = if ($Lines.Count -eq 0) { '' } else { $Lines -join [Environment]::NewLine }
    [System.IO.File]::WriteAllText($targetFile, $content, [System.Text.UTF8Encoding]::new($false))

    Write-Host "Estratto: $safeRel" -ForegroundColor Cyan
    return $true
}

# --- Main ---

$resolvedContext = Resolve-ContextFile -ExplicitPath $ContextFile
Write-Host "Elaborazione: $resolvedContext" -ForegroundColor Green

if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    $baseRoot = if (-not [string]::IsNullOrWhiteSpace($PSScriptRoot)) {
        (Get-Item -LiteralPath $PSScriptRoot).Parent.Parent.FullName
    } else {
        (Get-Location).Path
    }
    $OutputDir = Join-Path -Path $baseRoot -ChildPath 'output'
}

if (-not (Test-Path -LiteralPath $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}
$OutputDir = (Resolve-Path -LiteralPath $OutputDir).Path

Write-Host "Destinazione: $OutputDir" -ForegroundColor Green

$lines = Get-Content -LiteralPath $resolvedContext -Encoding UTF8
$currentFile = $null
$currentContent = [System.Collections.Generic.List[string]]::new()
$extractedCount = 0
$skipNextFenceOpen = $false

# Header supportati:
#   ## File: path/to/file.ext
#   === FILE: path/to/file.ext ===
#   --- FILE: path/to/file.ext ---
$headerRegex = '^(?:#{1,6}\s*File:\s*|={3,}\s*FILE:\s*|-{3,}\s*FILE:\s*)(.+?)(?:\s*(?:={3,}|-{3,})\s*)?$'

foreach ($line in $lines) {
    if ($line -match $headerRegex) {
        # Salva il file precedente
        if ($null -ne $currentFile) {
            if (Save-ExtractedFile -RelativePath $currentFile -Lines $currentContent -BaseOutputDir $OutputDir) {
                $extractedCount++
            }
        }

        $currentFile = $Matches[1].Trim()
        $currentContent.Clear()
        $skipNextFenceOpen = $true
        continue
    }

    if ($null -eq $currentFile) {
        continue
    }

    # Salta il fence di apertura subito dopo l'header (```markdown, ```powershell, ```, ecc.)
    if ($skipNextFenceOpen -and $line -match '^\s*```') {
        $skipNextFenceOpen = $false
        continue
    }
    $skipNextFenceOpen = $false

    $currentContent.Add($line)
}

# Ultimo file
if ($null -ne $currentFile) {
    if (Save-ExtractedFile -RelativePath $currentFile -Lines $currentContent -BaseOutputDir $OutputDir) {
        $extractedCount++
    }
}

if ($extractedCount -eq 0) {
    Write-Warning "Nessun file estratto. Verifica che il markdown contenga header '## File: path'."
} else {
    Write-Host ""
    Write-Host "Completato. Estratti $extractedCount file in: $OutputDir" -ForegroundColor Green
}
