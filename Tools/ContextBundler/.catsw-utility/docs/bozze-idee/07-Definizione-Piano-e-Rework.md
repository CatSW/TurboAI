---
title: Definizione dei Piani di Lavoro e Gestione del Rework
copyright: "© 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved."
author: IK0VCK
version: 1.0
updated: 2026-08-15
workflow: TDM 1.0
section: 7
---
# 7. Standard di Definizione dei Piani di Lavoro (Self-Contained & Token-Optimized)

## 7.0 Modello di Contesto Effettivo (premessa vincolante)

Il vincolo operativo reale è più stretto di un generico "evita di far leggere tutto il piano":

- **Ogni task gira in una chat nuova (reset).**
- **L'LLM esecutore riceve, per default, ESCLUSIVAMENTE il testo racchiuso tra `<next_task>` e `</next_task>`** — non l'Objective, non il Contratto, non i Constraints, non gli altri task, non lo storico dei task già completati.
- L'unico contesto aggiuntivo che l'LLM riceve è ciò che viene esplicitamente allegato alla sessione (file sorgente richiesti, `SOLUTION_GOVERNANCE.md` se lo start-session lo allega di default, eventuali "extra file per task" dichiarati — vedi §7.1.2 punto 6).

Conseguenza diretta: **il testo del singolo task È il piano**, non un suo riassunto. Qualunque informazione non riscritta dentro i delimitatori è, ai fini pratici, persa per l'LLM che esegue quel task — indipendentemente da quanto sia "ovvia" leggendo il file per intero.

## 7.1 Specifiche di Struttura del Piano (Self-Contained Task Framework)

### 7.1.1 Principi Guida per l'Ottimizzazione dei Token

- **Autocontenimento Totale (Closed-Book Execution):** un task deve essere eseguibile leggendo solo il proprio testo delimitato, senza inferenze su Objective/Contratto/Constraints globali o su altri task, completati o meno.
- **Granularità Atomica:** un task non deve essere né troppo generico ("aggiorna tutti i wrapper") né troppo minuto da richiedere 10 sessioni per una modifica banale — deve coincidere con un'unità logica eseguibile in un unico scambio prompt/response.
- **Budget di Ridondanza Mirata:** dato che ogni task riparte da zero, un minimo di duplicazione di contesto tra task è inevitabile e voluto — ma va tenuto mirato: si riporta solo il sottoinsieme di regole/vincoli globali realmente pertinente a QUEL task, in forma compatta, non l'intero Contratto/Constraints ogni volta. Il costo di ridondanza mirata è accettabile; il costo di un task che fallisce per contesto mancante non lo è.
- **Propagazione Esplicita delle Decisioni:** quando un task fissa un valore, un nome di chiave, un path risolto o una convenzione che un task successivo dovrà usare, quel valore deve essere scritto per esteso nel testo del task successivo al momento della chiusura del task corrente — mai lasciato come riferimento implicito ("vedi T5.1", "come deciso sopra"). Se il piano non viene aggiornato a ogni chiusura, il task successivo nasce già rotto.
- **Direttiva di Propagazione (self-flagging):** questo non può dipendere dalla memoria di chi chiude il task. Chi SCRIVE il piano, in fase 3, ha già visione di quali task a valle dipenderanno da un output non ancora noto (tipico dei task di discovery/assessment). Quel task va scritto includendo, nei suoi stessi Acceptance Criteria o Delivery Artifacts, l'istruzione esplicita per l'LLM esecutore di segnalare in modo marcato ogni valore che dovrà essere riportato altrove — es. "se trovi il path cablato, evidenzialo esplicitamente come `PROPAGATE TO T5.2: <valore>`" — così l'output del task stesso guida la chiusura, invece di richiedere che chi chiude ricordi a memoria cosa serviva a valle.
- **No Leakage tra Task:** nessun dettaglio indispensabile per il Task `N` deve stare esclusivamente nel Task `N-1` o `N+1` — se serve, va copiato dentro, non referenziato.

### 7.1.2 Anatomia Obbligatoria di ogni Task nel Piano

