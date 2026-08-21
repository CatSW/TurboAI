@echo off
REM Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
REM Licensed under the MIT License. See LICENSE file in the project root for full license information.
REM Version 1.4
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

REM --- Determina quale .turbo-ai usare per questo scenario ---------
REM Se lo scenario ha una .turbo-ai isolata dentro DIR\testdir (root
REM fisica = TurboAiWorkingRoot narrato nel bundle), usa quella. Altrimenti
REM ricade su quella condivisa a livello di skill-verification.
set "CATSW=%~dp0.turbo-ai"
if exist "%~dp0%DIR%\testdir\.turbo-ai\from-llm-watcher.cmd" (
    set "CATSW=%~dp0%DIR%\testdir\.turbo-ai"
)
echo.
echo .turbo-ai usata per questo scenario: %CATSW%
echo.

REM --- Ferma eventuali istanze attive e riavvia con la root corretta ----
call :StopIfRunning "from-llm-watcher.py"
call :StopIfRunning "tw.py"

if exist "%CATSW%\from-llm-watcher.cmd" (
    start "" /b cmd /c "%CATSW%\from-llm-watcher.cmd"
) else (
    echo ATTENZIONE: %CATSW%\from-llm-watcher.cmd non trovato, avvialo manualmente.
)
if exist "%CATSW%\tw.cmd" (
    start "" /b cmd /c "%CATSW%\tw.cmd"
) else (
    echo ATTENZIONE: %CATSW%\tw.cmd non trovato, avvialo manualmente.
)

REM Verifica la presenza del file ToLlm.txt in Download
if not exist "%USERPROFILE%\Downloads\ToLlm.txt" (
	type nul > "%USERPROFILE%\Downloads\ToLlm.txt"
)

echo.
echo ***************************************************************
echo * Apri una finestra IN INCOGNITO/PRIVATA della chat LLM sotto  *
echo * test, per non alterare i risultati con la history di sessioni*
echo * precedenti.                                                  *
echo ***************************************************************
echo.

python "%DIR%\run_test.py" setup

echo.
if "%SCELTA%"=="1" (
  echo Segui le istruzioni sopra, poi premi Invio per eseguire la verifica.
) else (
  echo Segui le istruzioni sopra: allega i file indicati alla chat LLM,
  echo esegui il prompt suggerito, poi salva l'output/lo ZIP/lo script
  echo consegnato dall'LLM dentro la cartella "%DIR%".
)
echo.
pause

set /p LLMNAME=Nome/versione LLM testato (es. grok, gpt5.6, claude-sonnet-5):

if not "%SCELTA%"=="1" set /p OUTFILE=Percorso del file salvato (output/zip/script):

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

goto FINE

:StopIfRunning
REM %~1 = nome dello script python da cercare/terminare (es. "tw.py")
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object {$_.CommandLine -like '*%~1*'} | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }" >nul 2>&1
goto :eof

:FINE
echo.
echo Premi Invio o ESC 😄
pause >nul
