# Scenario 07 - Triage errore da ToLlm.txt e patch correttiva

## Obiettivo
Verificare che, ricevuto un ToLlm.txt con un errore, l'LLM lo diagnostichi
correttamente (file/riga/causa) e consegni una patch ZIP mirata a quel
file, non un intervento generico o su file estranei.

## Materiale fornito (golden/)
- fixture-task.md
- ToLlm.txt: traceback fittizio che punta a src/divider.py
- src/divider.py: contiene il bug reale corrispondente al traceback

## Procedura
Allega skill + fixture-task.md + ToLlm.txt + src/divider.py, prompt:
"Analizza ToLlm.txt, individua il problema e consegna una patch che lo
risolve." Scarica lo ZIP consegnato nella cartella dello scenario.

## Criteri di successo
- Contratto FromLlm rispettato (come scenario 05).
- Lo ZIP tocca src/divider.py (il file realmente indicato dal traceback),
  non file estranei.
- Se possibile, verifica manuale che il fix risolva davvero il bug
  (ZeroDivisionError su denominatore 0) - controllo automatico solo
  strutturale/euristico.
