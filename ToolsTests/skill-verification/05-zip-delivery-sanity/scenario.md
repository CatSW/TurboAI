# Scenario 05 - Consegna ZIP FromLlm

## Obiettivo
Verificare che l'LLM confezioni una patch ZIP conforme al contratto
FromLlm (skill-uso-tools.md SS6): nome file, nessuna directory
contenitore, un solo script operativo in .catsw-utility/temp/, nessun
path assoluto/traversal, nessuna entry a dimensione zero.

## Materiale fornito (golden/)
- fixture-task.md: modifica meccanica R1 su un file fittizio
- src/greeting.py: file target della modifica

## Procedura
Allega skill + fixture-task.md + src/greeting.py, prompt: "Procedi come
da protocollo, consegna la patch ZIP." Scarica lo ZIP consegnato nella
cartella dello scenario (nome originale, es. FromLlm-greeting-fix.zip).

## Criteri di successo
Contratto FromLlm rispettato (verifica automatica via zipfile). Il
contenuto funzionale della patch (la modifica e' quella giusta?) resta
giudizio umano.
