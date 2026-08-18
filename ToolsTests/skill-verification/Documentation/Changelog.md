---
title: Changelog TurboAI
copyright: "© 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved."
author: IK0VCK
type: changelog
product: Turbo-AI - skill-verification
version: 1.0
license: MIT
updated: 2026-08-17
---
# Changelog TurboAI - skill-verification

Redatto seguendo le convenzioni di [Keep a Changelog](https://keepachangelog.com/it-IT/1.1.0/)

## [Unreleased]

## [0.2.0] - 2026-08-17

- piano: - skill-verification: verify & fix scenarios

### Fixed

- **golden/info_next_task.md** (scenario 01): il Target Path era dichiarato
  come path nudo (`src/config.py`) invece che relativo a
  `TurboAiWorkingRoot`, causando un context-out privo del file richiesto.
  Ora è `01-start-session-acquisition/testdir/src/config.py`.

### Changed

- **01-start-session-acquisition/run_test.py**: istruzioni di setup
  aggiornate (il context-out è generato automaticamente da turbo-ai,
  nessuna ripresa in chat oltre quel punto); checklist riformulata senza
  logica negata e senza la domanda post-context-out; report ora riporta
  il resoconto completo domanda/risposta invece dei soli item falliti.
- **verifica-skill.cmd**: rimossa la riga di istruzioni duplicata
  ("--- Istruzioni per lo scenario ---", ora stampata solo da
  `run_test.py`); messaggio post-setup condizionale per lo scenario 1.

### Added

- **_common/validators.py**: `extract_target_paths()` e
  `check_context_out_has_paths()` — controllo automatico che verifica la
  presenza dei Target Paths dichiarati nel context-out generato dall'LLM;
  fail-fast sulla checklist umana se un controllo automatico fallisce.
  
## [0.1.0] - 2026-08-15

### Added

- impianto iniziale da mettere a punto

---  

[@IK0VCK]: https://github.com/IK0VCK
