# Next task – generated 2026-08-18T09:49:35

## T1.1 - Riverifica 01-start-session-acquisition

- ricevi 20260817_LavorazioneBuildSkillVerification.md ed analizzalo
- dopo le modifiche conseguenti andrà riprovato lo scenario 01-start-session-acquisition e fatte nuove iterazioni su T1.1 fino a quando IK0VCK lo ritiene soddisfacente
- aggiornare Documentation/Changelog.md e versione dello scenario di test nel file 01-start-session-acquisition/run_test.py (SCENARIO_VERSION)

## T1.2 - Riverifica 01-start-session-acquisition (rev. post-analisi 20260817 in T1.1)

- verifica-skill.cmd: spostare riga "--- Istruzioni per lo scenario ---" dopo la riga
  "Copiata skill Canale B corrente..."; aggiornare le istruzioni rimuovendo il passo
  manuale di esecuzione ContextBundler.exe (tailwatch/from-llm-watcher lo generano
  in automatico al download della context-request); "Quando hai finito il giro,
  esegui:" -> "Esegui:"; rimuovere le istruzioni di salvataggio manuale
  output/ZIP/script (già gestito in automatico da run_test.py)

- run_test.py:
  - riformulare le domande della checklist eliminando la logica negata
    ("L'LLM NON ha...")
  - rimuovere la domanda su uso corretto del context-out post-ricezione
    (lo scenario 01 si ferma alla generazione del context-out)
  - aggiungere controllo automatico (non a giudizio umano) in _common/validators.py:
    il file dichiarato in Target Paths è presente nel context-out con contenuto
    non vuoto
  - fail-fast: se un passo precedente ha richiesto intervento manuale dell'utente
    per funzionare correttamente, interrompere la sequenza di domande residue
    (logica scoped a questo scenario; valutare riuso in _common solo se semplice)

- report .md: riscrivere "## Dettagli" come elenco domanda -> risposta data
  dall'utente (non solo le domande fallite); la sezione "## Note" libera resta
  invariata per il contesto aggiuntivo dell'utente

- ripetere l'esecuzione dello scenario 01 con sonnet5 fino a esito soddisfacente
  per IK0VCK (incluso il path corretto nella context-request, sotto
  01-start-session-acquisition/testdir/, non "src/config.py")

- aggiornare Documentation/Changelog.md e SCENARIO_VERSION in
  01-start-session-acquisition/run_test.py
