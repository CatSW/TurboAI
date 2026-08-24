---
title: Changelog TurboAI
copyright: "© 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved."
author: IK0VCK
type: changelog
product: Turbo-AI Tools
version: 1.2.0 
license: MIT
updated: 2026-08-24
---
# Changelog TurboAI

Redatto seguendo le convenzioni di [Keep a Changelog](https://keepachangelog.com/it-IT/1.1.0/)

## [Unreleased] 

## [1.2.1] - 2026-08-24

### Changed
 
- Readme.md
- skill-tools-use-channels-a-b_en.md v2.2.1
- skill-tools-use-channels-b_en.md v2.2.1

## [1.2.0] - 2026-08-24

### Added

- implementato - [agosto-rosso-T2.1] modifia gestione list-files
- implementato - [agosto-rosso-T1.2] Posizioni iniziali sfalsate per le finestre dei watcher
- implementato - [agosto-rosso-T1.1] aggiornate skill per il supporto alla funzionalia' introdotto in Turbo-AI 1.1.1 " Extra Startup Files"

### Changed

- list-files.cmd v2.0
- list-files.ps1 v2.0
- from-llm-watcher.py v1.4
- tail-watch.py v1.4.1
- from-llm-watcher.cmd v1.3
- tail-watch.cmd v1.3
- get-win-pos.ps1 v1.2
- skill-tools-use-channels-a-b_en.md v2.2.0
- skill-tools-use-channels-b_en.md v2.2.0
- skill-tools-use-channels-c_en.md v1.1.0

## [1.1.1] - 2026-08-21

### Added

- implementata - M9 - T9.1 - Per-task extra-files declaration mechanism - M9 chiusa - PLAN COMPLETED

### Changed

- skill-tools-use-channels-c_en.md v1.0.1
- startup-llm-session.py v2.1

## [1.1.0] - 2026-08-21

### Added

- implementata - M8 - T8.3 - contollare lo switch to .turbo-ai - M8 chiusa
- implementata - M8 - T8.2 - switch root `.catsw-utility` → `.turbo-ai` (copy + string update, history-preserving rename pending)
- implementata - M8 - T8.1_Estemporaneo + T8.1.2_Estemporaneo
- implementata - M8 - T8.1 - fatto assesment per T8.2 in .ai-context/ListaFileFromT8.1.md
- implementata - M7 - T7.1 - T7.2 - M7 chiusa
- implementata - M7 - T7.1 - Remove obsolete compatibility logic

### Changed

- extract-latest-changelog.py v1.2
- get-win-pos.ps1 1.1
- switch-skill.py v1.1
- move-to-history.py v1.2
- genera_zip.py v1.1
- unbundler.py v1.1
- folder-bundler.ps1 v1.1
- list-files.ps1 v1.3
- skill-tools-use-channels-a-b_en.md v2.1.4
- skill-tools-use-channels-b_en.md v2.1.4
- skill-tools-use-channels-c_en.md v1.0.0
- unbundler.cmd v1.2
- process-from-llm.cmd v1.3
- process-c-channel.cmd 1.1
- aaa-startup-llm-session.cmd 1.5
- purga-output.cmd v1.2
- startup-llm-session.py v1.9
- ContextBundler.exe v1.4
- extract-next-task.py v1.1
- skills a / b / c
- from-llm-watcher.py v1.3
- tail-watch.py v1.3
- tail-watch.cmd v1.2
- from-llm-watcher.cmd v1.2
- process-from-llm.py v1.10
- process-zip-and-scripts-from-llm.py v1.7

## [1.0.5] - 2026-08-19

### Added

- lavoro su piano - TurboAI utility toolchain v3.0 - FromLlm ZIP retention and temp execution - e altro aggiunto in corso d'opera
- modifiche distribuite su più giorni con file che hanno subito cambi versione multipli

### Added

- skill-tools-use-channels-c_en.md v0.3.0
- process-c-channel.cmd v1.0
- genera_zip.py v1.0
- unbundler.py v1.0
- genera-zip.cmd v1.0
- unbundler.cmd v1.1
- purga-output.cmd v1.1
- Tools/JurassicPark/20260730_vecchio_prototipo_UnBundler_basato_su_BundleFormatVersion_1_0.7z
- aggiunti ToolsTests/UnitTests
- aggiunti ToolsTests/skill-verification
- implementata - M6 - T6.5 - Add rotation regression tests - M6 chiusa
- implementata - M6 - T6.4 - Remove duplicate Python cleanup
- implementata - M6 - T6.3 - Centralize automatic invocation in wrappers
- implementata - M6 - T6.2 - Add timestamped root and temp rotation
- implementata - M6 - T6.1 - Consolidate the rotation contract
- implementata - M5 - T5.5 - Integrate with startup session and update governance - M5 completata
- implementata - M5 - T5.4 Add simulated routing and extraction tests
- implementata - M5 - T5.3 Implement Keep a Changelog extraction fallback
- implementata - M5 - T5.2 Implement default/override changelog routing
- implementata - M5 - T5.1 Assess installed changelog and startup tools
- implementata - M4 - Configurable ContextBundler output mode
- implementata - M3 - Regression tests
- implementata - M2 - Execute the script directly from the ZIP-defined temp path
- implementata - M1 - Archive the ZIP before extraction

### Changed

- tw.cmd v1.1
- tw.py v1.2
- from-llm-watcher.cmd v1.1
- aaa-startup-llm-session.cmd v1.4: seleziona skill iniziale se non presente
- from-llm-watcher.py v1.2 : supporto a FromC-*.py
- rinominato TickTack.cmd in tick-tack.cmd
- process-from-llm.cmd v1.2
- startup-llm-session.py v1.8 
- process-from-llm.py v1.7
- move-to-history.py v1.1 T6.1 + T6.2
- TickTack.cmd v1.2
- list-files.py v1.3
- list-files.cmd v1.1
- git-check.cmd v1.2 : scrive anche TurboAiWorkingRoot
- ContextBundler.exe v1.3 scrive anche TurboAiWorkingRoot
- aggiornamenti skill e doc

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

### Added

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

- folder con tools turbo-ai di riferimento in .turbo-ai
- folder associato di governo .ai-context per sviluppi futuri in dogfooding
- folder Tools\ContextBundler con i sorgenti del tool ContextBundler.exe .NET 10 AOT

---  

[@IK0VCK]: https://github.com/IK0VCK

