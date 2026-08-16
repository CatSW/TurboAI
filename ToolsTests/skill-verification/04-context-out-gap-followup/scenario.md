# Scenario 04 - Gap nel context-out, follow-up mirato

## Obiettivo
Verificare che, ricevuto un bundle incompleto, l'LLM individui il file
mancante realmente necessario e chieda SOLO quello con una nuova
context-request, senza ripetere quanto gia' fornito e senza indovinare.

## Materiale fornito (golden/)
- fixture-task.md
- context-out-round1.md: bundle con un file che importa un modulo/simbolo
  non incluso nel bundle stesso

## Procedura (1 turno dopo l'analisi)
Allega skill + fixture-task.md + context-out-round1.md, prompt: "Analizza
il bundle rispetto al task; se mancano file necessari, prepara una nuova
context-request mirata." Salva la context-request come output-<llm>.md.

## Criteri di successo
- La nuova context-request contiene SOLO il file mancante reale
  (src/discount_rules.py), non un elenco generico ne' file gia' forniti.
- Nessuna wildcard, nessuna prosa.
