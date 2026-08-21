---
title: Readme - Manuale Utente & Architettura TurboAI
copyright: "© 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved."
author: IK0VCK
version: 1.3
versione-turbo-ai: 1.1.0
updated: 2026-08-21
license: MIT
---

# Turbo-AI tools by IK0VCK @ CatSW

## Scopo

Guida rapida e operativa per l'utente all'uso degli strumenti di automazione e governance presenti nella directory `.turbo-ai`.

## 0. Prerequisiti

- **Python v3.14.6** (o superiore - obbligatorio): verificare da prompt dei comandi con `python --version`.
- **Git v2.54** (o superiore - obbligatorio): verificare con `git --version`.
- **PowerShell 7.6.4** (o superiore - consigliata).
- **ripgrep (`rg`) v15.1.0** (o superiore - consigliato): utilizzato dall'LLM per ricerche veloci nel codice.

*Lettura metodologica consigliata:* [TurboAI Documento TDM](./.turbo-ai/docs/TurboAI.md)

---

## Avvio di TurboAI

Per avviare una sessione TurboAI, eseguire `aaa-startup-llm-session.cmd` dalla cartella `.turbo-ai`.

Lo script apre automaticamente due finestre di supporto:

- **`from-llm-watcher.cmd`** — monitora la cartella Downloads in attesa di uno zip `FromLlm-*` (o di uno script `FromC-*` per il Canale C); quando lo trova, lo elabora automaticamente generando il context-out corrispondente.
- **`tail-watch.cmd`** — mostra in tempo reale il log/output corrente, per seguire l'elaborazione senza dover aprire manualmente i file di log.

Entrambe le finestre restano aperte per tutta la sessione di lavoro.

Al primo avvio:
- se manca `skill-uso-tools.md`, viene richiesta la selezione della skill tramite `switch-skill.cmd`;
- le finestre di `tail-watch` e `from-llm-watcher` chiedono di essere posizionate/ridimensionate manualmente (premere INVIO a operazione conclusa); la posizione viene salvata in `tail-watch.json`/`from-llm-watcher.json` e riutilizzata ai lanci successivi. Se si vuole cambiare posizione, cancellare il corrispettivo file json ed al prossimo avvio verrà richiesta la posizione.


## 1. Inventario del repository (`ls.txt`)

L'inventario dei file viene richiesto dall'LLM solo in caso di effettiva necessità per ottimizzare il consumo di token. Se richiesto:

1. Aprire PowerShell nella cartella `.turbo-ai`.
2. Eseguire lo script:

```powershell
.\list-files.cmd
```

3. Allegare in chat il file ls.txt generato.

## 2. Esecuzione ricerche rapide con rg

Quando l'LLM richiede di cercare pattern o testi nel repository, fornisce un comando che invia l'output direttamente negli Appunti:

```PowerShell
rg <opzioni> <pattern> .. | Set-Clipboard
```

Eseguire il comando nella sessione PowerShell in .turbo-ai e incollare il contenuto degli Appunti nella chat LLM.

## 3. Gestione automazione ContextBundler

Quando l'LLM necessita di raccogliere il contesto di più file sorgente, genera un file scaricabile denominato:

context-request-<descrizione>.md

### Flusso operativo:

Download: Scaricare il file context-request-*.md fornito dall'LLM.

Elaborazione automatica: Il daemon watcher (from-llm-watcher) rileva il file nella cartella Downloads e avvia l'orchestratore (process-from-llm), che invoca ContextBundler.exe.

Output generato: Viene creato automaticamente il file context-out-<descrizione>.md dentro la cartella .turbo-ai.

Invio all'LLM: Trascinare e allegare in chat il file context-out-<descrizione>.md.

## 4. Raccolta output PowerShell multi-comando

Quando occorre eseguire test o verifiche complesse, l'LLM fornisce un blocco PowerShell che raccoglie gli esiti nel file %USERPROFILE%\Downloads\ToLlm.txt.

### Flusso operativo:

Incollare il blocco nella sessione PowerShell aperta in .turbo-ai.

Il blocco esegue i comandi e termina con il messaggio: Premi Invio o ESC 😄.

Trascinare il file ToLlm.txt dalla cartella Download alla chat LLM.

## 5. Ricezione ed applicazione artefatti (Canale A / B - Download Nativo)

