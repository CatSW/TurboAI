# Piano-Multi-Task — skill-verification: verify & fix scenarios

## Obiettivo
Verificare e correggere tutti gli harness degli scenari sotto ToolsTests/skill-verification ora che
.catsw-utility è stato installato localmente in questa cartella (TurboAiWorkingRoot corretto
in C:/Repo/CatSW/TurboAI/ToolsTests/skill-verification).

## Scenari di test

- 01-start-session-acquisition
- 02-discovery-then-request
- 03-declared-files-request
- 4-context-out-gap-followup
- 05-zip-delivery-sanity
- 06-single-script-delivery
- 07-tolm-error-triage-patch

## Milestone M0 - Iniziale 

- esecuzione iniziale dello scenario 01-start-session-acquisition per testare il sistema

## T0.1 - 01-start-session-acquisition: causa radice diagnosticata [COMPLETATO, 16-08-2026]
L'esecuzione di sonnet5 è FALLITA: context-out non includeva il file richiesto (src/config.py),
TurboAiWorkingRoot nel bundle non corrispondeva allo scenario (DemoWidget), git log/status
facevano riferimento a TurboAI/skill-verification anziché a DemoWidget.
Causa radice: .catsw-utility mancava sotto skill-verification, quindi lo strumento veniva eseguito rispetto
alla radice errata. Trovato anche: context-request-config-py.md conteneva una riga di testo libero
("T1.1 - Rename a stale constant") non prefissata con `#`.
Correzione applicata dall'utente: .catsw-utility copiato all'interno di skill-verification.

## Milestone M1 - Miglioramento sistema di skill-verification

- usando lo scenario 01-start-session-acquisition bisogna affinare il sistema fino a quando IK0VCK lo ritiene soddisfacente

<next_task>
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
</next_task>

## Milestone M2 - Verifica scenario 02

## T2.1 - Verify 02-discovery-then-request

- lo scenario deve rispettare le migliorie apportate al sistema skill-verification da M1 adeguandolo con tutte le modifiche richieste
- se emergono nuove modifiche al sistema di skill-verification, deve essere fatta una verifica di conformità degli scenari precedenti (in questo caso solo lo 01)
- se scenari precedenti non risultano adeguati, aggiungere task in questa milestone per adeguarli e verificarli prima di passare alla prossima milestone
- aggiornare Documentation/Changelog.md e versione scenario di test nel file run_test.py (SCENARIO_VERSION)

## Milestone M3 - Verifica scenario 03

## T3.1 - Verify 03-declared-files-request

- lo scenario deve rispettare le migliorie apportate al sistema skill-verification nelle milestone precedenti adeguandolo con tutte le modifiche richieste
- aggiornare Documentation/Changelog.md e versione scenario di test nel file run_test.py (SCENARIO_VERSION)
- se emergono nuove modifiche al sistema di skill-verification, deve essere fatta una verifica di conformità degli scenari precedenti 
- se scenari precedenti non risultano adeguati, aggiungere task in questa milestone per adeguarli e verificarli prima di passare alla prossima milestone

## Milestone M4 - Verifica scenario 04

## T4.1 - Verify 04-context-out-gap-followup

- lo scenario deve rispettare le migliorie apportate al sistema skill-verification nelle milestone precedenti adeguandolo con tutte le modifiche richieste
- aggiornare Documentation/Changelog.md e versione scenario di test nel file run_test.py (SCENARIO_VERSION)
- se emergono nuove modifiche al sistema di skill-verification, deve essere fatta una verifica di conformità degli scenari precedenti 
- se scenari precedenti non risultano adeguati, aggiungere task in questa milestone per adeguarli e verificarli prima di passare alla prossima milestone

## Milestone M5 - Verifica scenario 05

## T5.1 - Verify 05-zip-delivery-sanity

- lo scenario deve rispettare le migliorie apportate al sistema skill-verification nelle milestone precedenti adeguandolo con tutte le modifiche richieste
- aggiornare Documentation/Changelog.md e versione scenario di test nel file run_test.py (SCENARIO_VERSION)
- se emergono nuove modifiche al sistema di skill-verification, deve essere fatta una verifica di conformità degli scenari precedenti 
- se scenari precedenti non risultano adeguati, aggiungere task in questa milestone per adeguarli e verificarli prima di passare alla prossima milestone

## Milestone M6 - Verifica scenario 06

## T6.1 - Verify 06-single-script-delivery

- lo scenario deve rispettare le migliorie apportate al sistema skill-verification nelle milestone precedenti adeguandolo con tutte le modifiche richieste
- aggiornare Documentation/Changelog.md e versione scenario di test nel file run_test.py (SCENARIO_VERSION)
- se emergono nuove modifiche al sistema di skill-verification, deve essere fatta una verifica di conformità degli scenari precedenti 
- se scenari precedenti non risultano adeguati, aggiungere task in questa milestone per adeguarli e verificarli prima di passare alla prossima milestone

## Milestone M7 - Verifica scenario 07

## T7.1 - Verify 07-tolm-error-triage-patch

- lo scenario deve rispettare le migliorie apportate al sistema skill-verification nelle milestone precedenti adeguandolo con tutte le modifiche richieste
- aggiornare Documentation/Changelog.md e versione scenario di test nel file run_test.py (SCENARIO_VERSION)
- se emergono nuove modifiche al sistema di skill-verification, deve essere fatta una verifica di conformità degli scenari precedenti 
- se scenari precedenti non risultano adeguati, aggiungere task in questa milestone per adeguarli e verificarli prima di passare alla prossima milestone