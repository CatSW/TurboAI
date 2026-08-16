@echo off
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cls
echo ===============================================
echo   Skill Verification - TurboAI
echo ===============================================
echo.
echo Scenari disponibili:
echo   1  Acquisizione start-session
echo   2  Discovery mirata poi context-request
echo   3  File gia' dichiarati, context-request diretta
echo   4  Gap nel context-out, follow-up mirato
echo   5  Consegna ZIP FromLlm
echo   6  Consegna script standalone
echo   7  Triage errore da ToLlm.txt e patch
echo.
set /p SCELTA=Scegli uno scenario [1-7]:

if "%SCELTA%"=="1" set DIR=01-start-session-acquisition
if "%SCELTA%"=="2" set DIR=02-discovery-then-request
if "%SCELTA%"=="3" set DIR=03-declared-files-request
if "%SCELTA%"=="4" set DIR=04-context-out-gap-followup
if "%SCELTA%"=="5" set DIR=05-zip-delivery-sanity
if "%SCELTA%"=="6" set DIR=06-single-script-delivery
if "%SCELTA%"=="7" set DIR=07-tolm-error-triage-patch

if not defined DIR (
  echo Scelta non valida.
  goto FINE
)

echo.
echo --- Istruzioni per lo scenario %DIR% ---
python "%DIR%\run_test.py" setup

echo.
echo Segui le istruzioni sopra: allega i file indicati alla chat LLM,
echo esegui il prompt suggerito, poi salva l'output/lo ZIP/lo script
echo consegnato dall'LLM dentro la cartella "%DIR%".
echo.
pause

set /p LLMNAME=Nome/versione LLM testato (es. grok, gpt5.6, claude-sonnet-5):
set /p OUTFILE=Percorso del file salvato (output/zip/script):

echo.
echo --- Esecuzione verifica ---
if "%SCELTA%"=="5" (
  python "%DIR%\run_test.py" verify --llm "%LLMNAME%" --zip "%OUTFILE%"
) else if "%SCELTA%"=="7" (
  python "%DIR%\run_test.py" verify --llm "%LLMNAME%" --zip "%OUTFILE%"
) else if "%SCELTA%"=="6" (
  python "%DIR%\run_test.py" verify --llm "%LLMNAME%" --script "%OUTFILE%"
) else if "%SCELTA%"=="1" (
  python "%DIR%\run_test.py" verify --llm "%LLMNAME%"
) else (
  python "%DIR%\run_test.py" verify --llm "%LLMNAME%" --output "%OUTFILE%"
)

:FINE
echo.
echo Premi Invio o ESC 😄
pause >nul
