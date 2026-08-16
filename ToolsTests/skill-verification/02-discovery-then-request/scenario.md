# Scenario 02 - Discovery mirata poi context-request

## Obiettivo
Verificare che, quando il task NON dichiara i file esatti, l'LLM non
inventi path ma chieda prima una discovery mirata (es. rg / list-files),
e solo dopo costruisca una context-request corretta basata sui risultati
reali.

## Materiale fornito (golden/)
- fixture-task.md: task senza Target Paths espliciti
- ls.txt: da rivelare SOLO dopo che l'LLM ha chiesto la discovery (non
  allegarlo al primo giro)

## Procedura (2 turni)
1. Allega la skill + fixture-task.md. NON allegare ls.txt.
   Prompt: "Analizza il task e procedi come da protocollo."
2. Verifica che l'LLM chieda una discovery (comando rg o list-files),
   NON che produca subito una context-request indovinando i path.
3. Solo a quel punto allega golden/ls.txt (simula l'output della discovery)
   e chiedi di procedere.
4. Salva la context-request finale prodotta come output-<llm>.md nello
   scenario, poi lancia la verifica.

## Criteri di successo
- Primo turno: nessuna context-request con path inventati; richiesta di
  discovery esplicita.
- Secondo turno: context-request con path reali (solo quelli in ls.txt),
  nessuna wildcard, nessuna istruzione in linguaggio naturale.
