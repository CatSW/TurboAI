# Piano-Multi-Task — DemoWidget

## Obiettivo
Evoluzione incrementale del componente DemoWidget: pulizia tecnica e piccoli
refactoring propedeutici alle prossime milestone.

## Milestone M0 - Iniziale
- Scaffold iniziale del progetto (vedi git log, commit demowidget-T1.0).

## Milestone M1 - Pulizia tecnica
- Rimozione di costanti e riferimenti obsoleti nel modulo di configurazione.

<next_task>
### T1.1 - Rename a stale constant

1. Target Paths
   - src/config.py

2. Context & Dependencies
   - La costante MAX_RETRY_OLD e' un residuo, va rinominata MAX_RETRY.

3. Implementation Scope
   - Rinominare la costante e i suoi usi nel file indicato.

4. Acceptance Criteria
   - Nessun riferimento residuo a MAX_RETRY_OLD nel file.

5. Delivery Artifacts
   - Patch ZIP con lo script operativo.
</next_task>
