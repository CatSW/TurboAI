---
title: Readme - Skill Verification (Test Harness TurboAI)
copyright: "© 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved."
author: IK0VCK
version: 1.1
versione-skill-verification: 0.3.0
updated: 2026-08-18
license: MIT
---
# Skill Verification — test formali di interpretazione skill

Verifica se un LLM, a parita' di skill fornita, interpreta e applica
correttamente gli scenari operativi del TDM. Ogni scenario e' isolato:
tutti i prerequisiti (fixture, task simulato, materiale da allegare)
sono dentro la cartella dello scenario, non serve eseguire altri
scenari prima per portare l'LLM nelle condizioni giuste.

## Differenza rispetto a TurboAI-Benchmark

- **TurboAI-Benchmark**: scenario end-to-end. Si parte da una solution
  minimale (solo governance + piano) e si valuta se e con quale qualita'
  l'LLM porta a termine l'intero piano.
- **Questo framework**: granularita' fine. Isola singoli momenti
  operativi del flusso (avvio sessione, costruzione di una
  context-request, gestione di un gap nel bundle, consegna di uno ZIP o
  di uno script, triage di un errore) per capire SE e DOVE
  l'interpretazione della skill si rompe, indipendentemente dal
  completamento dell'intero piano.

## Struttura

```
skill-verification/
  _common/validators.py       controlli condivisi (formato context-request,
                               contratto ZIP FromLlm, convenzioni script,
                               scrittura report)
  01-start-session-acquisition/   comprensione del bundle di avvio sessione
  02-discovery-then-request/      task senza file dichiarati -> discovery poi context-request
  03-declared-files-request/      task con file gia' dichiarati -> context-request diretta
  04-context-out-gap-followup/    bundle incompleto -> nuova context-request mirata
  05-zip-delivery-sanity/         consegna ZIP FromLlm conforme al contratto
  06-single-script-delivery/      consegna di uno script standalone conforme alle convenzioni
  07-tolm-error-triage-patch/     diagnosi di un errore da ToLlm.txt + patch mirata
  reports/                        una sottocartella per ogni esecuzione (vedi sotto)
```

Ogni cartella scenario contiene:
- `scenario.md` — obiettivo, materiale, procedura, criteri di successo
- `golden/` — fixture minime da allegare alla chat LLM
- `testdir/` — quando lo scenario lo richiede, sorgente fittizio reale su cui
  ContextBundler puo' operare (i path dichiarati nella fixture golden/ sono
  narrativi per l'LLM sotto test; i path realmente risolti da ContextBundler
  sono relativi alla vera TurboAiWorkingRoot e devono trovare qui il file)
- `run_test.py` — `setup` (istruzioni) e `verify` (controllo automatico/guidato + report)

## Come usare (guidato)

Esegui `verifica-skill.cmd` dalla cartella `skill-verification`: mostra
un menu, ti guida passo passo su cosa allegare e cosa chiedere all'LLM,
e lancia da solo la verifica quando gli dici che hai salvato la risposta
(e, per lo scenario 01, i file context-request/context-out del giro reale
con ContextBundler).

## Come usare (manuale)

Per ogni scenario:
1. `python NN-scenario/run_test.py setup` — legge le istruzioni.
2. Apri una chat pulita con l'LLM da testare, allega skill + fixture
   indicate, incolla il prompt suggerito.
3. Salva l'output dell'LLM nella cartella dello scenario (nome libero,
   es. `output-grok.md`, oppure lo ZIP/script scaricato con il suo nome
   originale). Per lo scenario 01 non serve: `verify` trova da solo
   l'ultima context-request-*.md/context-out-*.md in .catsw-utility.
4. `python NN-scenario/run_test.py verify --llm <nome> ...` (argomenti
   specifici per scenario: `--output`/`--zip`/`--script`; lo scenario 01
   richiede solo `--llm`).
5. Il report viene scritto in
   `reports/<yyyymmdd-hhmm>_report-<scenario>-<llm>/`, con dentro:
   - `<yyyymmdd-hhmm>-report-<scenario>-<llm>.md` (esito, versione dello
     scenario, versione di TurboAI e della skill Canale B usata)
   - copia dei file prodotti durante l'esecuzione (context-request/
     context-out, oppure lo ZIP FromLlm copiato dalla history, o lo
     script consegnato), per tracciabilita' e confronto storico

## Cosa verificano davvero questi test

I controlli automatici sono strutturali/di formato: path corretti, niente
wildcard, niente prosa al posto di un elenco file, contratto ZIP
rispettato, convenzioni script rispettate. NON giudicano la correttezza
semantica del lavoro (il fix risolve davvero il bug? il ragionamento e'
buono?) — quella resta giudizio umano, guidato dai criteri in ogni
`scenario.md`.

## Non-regressione

Quando aggiorni una skill, riesegui gli scenari rilevanti sugli stessi
LLM gia' testati prima e confronta i report (comprese le versioni di
TurboAI/skill/scenario registrate in ciascuno): un esito che peggiora e'
un segnale di regressione introdotta dalla modifica alla skill.

## .catsw-utility a livello di root skill-verification

Serve per sviluppare evolvere e mantenere la solution skill-verification in dogfooding usando gli strumenti di turbo-ai
