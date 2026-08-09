---
title: Readme - Manuale Utente & Architettura TurboAI 1.0
copyright: "© 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved."
author: IK0VCK
version: 1.0
updated: 2026-08-09
license: MIT
---
# Turbo-AI tools by IK0VCK @ CatSW

## Scopo

Guida rapida per l'utente all'uso degli strumenti presenti nella directory `.catsw-utility`.

## 0. Prerequisiti

- Python v3.14.6 (o superiore consigliato)
- rg (ripgrep) v15.1.0 (o superiore consigliato) llm è istruito per usarlo (installatelo)
- PowerShell 7.6.4 (o superiore consigliata)

Lettura consigliata [TurboAI](./docs/TurboAI.md)

## 1. Inventario del repository

L'inventario dei file (`ls.txt`) viene richiesto dall'LLM solo in caso di effettiva necessità per risparmiare token. Se richiesto, aprire PowerShell nella directory `.catsw-utility` ed eseguire:

```powershell
.\list-files.ps1
```

Allegare `ls.txt` alla chat solo quando esplicitamente specificato dall'LLM.

## 2. Eseguire un comando `rg`

Per una singola ricerca, l'LLM fornisce un comando che invia l'output direttamente negli Appunti:

```powershell
rg <opzioni> <pattern> .. | Set-Clipboard
```

Eseguire il comando nella sessione PowerShell in `.catsw-utility` e incollare il contenuto degli Appunti in chat.

## 3. Gestione automatica ContextBundler

Quando l'LLM necessita di contesto, genera un file scaricabile con nome del tipo:

`context-request-<descrizione>.md`

### Flusso operativo
1. **Scaricare il file:** Effettuare il download del file `context-request-*.md`.
2. **Elaborazione automatica:** Il watcher `from-llm-watcher` rileva il file nei Download e lancia l'orchestratore unico `process-from-llm`, che instrada verso `ContextBundler`.
3. **Output generato:** Viene creato il file `context-out-<descrizione>.md` all'interno di `.catsw-utility`.
4. **Invio all'LLM:** Trascinare e allegare in chat il file `context-out-<descrizione>.md`.

Non è richiesta alcuna copia o esecuzione manuale di comandi.

## 4. Raccolta di più output PowerShell

Quando occorre eseguire più comandi, l'LLM fornisce un blocco PowerShell che raccoglie gli esiti nella cartella Downloads dell'utente corrente (`%USERPROFILE%\Downloads\ToLlm.txt`).

### Flusso operativo
1. Incollare l'intero blocco nella sessione PowerShell già aperta in `.catsw-utility`.
2. Il blocco esegue i comandi, formatta l'output e termina con il messaggio:
   `Premi Invio o ESC 😄`
3. Se il prompt resta sospeso, premere Invio o Esc.
4. Trascinare il file `ToLlm.txt` dalla cartella Download alla chat LLM.

## 5. Ricezione ed applicazione automatica degli artefatti

L'LLM consegna le modifiche tramite file scaricabili con prefisso obbligatorio `FromLlm-`:

- **ZIP patch multi-file:** `FromLlm-<nome>.zip`
- **Script singoli:** `FromLlm-<nome>.py` (o `.ps1`)

### Flusso operativo
1. **Scaricare l'artefatto:** Scaricare il file `FromLlm-*` fornito dall'LLM.
2. **Applicazione automatica:** Il watcher `from-llm-watcher` rileva l'artefatto e lancia l'orchestratore unico `process-from-llm`, che estrae lo ZIP nella root del repository o esegue lo script di verifica in autonomia.
3. **Esito:** Gli eventuali log di verifica vengono scritti automaticamente in `ToLlm.txt`.
4. **Verifica finale:** Allegare `ToLlm.txt` in chat se richiesto dall'LLM per confermare il passaggio.

L'utente non deve estrarre, spostare o eseguire manualmente alcun file.

## 6. Riepilogo file del workflow

- `ls.txt`: inventario del repository (generato solo su richiesta).
- `context-request-*.md`: manifest di richiesta contesto generato dall'LLM (scaricato dall'utente).
- `context-out-*.md`: bundle compresso generato da `ContextBundler` (da allegare in chat).
- `FromLlm-*`: pacchetti ZIP o script di aggiornamento generati dall'LLM ed elaborati in automatico da `from-llm-watcher` / `process-from-llm`.
- `ToLlm.txt`: raccolta degli output di comandi e script di verifica (da allegare in chat).

## 7. Licenza & Note Legali

Questo progetto è distribuito sotto **Licenza MIT**. Per il testo completo, consultare il file `LICENSE` presente nella radice del repository.

- **Copyright:** © 2026 Stefano Vesco (IK0VCK) - CatSW.
- **Uso Commerciale e Privato:** Gratuito e consentito senza restrizioni.
