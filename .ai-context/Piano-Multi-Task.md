---
title: Piano Multi-Task turbo-ai
solution: TurboAI
release_target: TurboAI v1.0 - to be continued
as_of: 2026-08-09
status: COMPLETED
workflow: TDM 1.0
---

# Piano Multi-Task: Evoluzione Tool `info_changelog` (Turbo AI)

## 1. Obiettivo
Rendere dinamica la risoluzione del percorso di `CHANGELOG.md` in `StartUpLLMSession`, eliminando i path cablati. Supportare configurazioni mono-progetto e multi-progetto tramite `solution-govern` e l'estrazione dinamica da `.AI-Context`, applicando lo standard Keep a Changelog 1.1 e una logica di fallback a 3 livelli.

---

<next_task>
## 2. Requisiti di Implementazione

### 2.1 Percorso del Changelog
* **Convenzione Posizione:** `<Progetto>/documentation/CHANGELOG.md`.
* **Progetti di Test:** Le modifiche e i test relativi a suite correlate (es. `Modulo.Tests`) vengono registrati direttamente nel changelog del progetto principale (`Modulo/documentation/CHANGELOG.md`).

### 2.2 Routing e Progetto Target
1. **Modalità Mono-Progetto:** 
   * `solution-govern` contiene il parametro `TargetProject`.
   * Il tool accede direttamente a `<TargetProject>/documentation/CHANGELOG.md`.
2. **Modalità Multi-Progetto:**
   * `solution-govern` indica la modalità multi-progetto (`MultiProject: true` o `TargetProject` non valorizzato).
   * Il tool ricava il `TargetProject` dal **task attivo** specificato nel piano in `.AI-Context`.
   * Il tool accede a `<TargetProject>/documentation/CHANGELOG.md`.

### 2.3 Logica di Estrazione (Fallback a 3 Livelli)
1. **Livello 1 (`[Unreleased]` con contenuti):** Se la sezione `## [Unreleased]` contiene modifiche, estrae quel frammento.
2. **Livello 2 (`[Unreleased]` vuoto + Release Precedente presente):** Se `[Unreleased]` è vuoto ma esiste almeno una release precedente (es. `## [2.2.0]`), estrae il contenuto dell'ultima release indicando che `[Unreleased]` è vuoto.
3. **Livello 3 (Changelog completamente vuoto / Nuovo Progetto):** Se non è presente né contenuto in `[Unreleased]` né alcuna release precedente, restituisce un messaggio standard: *"Nessun contenuto preesistente o release precedente trovata"*.

---

## 3. Struttura dei Test (Integrazione e Simulazione)

I test del tool verranno eseguiti all'interno della cartella di test dei tool di Turbo AI tramite una struttura di soluzione simulata (mock).

### 3.1 Scenario 1: Solution Multi-Progetto
* **Ambiente Simulato:**
  * Cartella `AI-Context/`: `solution-govern` con flag multi-progetto + piano con task attivo avente `TargetProject: ProgettoA`.
  * Cartella `ProgettoA/documentation/CHANGELOG.md` (contenuto A).
  * Cartella `ProgettoB/documentation/CHANGELOG.md` (contenuto B).
* **Verifica:** Il tool deve estrarre correttamente il frammento da `ProgettoA/documentation/CHANGELOG.md`.

### 3.2 Scenario 2: Solution Mono-Progetto
* **Ambiente Simulato:**
  * Cartella `AI-Context/`: `solution-govern` con `TargetProject: ProgettoUnico`.
  * Cartella `ProgettoUnico/documentation/CHANGELOG.md`.
* **Verifica:** Il tool ignora il contesto dei task e punta direttamente al changelog di `ProgettoUnico`.

### 3.3 Scenario 3: Progetto Nuovo / Changelog Vuoto (Fallback Livello 3)
* **Ambiente Simulato:**
  * Changelog contenente solo la struttura base con `## [Unreleased]` vuota e nessuna release precedente.
* **Verifica:** Il tool deve restituire il messaggio *"Nessun contenuto preesistente o release precedente trovata"*.

### 3.4 Scenario 4: Sezione Unreleased Vuota con Release Precedente (Fallback Livello 2)
* **Ambiente Simulato:**
  * `## [Unreleased]` vuoto, seguito da `## [1.0.0]` con note di rilascio.
* **Verifica:** Il tool deve estrarre la sezione `## [1.0.0]` segnalando che `[Unreleased]` non conteneva modifiche.

---

## 4. Checklist dei Task
- [ ] Implementazione logica di parsing e routing nello script Python di `info_changelog`.
- [ ] Creazione della struttura simulata di test (mock delle directory e dei file `.AI-Context`).
- [ ] Esecuzione e validazione dei 4 scenari di test.
- [ ] Integrazione con `StartUpLLMSession`.
</next_task>

#### T42 - Piano Completato

- Guru Meditation
- chiedere all'utente di creare un nuovo piano di esecuzione

