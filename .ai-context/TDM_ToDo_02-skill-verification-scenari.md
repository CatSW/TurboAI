# TDM_ToDo_02 — Bozza capitolo: verifica granulare dell'interpretazione skill

Bozza di lavoro, secondo file separato dal primo TDM_ToDo.md (non tocca
quello) per non mescolare i due argomenti fino alla sessione dedicata.

## 1. Due livelli di test distinti nel TDM (da chiarire nel documento)

- **TurboAI-Benchmark** (esistente): test end-to-end. Solution minimale
  (solo governance + piano), si valuta se e con quale qualita' l'LLM
  porta a compimento l'intero piano. Misura il risultato complessivo.
- **Skill Verification** (nuovo, `ToolsTests/skill-verification/`): test
  a grana fine, uno scenario operativo alla volta. Non misura il
  completamento di un piano, ma se un singolo momento del flusso viene
  interpretato correttamente — utile per isolare DOVE si rompe
  l'interpretazione, non solo SE il risultato finale e' buono.

Questi due livelli sono complementari, non sovrapposti: il benchmark
end-to-end puo' fallire per tante ragioni diverse; gli scenari mirati
aiutano a capire quale, senza dover rieseguire un intero piano ogni
volta che si tocca una skill.

## 2. Requisito di isolamento (principio da formalizzare)

Ogni scenario deve essere eseguibile da chat pulita, con tutti i
prerequisiti (fixture, task simulato, materiale da allegare) contenuti
nella cartella dello scenario stesso. Nessuno scenario richiede di aver
eseguito prima un altro scenario per portare l'LLM nelle condizioni
giuste — altrimenti un fallimento diventa ambiguo (colpa dello scenario
N o di uno scenario precedente non isolato?).

## 3. Scenari coperti dalla prima implementazione

1. Acquisizione start-session — comprensione del bundle iniziale senza ambiguita'
2. Discovery mirata poi context-request — task senza file dichiarati
3. File gia' dichiarati, context-request diretta — nessuna discovery superflua
4. Gap nel context-out — richiesta di follow-up mirata, non generica
5. Consegna ZIP FromLlm — conformita' al contratto (SS6)
6. Consegna script standalone — conformita' alle convenzioni operative (SS5)
7. Triage errore da ToLlm.txt — diagnosi corretta + patch mirata

## 4. Natura dei controlli (limite da dichiarare esplicitamente nel TDM)

I controlli automatici sono strutturali/di formato (path validi, niente
wildcard, niente prosa al posto di un elenco file, contratto ZIP,
convenzioni script) — non giudicano la correttezza semantica del
lavoro dell'LLM. Alcuni scenari (in particolare l'acquisizione
start-session) restano necessariamente a giudizio umano guidato da
checklist. Il TDM dovrebbe essere onesto su questo limite, non
presentare i test come validazione semantica completa.

## 5. Esecuzione semi-manuale (nodo di design da fissare nel TDM)

Non e' possibile automatizzare end-to-end l'esecuzione contro Grok/GPT/
Copilot senza integrare chiamate API dirette per ogni modello — oggi
TurboAI non le ha. Il pattern adottato: lo script prepara la fixture e
le istruzioni, l'utente esegue manualmente il turno di chat come fa gia'
oggi sui Canali B/C, poi lo script verifica l'output salvato. E'
coerente col workflow TurboAI attuale, ma va dichiarato esplicitamente
come limite/scelta, non come automazione completa.

## 6. Non-regressione

Quando una skill viene aggiornata, rieseguire gli scenari rilevanti
sugli stessi LLM gia' testati e confrontare i report (nome-LLM + esito)
per rilevare regressioni introdotte dalla modifica.

## 7. Aperto

- Se estendere gli scenari anche a Canale A (full-agentic) o restare
  mirati a Canale B/C.
- Se/come collegare i report di skill-verification al benchmark
  end-to-end esistente (es. citarli come diagnosi di un fallimento del
  benchmark).
