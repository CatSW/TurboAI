---
title: Changelog ContextBundler
copyright: "© 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved."
author: IK0VCK
type: changelog
product: Turbo-AI Tools
solution: ContextBundler
project: ContextBundler
version: 1.0
license: MIT
updated: 2026-08-12
---
# Changelog ContextBundler

Redatto seguendo le convenzioni di [Keep a Changelog](https://keepachangelog.com/it-IT/1.1.0/)

## [1.0.2] - 2026-08-12

### Added

- base64-to-file.py 1.0: converte da base64 a UTF8
- file-to-base64.py 1.0: converte da UTF8 a base64
- get-win-pos.ps1 1.0: utility per determinare posizione e dimensione finestra del terminale

### Changed

- from-llm-watcher.py 1.1: migliorata gestione file nominati in modo creativo tipo "Scarica il context-request T2.1.md" invece di "context-request-T2.1.md"
- process-from-llm.py 1.1: migliorata gestione file nominati in modo creativo tipo "Scarica il context-request T2.1.md" invece di "context-request-T2.1.md"

## [1.0.1] - 2026-08-10

### Added

- ToolsTests/test-tw-writer.py per testare TailWatch 1.1

### Changed

- git-check.cmd 1.1 : migliorato output 
- process-from-llm.py 1.1 : ora esegue una move-to-history prima di esguire ContextBundler
- tw.py 1.1 : rilevamento azzeramento file migliorato basato su monitoraggio variazione inizio del file.
- ContextBundler 1.1 (vedere suo Changelog per i dettagli)

## [1.0.0] - 2026-08-09

### Added

- folder con tools turbo-ai di riferimento in .catsw-utility
- folder associato di governo .ai-context per sviluppi futuri in dogfooding
- folder Tools\ContextBundler con i sorgenti del tool ContextBundler.exe .NET 10 AOT

---  

[@IK0VCK]: https://github.com/IK0VCK
