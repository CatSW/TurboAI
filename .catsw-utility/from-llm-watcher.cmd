@echo off
rem from-llm-watcher.cmd
rem Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
rem Version 1.2

setlocal
chcp 65001 >nul
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

rem Cartella artifacts dove risiede lo script Python
set "BASE_DIR=%~dp0"
set "SCRIPT_DIR=%BASE_DIR%artifacts"
set "PYTHON_SCRIPT=%SCRIPT_DIR%\from-llm-watcher.py"
set "GET_POS_SCRIPT=%SCRIPT_DIR%\get-win-pos.ps1"
set "CONFIG_FILE=%BASE_DIR%from-llm-watcher.json"

rem Parametri di posizionamento e dimensione per Windows Terminal (default)
set "WT_POS=2695,700"
set "WT_SIZE=110,28"

rem Se from-llm-watcher.json non esiste, invoca get-win-pos.ps1 per crearla
if not exist "%CONFIG_FILE%" (
    if exist "%GET_POS_SCRIPT%" (
        powershell -ExecutionPolicy Bypass -File "%GET_POS_SCRIPT%" "%CONFIG_FILE%"
    ) else (
        echo AVVISO: Impossibile generare la configurazione. Script non trovato:
        echo   %GET_POS_SCRIPT%
    )
)

rem Se presente from-llm-watcher.json, estrae la configurazione tramite Python inline
if exist "%CONFIG_FILE%" (
    for /f "tokens=1-4" %%A in ('python -c "import json, sys; j=json.load(open(sys.argv[1], encoding='utf-8-sig')); print(j.get('x-win-pos', 2695), j.get('y-win-pos', 700), j.get('width', 110), j.get('height', 28))" "%CONFIG_FILE%" 2^>nul') do (
        set "WT_POS=%%A,%%B"
        set "WT_SIZE=%%C,%%D"
    )
)

rem Controlli preventivi
if not exist "%PYTHON_SCRIPT%" (
    echo ERRORE: non trovo lo script Python:
    echo   %PYTHON_SCRIPT%
    pause
    exit /b 1
)

rem Verifica presenza di Windows Terminal (wt.exe)
where wt.exe >nul 2>&1
if %ERRORLEVEL% equ 0 (
    rem Avvio tramite Windows Terminal con geometria e titolo corretti
    start "" wt.exe --pos %WT_POS% --size %WT_SIZE% --title "TurboAI" --suppressApplicationTitle cmd.exe /k "python \"%PYTHON_SCRIPT%\""
) else (
    rem Fallback su console classica (cmd.exe) se wt.exe non è disponibile
    start "from-llm-watcher" cmd.exe /k "python \"%PYTHON_SCRIPT%\""
)

endlocal
