---
title: Changelog TurboAI
copyright: "© 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved."
author: IK0VCK
type: changelog
product: Turbo-AI Tools
version: 1.0
license: MIT
updated: 2026-08-15
---
# Changelog TurboAI

Redatto seguendo le convenzioni di [Keep a Changelog](https://keepachangelog.com/it-IT/1.1.0/)

## [Unreleased] - 2026-08-15

- git-check.cmd 1.2 : scrive anche TurboAiWorkingRoot
- ContextBundler scrive anche TurboAiWorkingRoot
- aggiornamenti skill e doc
- implementata - M4 - Configurable ContextBundler output mode
- implementata - M3 - Regression tests
- implementata - M2 - Execute the script directly from the ZIP-defined temp path
- implementata - M1 - Archive the ZIP before extraction
- lavoro su piano - TurboAI utility toolchain v3.0 - FromLlm ZIP retention and temp execution - e altro aggiunto in corso d'opera

## [1.0.4] - 2026-08-13

### Added

- Contratto di archiviazione e validazione dei pacchetti `FromLlm-*.zip`: copia autorevole conservata in `history` con timestamp deterministico, validazione delle entry contro path assoluti e traversal prima dell'estrazione.
- Esecuzione controllata di un singolo script operativo dichiarato dall'inventario dello ZIP, con rimozione della copia estratta a fine esecuzione (la copia autorevole resta nello ZIP archiviato).
- Aggiornamento dei timestamp dei file estratti, per build incrementali coerenti.

### Changed

- Riorganizzazione della documentazione skill in canali A/B (versione EN).

Nota: sviluppo condotto in dogfooding con workflow multi-agente (verifica incrociata Grok/Claude Sonnet sul contratto ZIP, con Gemini in modalità spettatore entusiasta) — parte del piano evolutivo di TurboAI come framework pensato per lo sviluppo assistito da più LLM in collaborazione.

### Folclore

**IK0VCK**:
> Senti, Sezione 11 de che? Qua siamo alla Sezione 31 di Star Trek: le direttive formali si piegano quando c'è da mandare avanti la nave!
> Questo repo È il framework TurboAI, il dogfooding multi-agente è l'anima stessa del progetto. Meno burocrazia da >Starfleet Command, più operatività.
> Procedi con la release [1.0.4] includendo la nota sul dogfooding (e il tifo di Gemini) e dammi i comandi git per chiudere.

Sonnet5 (coda tra le gambe mode, un po' risentito):
> Riconosciuto il conflitto normativo e proceduto con la richiesta dell'utente
> Ok, è casa tua — la sezione 11 l'avete scritta voi, se decidete che per questo progetto il dogfooding è il prodotto (non solo il processo), è una scelta legittima. Segnalo solo una cosa pratica, non per fare il burocrate: se la direzione è questa, converrebbe aggiornare anche la Sezione 11 in skill-uso-tools.md, altrimenti ogni prossima sessione (mia o di Grok) continuerà a segnalartelo come violazione — la regola scritta e la prassi voluta finiranno per divergere. Se vuoi te la preparo come patch separata; per ora procedo con quello che hai chiesto.

## [1.0.3] - 2026-08-13

- ContextBundler con supporto output base64
- tool con valore base64 cablato per prova
- aggiornamento skills

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
