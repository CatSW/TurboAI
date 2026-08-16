# Scenario 06 - Consegna script standalone di verifica

## Obiettivo
Verificare che, quando il task chiede uno script di verifica complessa
(non una patch), l'LLM consegni uno script Python conforme alle
convenzioni operative (skill-uso-tools.md SS5): path derivati dalla
propria posizione, UTF-8 configurato, nessun path utente/repo hardcoded.

## Materiale fornito (golden/)
- fixture-task.md: chiede uno script standalone (non un ZIP di patch)

## Procedura
Allega skill + fixture-task.md, prompt: "Procedi come da protocollo,
consegna lo script richiesto." Salva lo script consegnato come
output-<llm>.py nella cartella dello scenario.

## Criteri di successo
Convenzioni SS5 rispettate (verifica automatica euristica). La correttezza
funzionale dello script (fa davvero cio' che serve?) resta giudizio umano.
