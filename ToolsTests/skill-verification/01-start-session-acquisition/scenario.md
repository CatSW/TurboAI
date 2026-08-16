# Scenario 01 - Acquisizione start-session

## Obiettivo
Verificare che l'LLM, ricevuto un bundle di avvio sessione (governance +
next_task + info git), capisca senza ambiguita' qual e' il task da
eseguire e sia pronto a iniziare senza richiedere materiale gia' fornito.

## Materiale fornito (golden/)
- SOLUTION_GOVERNANCE.md (solution fittizia "DemoWidget")
- info_next_task.md (task T1.1, mirato e con Target Paths dichiarati)
- info_git.txt (log/status fittizi)

## Prompt suggerito
Allega la tua skill Canale B + i tre file in golden/, poi scrivi:
"Questo e' il bundle di avvio sessione per DemoWidget. Procedi come da
protocollo di sessione."

## Criteri di successo (giudizio umano, checklist guidata da run_test.py verify)
1. L'LLM identifica correttamente il task corrente (T1.1) senza chiedere
   di ripeterlo.
2. L'LLM non richiede file gia' presenti nel bundle (governance, next_task, git).
3. L'LLM non inventa file/percorsi assenti dal bundle.
4. L'LLM propone correttamente il prossimo passo operativo (es. richiesta
   dei file dichiarati in Target Paths) invece di restare generico.

## Nota
Questo scenario valuta comprensione semantica: non e' automatizzabile al
100%. `run_test.py verify` guida una checklist interattiva e scrive comunque
un report con nome-LLM per il confronto storico/non-regressione.
