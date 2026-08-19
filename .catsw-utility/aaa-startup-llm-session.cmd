@echo off
REM Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
REM Licensed under the MIT License. See LICENSE file in the project root for full license information.
REM Version 1.5
REM
REM Changelog 1.5:
REM - rinominati tw.cmd e tw.py in tail-watch.cmd/py
REM
REM Changelog 1.4:
REM - Aggiunta verifica del file .catsw-utility\docs\skill-uso-tools.md.
REM   Se assente, viene invocato switch-skill.cmd prima di continuare.
REM
REM Changelog 1.3:
REM - ToLlm.txt viene sempre azzerato e riscritto a ogni avvio di nuova
REM   sessione.

setlocal
chcp 65001 >nul
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

REM Controllo presenza della skill tools; se manca, invoca switch-skill.cmd
if not exist "%~dp0docs\skill-uso-tools.md" (
    if exist "%~dp0switch-skill.cmd" (
    	echo [WARNING] File skill-uso-tools.md assente - Selezionare una Skill.
    	timeout /t 3
        call "%~dp0switch-skill.cmd"
        if errorlevel 1 (
            echo [ERROR] Selezione della skill annullata o non completata. Impossibile proseguire.
            timeout /t 5 >nul
            endlocal
            exit /b 1
        )
    ) else (
        echo [WARNING] File skill-uso-tools.md assente e switch-skill.cmd non trovato.
    )
)

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

REM Verifica e avvia tail-watch se non è già in esecuzione
powershell -NoProfile -Command "if (Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object {$_.CommandLine -like '*tail-watch.py*'}) { exit 0 } else { exit 1 }" >nul 2>&1
if errorlevel 1 (
    if exist "%~dp0tail-watch.cmd" (
        call "%~dp0tail-watch.cmd"
        set "TailWatchActiveted=true"
    )
)

cd /d "%~dp0artifacts" 2>nul || cd /d "%~dp0artifacts"
python startup-llm-session.py
set "ExitCode=%ERRORLEVEL%"
echo.

REM Estraggo la versione da Readme.md (campo versione-turbo-ai:)
set "TURBO_VER=unknown"
for /f "tokens=2 delims=:" %%A in ('findstr /I /C:"versione-turbo-ai:" "%~dp0Readme.md" 2^>nul') do (
    for /f "tokens=*" %%B in ("%%A") do set "TURBO_VER=%%~B"
)

REM Scrittura immediata di ToLlm.txt all'avvio
if not defined TailWatchActiveted goto :SkipToLlm
    >> "%USERPROFILE%\Downloads\ToLlm.txt" echo .
    >> "%USERPROFILE%\Downloads\ToLlm.txt" echo -----------------------------------------------------------------------
    >> "%USERPROFILE%\Downloads\ToLlm.txt" echo Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
    >> "%USERPROFILE%\Downloads\ToLlm.txt" echo TurboAI %TURBO_VER%
    >> "%USERPROFILE%\Downloads\ToLlm.txt" echo READY :)
:SkipToLlm

timeout /t 10

endlocal
exit /b %ExitCode%