---
title: Benchmark e Valutazione Cross-Modello
copyright: "© 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved."
author: IK0VCK
version: 1.0
updated: 2026-08-15
workflow: TDM 1.0
section: 8
---
# 8. Benchmark e Valutazione Cross-Modello

## 8.1 Scopo

`TurboAI-Benchmark` è il workload di riferimento usato per misurare, in modo ripetibile, quattro cose distinte:

1. **Dogfooding** — verificare che TurboAI stesso, applicato a un caso reale ma limitato, produca un output corretto seguendo i propri gate.
2. **Test di non regressione** — confrontare due release di TurboAI (tool, skill, formato bundle) sullo stesso workload, per accertare che una modifica non abbia degradato la disciplina di esecuzione o la qualità del codice prodotto.
3. **Fine-tuning delle skill** — quando una skill viene riscritta o compattata per un canale/modello specifico (es. la migrazione italiano→inglese descritta nel changelog di TurboAI), il benchmark è il modo per verificare che la nuova skill produca ContextRequest e patch valide, prima di adottarla in produzione.
4. **Confronto tra modelli** — eseguire lo stesso piano con combinazioni diverse di Canale A/B/C (vedi §9) e confrontare correttezza, disciplina sullo scope, qualità ingegneristica ed efficienza operativa.

## 8.2 Struttura

- **`GoldenFiles/`**: scenari deterministici (`Input/`, `Invalid/`, `Expected/`) con `manifest.json` che mappa ogni scenario a input, output atteso e exit code. Gli scenari `Invalid/` sono fatali per costruzione (`fatal-no-output`) e non devono produrre JSON.
- **`.ai-context/Piano-Multi-Task.md`**: piano di riferimento, scritto secondo lo standard di §7 — stessa Anatomia Obbligatoria e Checklist di Chiusura di un piano reale, nessuna eccezione (vedi §7.4).
- **`.ai-context/SOLUTION_GOVERNANCE.md`**: contratto dei dati (formati, formule di aggregazione, regole di errore) su cui il primo task del piano (T0.1) deve convergere prima che venga scritta una riga di codice applicativo.
- **`BenchmarkProtocol/`**: protocollo di evidenza per confronti cross-modello formali.

## 8.3 Modalità di esecuzione

- **`B_ONLY`**: un solo partecipante di Canale B governa ed esegue.
- **`A_PLUS_B`**: Canale B governa, verifica e chiude; Canale A esegue i task assegnati.

Il confronto tra run avviene solo a posteriori, sui report finali di run separate e pulite — non c'è un meccanismo di comparazione "live" tra run in corso.

## 8.4 Convenzione di esecuzione

Da `Readme.md` del pacchetto: copiare la cartella `TurboAI-Benchmark` in una nuova cartella con naming che identifica modello e versione di TurboAI in prova (es. `TurboAI-Benchmark-Grok_4_6-turboai_1_0_4`), copiarvi la versione di `.turbo-ai` da testare, lanciare `aaa-startup-llm-session.cmd` da lì, eseguire il piano, generare il report di valutazione a fine esecuzione. Questa convenzione di naming è ciò che rende le run archiviabili e confrontabili nel tempo senza ambiguità su quale combinazione modello/versione abbia prodotto quale report.

## 8.5 Log delle interazioni significative

Durante l'esecuzione può essere tenuto un log manuale, libero, delle sole interazioni in cui l'utente ha dovuto correggere, reindirizzare o sbloccare l'LLM — prompt di routine (`go`, approvazioni normali, allegati attesi) non vanno registrati. A fine piano lo script di analisi del benchmark può contare le righe che iniziano per `User:` in questo file come indicatore *indicativo* di quanto intervento manuale sia stato necessario: non è una metrica di qualità, è un segnale grezzo da leggere insieme al resto del report, non da sommare tra file multipli in caso di ambiguità sulla fonte.

## 8.6 Non negoziabili

- I file in `GoldenFiles/Expected/` non vanno mai rigenerati automaticamente durante un'esecuzione normale: un aggiornamento del golden richiede una decisione esplicita di contratto e una review semantica, esattamente come un cambio di contratto dati su un progetto reale (vedi Constraints in `Piano-Multi-Task.md`: niente campi non deterministici, niente output parziale dopo un errore fatale).
- Il primo task del piano (T0.1) è sempre un assessment del contratto stesso (ricalcolo indipendente degli aggregati attesi, verifica di sintassi/encoding, verifica che ogni scenario del manifest referenzi un file esistente) — non si parte a scrivere codice prima che la baseline sia stata verificata come internamente coerente, coerentemente con l'approccio "closed-book" di §7.
