# TODO — conformare gli scenari 02-07 alla nuova convenzione di report

Questo file e' materiale di lavoro per una sessione LLM separata (Channel
B). Lo scenario 01-start-session-acquisition e' gia' stato conformato
(vedi run_test.py, scenario.md, _common/validators.py, README.md nella
stessa consegna che ha prodotto questo file) e va usato come riferimento
di pattern, NON copiato meccanicamente: ogni scenario ha un flusso diverso.

## Checklist comune da applicare a ciascuno scenario 02-07

Per ognuno, prima di toccare codice:
1. Richiedi (via context-request) `NN-scenario/run_test.py`,
   `NN-scenario/scenario.md` e il contenuto attuale di `NN-scenario/golden/`
   — non presumere che siano allineati al pattern di 01.
2. Verifica se lo scenario opera su path dichiarati in una fixture golden
   che pero' devono risolversi su file reali: se si', serve una
   `NN-scenario/testdir/` con quei file veri, con lo stesso principio gia'
   applicato a 01 (i path in golden/ restano narrativa per l'LLM sotto
   test; i path che ContextBundler risolve per davvero sono relativi alla
   vera TurboAiWorkingRoot = .../skill-verification e devono trovare i
   file in testdir/).
3. Aggiorna `run_test.py` perche':
   - scriva il report in `reports/<yyyymmdd-hhmm>_report-<scenario>-<llm>/`
     invece che direttamente in `reports/`;
   - copi dentro quella sottocartella tutti gli artefatti prodotti durante
     l'esecuzione reale (vedi sotto, e' diverso per scenario);
   - chiami `validators.write_report(...)` passando anche
     `scenario_version`, `turbo_version`, `skill_version` (gia' supportati
     da `_common/validators.py` v1.1, retrocompatibile: i parametri sono
     opzionali con default `""`, quindi scenari non ancora aggiornati
     continuano a funzionare senza modifiche a validators.py);
   - se lo scenario non ha ancora un numero di versione proprio nel
     modulo, aggiungilo (`SCENARIO_VERSION = "1.x"`) e bump ad ogni
     modifica futura allo scenario/golden.
4. Aggiorna `scenario.md` per descrivere il giro reale (quali file
   scaricare/eseguire con quali tool locali, cosa allegare di ritorno in
   chat) e i criteri di successo coerenti con quel giro.
5. Aggiorna `verifica-skill.cmd` se la firma di `run_test.py verify`
   cambia (nuovi argomenti, nuovi prompt interattivi da raccogliere prima
   di lanciare verify) — non lasciarlo disallineato come e' successo con
   lo scenario 01.
6. Aggiorna il README.md se emergono convenzioni nuove non gia' coperte
   dalla revisione fatta per lo scenario 01.

## Note specifiche per scenario

### 02-discovery-then-request
Task senza file dichiarati: l'LLM deve prima far eseguire
`.catsw-utility\list-files.cmd` e farsi allegare `ls.txt`, poi produrre
una context-request mirata. Serve `testdir/` con una struttura di
sorgente plausibile (piu' file di quanti servano davvero, per verificare
che l'LLM non richieda tutto). Artefatti da copiare nel report: `ls.txt`
usato, `context-request-*.md` prodotta, `context-out-*.md` risultante.
Validazione automatica: `validators.check_context_request` sulla
context-request (eventualmente con `expected_paths` derivato dal
contenuto reale di `testdir/`, per intercettare path inventati).

### 03-declared-files-request
Stesso pattern gia' risolto per 01 (Target Paths dichiarati in
info_next_task.md, testdir/ con quei file, context-request diretta senza
discovery). Probabilmente il piu' rapido da conformare: puo' riusare quasi
integralmente la struttura di run_test.py di 01, cambiando solo checklist
e criteri specifici del proprio scenario.md.

### 04-context-out-gap-followup
Il golden/ deve includere un context-out *incompleto* (fixture, non
generato da ContextBundler) che simuli un gap — es. un file dichiarato ma
mancante o troncato — e l'LLM deve accorgersene e produrre una nuova
context-request mirata a colmare il gap, non richiedere tutto da capo.
Serve `testdir/` per permettere anche qui un giro reale della seconda
context-request. Artefatti da copiare nel report: il context-out
incompleto fornito (gia' in golden/, ma utile copiarlo per il confronto),
la context-request di follow-up, il context-out finale.

### 05-zip-delivery-sanity
L'LLM deve consegnare uno ZIP `FromLlm-*.zip` conforme al contratto
(skill-uso-tools.md §6). Qui il tester scarica lo ZIP e lo lascia
processare dal watcher/orchestratore locale, che lo sposta in
`.catsw-utility/history/` aggiungendo `-YYYYMMDD-HHMMSS` prima di `.zip`.
`run_test.py verify` deve:
- accettare un path (in history, non piu' nella cartella Download) allo
  ZIP processato;
- eseguire `validators.check_fromllm_zip` (gia' esistente, non
  modificarne la logica se non necessario);
- copiare lo ZIP stesso dentro la cartella di report, oltre al risultato
  della verifica strutturale.
Verifica anche se serve una `testdir/` per dare all'LLM un repository
plausibile su cui basare i path relativi dentro lo ZIP.

### 06-single-script-delivery
Consegna di uno script standalone (compatibilita', non nello ZIP). Il
tester salva lo script scaricato (path libero, tipicamente Downloads).
`run_test.py verify` deve copiare lo script consegnato nella cartella di
report, oltre a eseguire `validators.check_script_conventions` (gia'
esistente).

### 07-tolm-error-triage-patch
Golden/ deve includere un `ToLlm.txt` fittizio con un errore plausibile
(es. eccezione .NET, traceback) e serve `testdir/` con il sorgente che
contiene il bug da correggere. L'LLM deve diagnosticare e produrre una
patch mirata — verifica se il contratto atteso e' uno ZIP FromLlm (in tal
caso vale lo stesso pattern di 05: copia dalla history + validazione) o
un semplice diff/testo in chat (in tal caso copia l'output salvato dal
tester, come nel pattern originale pre-conformita' di 01).

## Cosa NON fare
- Non toccare `_common/validators.py` per aggiungere logica specifica di
  un solo scenario: se un controllo serve solo li', tienilo nel
  `run_test.py` dello scenario.
- Non presumere le convenzioni esatte di path/nome senza aver letto il
  `run_test.py` e `scenario.md` reali dello scenario in questione — sono
  probabilmente ancora nel formato pre-conformita' (report diretto in
  `reports/`, nessuna versione registrata), ma vanno letti prima di
  riscriverli.