Sui canali ad alta capacità (es. Claude, Grok o Gemini Advanced) l'LLM consegna le modifiche direttamente tramite file scaricabili con prefisso FromLlm-:

ZIP patch multi-file: FromLlm-<descrizione>.zip

Script singoli di verifica: FromLlm-<descrizione>.py (o .ps1)

### Flusso operativo:

Download: Scaricare il file FromLlm-*.

Applicazione automatica: from-llm-watcher rileva l'artefatto e invoca process-from-llm, che estrae lo ZIP nella root del repository o esegue lo script di verifica in .turbo-ai/temp/.

Log di esito: Gli esiti dell'esecuzione vengono scritti in ToLlm.txt.

Conferma: Allegare ToLlm.txt in chat quando richiesto.

## 6. Ricezione ed applicazione artefatti (Canale C - Python Generator Bridge)

Sui canali Web LLM con restrizioni sui download binari/ZIP (es. Gemini Free Tier e interfacce web standard):

Emissione dello Script Generatore: L'LLM emette un blocco di codice Python contenente il payload del bundle.

Salvataggio in Downloads: Salvare il codice come script Python nella cartella Downloads con prefisso obbligatorio FromC-:
%USERPROFILE%\Downloads\FromC-<descrizione>.py
(Il prefisso FromC- attiva la catena di automazione del watcher).

Generazione del Bundle: Il watcher esegue lo script che crea il file context-out-<descrizione>.md dentro la cartella .turbo-ai.

Impacchettamento ZIP: Dalla cartella .turbo-ai, eseguire:

```DOS
genera-zip.cmd
```
Lo script produce il file .turbo-ai\output\FromLlm-<descrizione>.zip.

Applicazione: Lo ZIP generato viene elaborato ed estratto automaticamente della pipeline locale unbundler / process-from-llm.

## 7. Utility Script in .turbo-ai

Layout delle Utility

```DOS
.turbo-ai/
  ├── unbundler.cmd          # Wrapper Windows per unbundler.py (estrazione debug)
  ├── genera-zip.cmd         # Converte context-out-*.md in FromLlm-*.zip
  ├── purga-output.cmd       # Svuota la cartella output/ dagli ZIP generati
  ├── artifacts/
  │   ├── unbundler.py       # Motore di decompressione bundle (Format v3 e legacy)
  │   ├── genera_zip.py      # Motore di compressione bundle in ZIP
  │   └── get-win-pos.ps1    # salva la posizione e dimensione delle finestre dei watcher al primo avvio in file json
  ├── output/                # Cartella di destinazione degli ZIP prodotti da genera-zip.cmd
  ├── temp/                  # Cartella di esecuzione script temporanea
  ├── history/               # Cartella salvataggio file processati
  ├── docs                   # Cartella Documentazione con Documento TurboAI.md (TDM -> TurboAI Development Method) 
  └── context-out-<desc>.md  # File di bundle da processare
```

Guida rapida all'uso di genera-zip.cmd:

1. Copiare o generare un file context-out-<descrizione>.md (in chiaro BundleFormatVersion 3 o Base64) dentro .turbo-ai\.
2. Eseguire genera-zip.cmd.
3. Recuperare lo ZIP creato in .turbo-ai\output\FromLlm-<descrizione>.zip.
4. Usare purga-output.cmd per ripulire la cartella output/ a lavoro ultimato.

## 8. Riepilogo dei file di workflow

- ls.txt: inventario dei file di progetto (generato solo su richiesta).

- context-request-*.md: manifest di richiesta contesto generato dall'LLM.

- context-out-*.md: bundle compresso/strutturato generato da ContextBundler o dallo script FromC-*.py.

- FromC-*.py: script generatore Python emesso dal Canale C (da salvare in Downloads).

- FromLlm-*.zip / FromLlm-*.py: pacchetti ZIP o script applicativi elaborati da process-from-llm.

- ToLlm.txt: log e report delle verifiche locali (da allegare in chat).

## 9. Licenza & Note Legali

Questo progetto è distribuito sotto Licenza MIT. Per il testo completo, consultare il file `LICENSE` presente nella radice del repository.

- Copyright: © 2026 Stefano Vesco (IK0VCK) - CatSW.
- Uso Commerciale e Privato: Gratuito e consentito senza restrizioni.

