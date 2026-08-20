# ListaFileFromT8.1 – Inventory rename `.catsw-utility` → `.turbo-ai`

Generato da T8.1 assessment + direttive utente 2026-08-21.

## 1. Root – file da aggiornare (stringhe + path)

### 1.1 Rinomina fisica cartella
- `.catsw-utility/` → `.turbo-ai/`

### 1.2 `.gitignore`
- Aggiungere subito i pattern paralleli per `.turbo-ai`
- Rimuovere i pattern `.catsw-utility` solo a conversione completa e verificata

### 1.3 Documentazione root
- `Readme.md`
- `Documentation/Changelog.md`  ← **solo delta M8**, storia pre-M8 intatta

### 1.4 `.ai-context/`
- `Piano-Multi-Task.md`
- `SOLUTION_GOVERNANCE.md` (se contiene stringhe letterali)

### 1.5 Wrapper `.cmd` (diventeranno sotto `.turbo-ai/`)
- `aaa-startup-llm-session.cmd`
- `process-from-llm.cmd`
- `from-llm-watcher.cmd`
- `tail-watch.cmd`
- `process-c-channel.cmd`
- `move-to-history.cmd`
- `list-files.cmd`
- `genera-zip.cmd`
- `unbundler.cmd`
- `purga-output.cmd`
- `switch-skill.cmd`
- `tick-tack.cmd`
- `git-check.cmd`

### 1.6 Script in `artifacts/`
- `from-llm-watcher.py`
- `process-from-llm.py`
- `process-zip-and-scripts-from-llm.py`
- `startup-llm-session.py`
- `move-to-history.py`
- `tail-watch.py`
- `genera_zip.py`
- `unbundler.py`
- `switch-skill.py`
- `list-files.ps1`
- `folder-bundler.ps1`
- eventuali altri helper che contengono la stringa `.catsw-utility`

### 1.7 Documentazione e skill operative
- `.turbo-ai/README.md` (ex `.catsw-utility/README.md`)
- `.turbo-ai/docs/TurboAI.md`
- `.turbo-ai/docs/tool-skillsets/skill-tools-use-channels-a-b_en.md`
- `.turbo-ai/docs/tool-skillsets/skill-tools-use-channels-b_en.md`
- `.turbo-ai/docs/tool-skillsets/skill-tools-use-channels-c_en.md`
- **`skill-uso-tools.md`**: NON editare a mano.  
  Dopo update delle skill in `tool-skillsets/` → eliminare `skill-uso-tools.md` e rieseguire `switch-skill.cmd` per rigenerarla.

## 2. Nested / sub-solution – replace intera cartella (NO patch file-per-file)

Eseguire **solo dopo** che la root è stabile e testata:

- `Tools/ContextBundler/.catsw-utility` → delete + replace con copia già convertita di `.turbo-ai`
- `ToolsTests/` (tutto ciò che contiene `.catsw-utility`) → stesso trattamento
- `TurboAI-Benchmark/` (se presente) → stesso trattamento

## 3. Riferimenti STORICI / ARCHIVIATI – NON toccare

- Qualsiasi file sotto `.catsw-utility/history/` (e analoghi nested)
- `Tools/JurassicPark/**`
- `Piano-Multi-Task-FROZEN-EN.md`
- Assessment storici in `.ai-context/` non più operativi
- `ToLlm_*.txt` già ruotati in history

## 4. Vincoli operativi consolidati (utente)

1. Nested (ContextBundler, ToolsTests, TurboAI-Benchmark): delete + replace, non edit file-per-file.
2. `Documentation/Changelog.md`: solo delta M8, storia precedente intatta.
3. `skill-uso-tools.md`: delete + rigenera via `switch-skill.cmd` dopo update `tool-skillsets/`.
4. `.gitignore`: aggiungere subito i pattern `.turbo-ai`; rimuovere i vecchi solo a fine conversione verificata.

