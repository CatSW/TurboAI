@echo off
REM Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
REM Licensed under the MIT License. See LICENSE file in the project root for full license information.
REM Version 1.3

setlocal
chcp 65001 >nul
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

rem Cartella dove risiede questo .cmd
set "BASE_DIR=%~dp0"
set "SCRIPT_DIR=%BASE_DIR%artifacts"
set "PYTHON_SCRIPT=%SCRIPT_DIR%\tail-watch.py"
set "GET_POS_SCRIPT=%SCRIPT_DIR%\get-win-pos.ps1"
set "CONFIG_FILE=%BASE_DIR%tail-watch.json"

rem ToLlm.txt sta sempre in Downloads dell'utente corrente
set "TARGET_FILE=%USERPROFILE%\Downloads\ToLlm.txt"

rem Parametri di posizionamento e dimensione per Windows Terminal (default sfalsato)
set "WT_POS=150,150"
set "WT_SIZE=110,28"

rem Se tail-watch.json non esiste, invoca get-win-pos.ps1 per crearla con offset sfalsato (100, 100)
if not exist "%CONFIG_FILE%" (
    if exist "%GET_POS_SCRIPT%" (
        powershell -ExecutionPolicy Bypass -File "%GET_POS_SCRIPT%" "%CONFIG_FILE%" 100 100
    ) else (
        echo AVVISO: Impossibile generare la configurazione. Script non trovato:
        echo   %GET_POS_SCRIPT%
    )
)

rem Se presente tail-watch.json, estrae la configurazione tramite Python inline (con gestione utf-8-sig per il BOM)
if exist "%CONFIG_FILE%" (
    for /f "tokens=1-4" %%A in ('python -c "import json, sys; j=json.load(open(sys.argv[1], encoding='utf-8-sig')); print(j.get('x-win-pos', 150), j.get('y-win-pos', 150), j.get('width', 110), j.get('height', 28))" "%CONFIG_FILE%" 2^>nul') do (
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

if not exist "%TARGET_FILE%" (
    type nul > "%TARGET_FILE%"
)

rem Verifica presenza di Windows Terminal (wt.exe)
where wt.exe >nul 2>&1
if %ERRORLEVEL% equ 0 (
    start "" wt.exe --pos %WT_POS% --size %WT_SIZE% --title "TurboAI" --suppressApplicationTitle cmd.exe /k "python "%PYTHON_SCRIPT%" "%TARGET_FILE%""
) else (
    start "tail-watch" cmd.exe /k "python "%PYTHON_SCRIPT%" "%TARGET_FILE%""
)