```markdown
#### [ID_TASK] - [Titolo Sintetico e Chiaro]

1. Target Paths (Mappa dei File)
   - Elenco ESPLICITO e COMPLETO dei percorsi relativi dei file da creare, modificare o testare.
   - Nessun riferimento generico a "tutti i file" o "i wrapper": solo path esatti.
   - Se il task è di sola discovery/assessment (path non ancora noti), va dichiarato esplicitamente come tale
     e va indicato il punto di partenza della ricerca (es. cartella radice, pattern di ricerca).

2. Context & Dependencies (Contratto Minimo Autosufficiente)
   - Sintesi (poche righe) del SOLO sottoinsieme di regole di business/vincoli globali applicabile a questo task.
   - Qualunque decisione presa in task precedenti da cui questo task dipende (nome chiave di governance,
     path risolto, convenzione adottata) va riscritta qui per intero, non richiamata per riferimento.
   - Eventuali variabili di ambiente, chiavi di configurazione o contratti dati coinvolti.

3. Implementation Scope (Cose da Fare)
   - Elenco puntato delle azioni esatte di refactoring, scrittura o cancellazione codice.

4. Acceptance Criteria (Criteri di Successo)
   - Condizioni oggettive per considerare il task COMPLETATO prima di passare al successivo.
   - Se questo è un task di discovery/assessment da cui dipendono task successivi (§7.1.1 Direttiva di
     Propagazione), includere qui l'obbligo di marcare esplicitamente ogni valore da propagare, es.
     `PROPAGATE TO [ID_TASK]: <valore>`.

5. Delivery Artifacts (Cosa deve produrre l'LLM)
   - Formato dell'output atteso (es. Patch ZIP con script verificatore in `.catsw-utility/temp/`,
     codice completo nei blocchi markdown, o report di assessment).

6. Extra Startup Files (opzionale)
   - Elenco dei file da allegare automaticamente all'avvio sessione per questo specifico task,
     oltre a quelli standard (SOLUTION_GOVERNANCE.md ecc.) — meccanismo dichiarativo per-task,
     non un config globale separato.
```

### 7.1.3 Checklist di Chiusura Task (obbligatoria prima di avanzare `<next_task>`)

Prima di spostare il puntatore `<next_task>` sul task successivo, chi chiude il task corrente deve verificare:

- [ ] Il task successivo ha già Target Paths validi e verificati (non ipotizzati)?
- [ ] Ogni decisione/valore appena fissato in questo task, se rilevante per il successivo, è stato riscritto per esteso nel suo testo?
- [ ] Il task successivo è eseguibile leggendo SOLO il proprio testo, senza aprire il resto del piano?
- [ ] Se il task successivo era uno stub/placeholder, è stato espanso secondo l'Anatomia Obbligatoria (§7.1.2) prima di diventare `<next_task>` attivo?

Un task placeholder (una riga, senza Target Paths/Acceptance Criteria) non deve mai diventare il blocco `<next_task>` attivo così com'è: va prima riscritto secondo §7.1.2.

### 7.1.4 Nota tecnica: il tag `<next_task>` in prosa

Quando il testo del piano deve *menzionare* il tag `<next_task>` (es. nelle istruzioni di resume o nei task che parlano del meccanismo stesso), va scritto in modo che un parser Markdown/HTML non lo interpreti come un tag reale vuoto — altrimenti sparisce dal testo reso. Usare entità (`&lt;next_task&gt;`) o comunque verificare il rendering finale.

## 7.2 Protocollo di Fase Iniziale (Requirements Gathering & Plan Generation)

```
FASE 1: Raccolta Requisiti Tecnico-Funzionali (Input Utente)
              |
              v
FASE 2: Analisi delle Lacune e Questionario di Chiarimento (LLM)
              |
              v
FASE 3: Generazione del Piano Autocontenuto (LLM secondo §7.1)
              |
              v
FASE 4: Chiusura Task e Propagazione (ricorrente, a ogni task)
```

**FASE 1 — Raccolta Requisiti Tecnico-Funzionali.** L'utente fornisce l'obiettivo di alto livello descrivendo: obiettivo finale, vincoli tecnologici/d'ambiente/linguaggio, architettura nota e contratti dati esistenti.

**FASE 2 — Analisi delle Lacune e Questionario di Chiarimento.** L'LLM non genera subito il piano. Analizza l'input e pone domande strutturate per riconoscere ambiguità/assunzioni implicite, individuare file o componenti non chiariti, definire la gestione dei casi limite, identificare modalità di test e validazione. Le risposte a questo questionario NON restano solo nella cronologia della chat di pianificazione: vanno distribuite dentro i `Context & Dependencies` dei task pertinenti in Fase 3 — la chat di pianificazione non è disponibile all'LLM che eseguirà i singoli task.

