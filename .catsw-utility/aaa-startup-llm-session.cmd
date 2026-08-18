@echo off
REM Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
REM Licensed under the MIT License. See LICENSE file in the project root for full license information.
REM Version 1.3
REM
REM Changelog 1.3:
REM - ToLlm.txt viene sempre azzerato e riscritto a ogni avvio di nuova
REM   sessione (prima veniva creato solo "type null >" se assente, quindi
REM   restava con contenuto stantio di un run precedente e "type null" era
REM   comunque un bug: "null" non e' il device nul di Windows).
REM - Messaggio di reset scritto in ToLlm.txt: "TurboAI- new Session
REM   Started ... enjoy :)".

setlocal
chcp 65001 >nul
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

REM Rotazione preventiva iniziale (T6.3)
call "%~dp0move-to-history.cmd"
if errorlevel 1 (
    echo [WARNING] Rotazione history completata con avvisi o errori.
)

REM Verifica e avvia from-llm-watcher se non è già in esecuzione
powershell -NoProfile -Command "if (Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object {$_.CommandLine -like '*from-llm-watcher.py*'}) { exit 0 } else { exit 1 }" >nul 2>&1
if errorlevel 1 (
    if exist "%~dp0from-llm-watcher.cmd" (
        call "%~dp0from-llm-watcher.cmd"
    )
)

REM Reset di ToLlm.txt a ogni nuova sessione: evita contenuto stantio di
REM run precedenti (bug precedente: veniva creato solo se assente, e con
REM "type null" invece di "type nul").
> "%USERPROFILE%\Downloads\ToLlm.txt" echo TurboAI- new Session Started ... enjoy :)

REM Verifica e avvia tw se non è già in esecuzione
powershell -NoProfile -Command "if (Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object {$_.CommandLine -like '*tw.py*'}) { exit 0 } else { exit 1 }" >nul 2>&1
if errorlevel 1 (
    if exist "%~dp0tw.cmd" (
        call "%~dp0tw.cmd"
    )
)

cd /d "%~dp0artifacts" 2>nul || cd /d "%~dp0artifacts"
python startup-llm-session.py
set "ExitCode=%ERRORLEVEL%"
echo.
timeout /t 10

endlocal
exit /b %ExitCode%
