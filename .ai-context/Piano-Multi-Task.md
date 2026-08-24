---
title: Piano Multi-Task TurboAI - ND
solution: TurboAI
release_target: TurboAI 1.2.0
updated: 2026-08-21
status: IN_PROGRESS
workflow: TDM 1.0
---

## 1. Obbiettivi
- piano alias agosto-rosso miglioramenti 

## 2. Vincoli

## 3. Milestones and Tasks


## M1 - Skill: Extra Startup Files

### T1.1 - Documentare "Extra Startup Files" nelle skill (Canale A+B e C)

Obiettivo: spiegazione compatta (EN, integrata nel corpo skill, non a parte) di come dichiarare
gli "Extra Startup Files" nel blocco `<next_task>` del piano, eliminando il bisogno del bypass
ad-hoc oggi scritto a mano in SOLUTION_GOVERNANCE.md di alcune solution client.
Scope:
- File: tool-skillsets/skill-tools-use-channels-a-b_en.md, tool-skillsets/skill-tools-use-channels-c_en.md e skill-tools-use-channels-b_en.md (questo lo ricevi tramite skill-uso-tools.md come default in questa start session)
- Contenuto minimo: i file di startup automatici (governance, skill attiva, ultimo changelog)
  non vanno ripetuti; ogni altro file necessario al task va nella sezione
  `##### Extra Startup Files` del next_task, path relativi a TurboAiWorkingRoot, niente
  wildcard, niente contenuti sotto `old.catsw-utility/`
Rischio: R1

##### Extra Startup Files

 - .turbo-ai/docs/tool-skillsets/skill-tools-use-channels-a-b_en.md
 - .turbo-ai/docs/tool-skillsets/skill-tools-use-channels-c_en.md


<next_task>
### T1.2 - Posizioni iniziali sfalsate per le finestre dei watcher

Obiettivo: al primo avvio le finestre dei watcher non devono aprirsi coperte da quella di
startup — l'utente, chiusa/confermata quella sopra, non capisce cosa fare.
Scope: offset di posizione iniziale per ciascuna finestra watcher lanciata allo startup.
Se i file from-llm-watcher.json e/o tail-watch.json sono assenti in `.turbo-ai/` significa che non sono state inizializzate le posizioni e dimenisioni iniziali dei watcher.
Per evitare il problema indicato, si potrebbe inizializzare tali file in modo sfalsato nella finestra principale e aggiungere le istruzioni per personalizzare la posizione di tali finestre.
Quando vengono avviati i watcher, se si preme control-C prima di terminare viene attivato un controllo che se la posizione/dimensione della finestra è variata rispetto a quando indicato nel file json, questo viene aggiornato. Così se si dice all'utente di spostare e ridimensionare la finestra dove desiderato e premere Ctrl+C si avrà la configurazione iniziale impostata.
Bisonga anche migliorare i messaggi nei watcher, quando si preme cotrl+c ora viene indicato solo messaggi del tipo "Arresto richiesto" che sarebbe meglio cambiare in "Posizione e dimensione finestra aggiornata. Se si vuole terminare il Watcher premere la x nel bordo in alto a destra."  e non terminare lo script ma riavviarlo...
 
Rischio: R1/R2 (da confermare in analisi)

vedere la presenza della finestra sottostante. Nel output di aaa-startup-llm-session.cmd 
##### Extra Startup Files

- .turbo-ai/aaa-startup-llm-session.cmd
</next_task>

## M2 - Revisione list-files per solution operative

Obiettivo: il meccanismo di estrazione file, oggi cablato per lo sviluppo di TurboAI stesso,
deve diventare generico per solution operative.
Scope:
- Default: root della solution come target di estrazione, sulla falsa riga di ContextBundler
- Esclusioni: aggiungere filtro su `.turbo-ai` alle esclusioni esistenti
- Estensione: ricerca sottoprogetti via `.csproj`; ogni cartella con un `.csproj` genera una
  voce di menu col proprio nome; selezionandola si estraggono solo i file di quel sottoprogetto
Rischio: R2

---

### M0 - Descrizione

#### T0.1 - Descrizione

**Purpose**
- punto 1
- punto 2

##### Extra Startup Files
- .turbo-ai/process-from-llm.cmd
- .turbo-ai/artifacts/process-from-llm.py
- .turbo-ai/artifacts/process-zip-and-scripts-from-llm.py

**Checks**


**Output**

---


### M42 - END OF PLAN

#### T42.1 Guru Meditation