**FASE 3 — Generazione del Piano Autocontenuto.** Solo dopo le risposte del questionario, l'LLM compila il piano finale secondo l'Anatomia Obbligatoria (§7.1.2), applicando Budget di Ridondanza Mirata e Propagazione Esplicita delle Decisioni fin dalla prima stesura.

**FASE 4 — Chiusura Task e Propagazione (ricorrente).** A ogni chiusura di task, prima di avanzare `<next_task>`: applicare la Checklist di Chiusura (§7.1.3). Non è un evento una tantum in fase di generazione del piano, ma un'attività che si ripete a ogni singolo task per tutta la vita del piano — è la parte più facile da saltare sotto pressione.

---

# 7.3 Gestione Rework di Milestone in Fase d'Opera

## Principio

Le milestone vanno definite in modo che una milestone successiva non dipenda implicitamente dai dettagli implementativi di una milestone precedente. Se una dipendenza esiste, va dichiarata esplicitamente nella milestone dipendente — mai lasciata da dedurre. L'obiettivo non è eliminare ogni dipendenza (spesso impossibile), ma minimizzarla e renderla sempre visibile a chi legge una singola milestone in isolamento.

Questo principio è ciò che rende un rework di milestone in corso d'opera un'operazione a raggio contenuto invece che un rischio di propagazione silenziosa su tutto il piano.

## Quando si applica

Ogni volta che, a milestone già definita (eventualmente già in parte eseguita), emerge una necessità che richiede di ridefinirne il design — non un semplice refinement di un singolo task, ma un cambio del meccanismo/contratto che quella milestone consegna alle successive.

## Protocollo obbligatorio

1. **Blast-radius check.** Prima di riscrivere qualunque task, cercare nel resto del piano (milestone successive) ogni occorrenza — per nome di meccanismo, chiave di configurazione, comportamento — di ciò che il rework va a modificare. Ricerca mirata (grep/ricerca testuale + lettura del contesto trovato), non basata su memoria/assunzione di quanto letto in precedenza nella sessione.

2. **Dichiarazione esplicita dell'esito.** Prima di procedere alla riscrittura, dichiarare in modo esplicito il risultato del check: quali milestone/task successivi risultano impattati (se nessuno, dirlo esplicitamente e perché — non solo "nessun impatto trovato"). Questa dichiarazione è parte della consegna, non un passaggio interno da omettere.

3. **Atomicità del rework.** Tutti i task della milestone toccati dal rework vanno riscritti nello stesso ciclo di consegna. Non si applica il nuovo design a un task lasciando gli altri della stessa milestone ancora sul design vecchio: uno stato intermedio misto è la fonte più comune di errori quando una sessione futura (anche un modello diverso) riprende il piano senza il contesto della sessione di rework.

4. **Riuso di lavoro già svolto.** Se un task della milestone era già stato eseguito con il design precedente (es. un assessment che ha già raccolto dati fattuali indipendenti dal design), non va rieseguito da zero se i suoi risultati restano validi — vanno però riformulati esplicitamente nei punti in cui referenziano il design vecchio (es. nomi di chiavi di configurazione cambiati), non lasciati con riferimenti stale.

5. **Traccia del rework.** Il cambio va registrato in un punto stabile e persistente — `SOLUTION_GOVERNANCE.md` e/o changelog del progetto, non solo nel testo del piano — così una sessione futura che legge solo la governance capisce che quel meccanismo è stato ridisegnato e non trova residui del design precedente senza spiegazione.

## Cosa NON fare

- Non riscrivere un singolo task "al volo" mentre si scopre la necessità, senza prima aver fatto il blast-radius check sul resto del piano.
- Non assumere che l'assenza di menzioni esplicite in milestone successive significhi assenza di dipendenza — verificare, non presumere.
- Non lasciare lo status del piano (es. `status: COMPLETED`) incoerente con lo stato reale dei task dopo un rework parziale.

## 7.4 Relazione con TurboAI-Benchmark

Il piano di riferimento usato in `TurboAI-Benchmark` (`.ai-context/Piano-Multi-Task.md`) è scritto secondo questa stessa disciplina — Anatomia Obbligatoria (§7.1.2), Checklist di Chiusura (§7.1.3), nessuna eccezione perché "è solo un benchmark". È proprio l'applicazione identica dello standard, indipendentemente dal fatto che il piano sia di un progetto reale o del workload di riferimento, a rendere le run comparabili tra modelli e versioni (vedi §8): se il piano stesso variasse in rigore da una run all'altra, un peggioramento osservato non sarebbe più attribuibile al modello/skill in prova.
