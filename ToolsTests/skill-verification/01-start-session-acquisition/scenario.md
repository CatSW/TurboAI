# Scenario 01 - Acquisizione start-session

## Obiettivo
Verificare che l'LLM, ricevuto un bundle di avvio sessione (governance +
piano/next-task + info git), capisca senza ambiguita' qual e' il task da
eseguire, sia pronto a iniziare senza richiedere materiale gia' fornito,
e sappia proseguire correttamente fino alla vera acquisizione dei file
mancanti tramite context-request/context-out.

## Materiale fornito (testdir/.ai-context/)
- SOLUTION_GOVERNANCE.md (solution fittizia "DemoWidget", TurboAiWorkingRoot
  = testdir stesso — root fisica isolata con la propria .turbo-ai)
- Piano-Multi-Task.md (contiene il blocco `<next_task>` T1.1, mirato e con
  Target Paths dichiarati relativi a testdir)
- info_git.txt (log/status fittizi)

## Prompt suggerito
Allega la tua skill Canale B + i file in testdir/.ai-context/, poi scrivi:
"Questo e' il bundle di avvio sessione per DemoWidget. Procedi come da
protocollo di sessione."

## Procedura (aggiornata: richiede un giro reale di ContextBundler)
0. Apri una finestra IN INCOGNITO/PRIVATA della chat LLM sotto test, per non
   alterare i risultati con la history di sessioni precedenti.
1. Attacca i file di testdir/.ai-context/ + skill Canale B in quella chat
   pulita e invia il prompt suggerito.
2. L'LLM deve proporre come prossimo passo la richiesta dei file dichiarati
   in Target Paths sotto forma di context-request-*.md scaricabile.
3. Scarica quel file: from-llm-watcher rileva il download e genera in
   automatico il context-out corrispondente (non serve piu' eseguire
   ContextBundler.exe a mano).
4. Incolla/allega il context-out nella stessa chat e osserva la risposta
   finale dell'LLM.
5. Esegui `run_test.py verify` passando entrambi i file: verranno copiati
   nella cartella di report per tracciabilita' e la context-request verra'
   validata automaticamente nel formato (niente prosa, niente wildcard).

## Criteri di successo (giudizio umano + controllo automatico di formato)
1. L'LLM identifica correttamente il task corrente (T1.1) senza chiedere
   di ripeterlo.
2. L'LLM non richiede file gia' presenti nel bundle (governance, piano, git).
3. L'LLM non inventa file/percorsi assenti dal bundle.
4. L'LLM propone correttamente il prossimo passo operativo generando una
   context-request-*.md ben formata (verificato anche automaticamente).
5. Dopo aver ricevuto il context-out reale, l'LLM lo usa correttamente
   (nessuna invenzione, nessuna richiesta di file gia' presenti nel
   context-out).

## Nota
Questo scenario valuta comprensione semantica: non e' automatizzabile al
100%. `run_test.py verify` guida una checklist interattiva, valida
automaticamente il formato della context-request generata, copia
context-request e context-out nella cartella di report e registra
versione dello scenario, di TurboAI e della skill Canale B usata, per il
confronto storico/non-regressione.
