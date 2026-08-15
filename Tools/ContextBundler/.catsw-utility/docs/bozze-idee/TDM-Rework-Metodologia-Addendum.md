---
updated: 2026-08-15
---

# Addendum: Gestione Rework di Milestone in Fase d'Opera

Da inserire in FaseDefinizionePiano.md, come sezione a sé stante.

## Principio

Le milestone vanno definite in modo che una milestone successiva non dipenda
implicitamente dai dettagli implementativi di una milestone precedente.
Se una dipendenza esiste, va dichiarata esplicitamente nella milestone
dipendente — mai lasciata da dedurre. L'obiettivo non è eliminare ogni
dipendenza (spesso impossibile), ma minimizzarla e renderla sempre visibile
a chi legge una singola milestone in isolamento.

Questo principio è ciò che rende un rework di milestone in corso d'opera
un'operazione a raggio contenuto invece che un rischio di propagazione
silenziosa su tutto il piano.

## Quando si applica

Ogni volta che, a milestone già definita (eventualmente già in parte
eseguita), emerge una necessità che richiede di ridefinirne il design
— non un semplice refinement di un singolo task, ma un cambio del
meccanismo/contratto che quella milestone consegna alle successive.

## Protocollo obbligatorio

1. **Blast-radius check.** Prima di riscrivere qualunque task, cercare
   nel resto del piano (milestone successive) ogni occorrenza — per nome
   di meccanismo, chiave di configurazione, comportamento — di ciò che
   il rework va a modificare. Ricerca mirata (grep/ricerca testuale +
   lettura del contesto trovato), non basata su memoria/assunzione di
   quanto letto in precedenza nella sessione.

2. **Dichiarazione esplicita dell'esito.** Prima di procedere alla
   riscrittura, dichiarare in modo esplicito il risultato del check:
   quali milestone/task successivi risultano impattati (se nessuno,
   dirlo esplicitamente e perché — non solo "nessun impatto trovato").
   Questa dichiarazione è parte della consegna, non un passaggio interno
   da omettere.

3. **Atomicità del rework.** Tutti i task della milestone toccati dal
   rework vanno riscritti nello stesso ciclo di consegna. Non si applica
   il nuovo design a un task lasciando gli altri della stessa milestone
   ancora sul design vecchio: uno stato intermedio misto è la fonte più
   comune di errori quando una sessione futura (anche un modello diverso)
   riprende il piano senza il contesto della sessione di rework.

4. **Riuso di lavoro già svolto.** Se un task della milestone era già
   stato eseguito con il design precedente (es. un assessment che ha già
   raccolto dati fattuali indipendenti dal design), non va rieseguito da
   zero se i suoi risultati restano validi — vanno però riformulati
   esplicitamente nei punti in cui referenziano il design vecchio
   (es. nomi di chiavi di configurazione cambiati), non lasciati con
   riferimenti stale.

5. **Traccia del rework.** Il cambio va registrato in un punto stabile
   e persistente — SOLUTION_GOVERNANCE.md e/o changelog del progetto,
   non solo nel testo del piano — così una sessione futura che legge
   solo la governance capisce che quel meccanismo è stato ridisegnato
   e non trova residui del design precedente senza spiegazione.

## Cosa NON fare

- Non riscrivere un singolo task "al volo" mentre si scopre la necessità,
  senza prima aver fatto il blast-radius check sul resto del piano.
- Non assumere che l'assenza di menzioni esplicite in milestone successive
  significhi assenza di dipendenza — verificare, non presumere.
- Non lasciare lo status del piano (es. `status: COMPLETED`) incoerente
  con lo stato reale dei task dopo un rework parziale.
