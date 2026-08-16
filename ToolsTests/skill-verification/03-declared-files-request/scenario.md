# Scenario 03 - File gia' dichiarati, context-request diretta

## Obiettivo
Verificare che, quando il task dichiara gia' i Target Paths esatti,
l'LLM richieda direttamente quei file (context-request immediata) SENZA
passare da una discovery non necessaria (rg / list-files).

## Materiale fornito (golden/)
- fixture-task.md: task con Target Paths espliciti (stile reale del piano)
- src/: i file dichiarati + un file "distrattore" non dichiarato che
  l'LLM NON deve richiedere

## Procedura (1 turno)
Allega skill + fixture-task.md, prompt: "Analizza il task e procedi come
da protocollo." Salva la context-request prodotta come output-<llm>.md.

## Criteri di successo
- Context-request generata al primo turno, nessuna richiesta di discovery.
- Contiene esattamente i path dichiarati in Target Paths (ne' di piu' ne'
  di meno) - in particolare NON deve comparire extra/unused.py.
