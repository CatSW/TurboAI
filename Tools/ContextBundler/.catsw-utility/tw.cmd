@echo off
REM Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
REM Licensed under the MIT License. See LICENSE file in the project root for full license information.
REM Version 1.0

setlocal

rem Cartella dove risiede questo .cmd
set "BASE_DIR=%~dp0"
set "SCRIPT_DIR=%BASE_DIR%artifacts"
set "PYTHON_SCRIPT=%SCRIPT_DIR%\tw.py"

rem ToLlm.txt sta sempre in Downloads dell'utente corrente
set "TARGET_FILE=%USERPROFILE%\Downloads\ToLlm.txt"

rem Parametri di posizionamento e dimensione per Windows Terminal
set "WT_POS=2695,10"
set "WT_SIZE=110,28"

rem Controlli preventivi
if not exist "%PYTHON_SCRIPT%" (
    echo ERRORE: non trovo lo script Python:
    echo   %PYTHON_SCRIPT%
    pause
    exit /b 1
)

if not exist "%TARGET_FILE%" (
    echo ERRORE: non trovo il file da monitorare:
    echo   %TARGET_FILE%
    echo.
    echo Crealo o verifica che sia in Downloads.
    pause
    exit /b 1
)

rem Verifica presenza di Windows Terminal (wt.exe)
where wt.exe >nul 2>&1
if %ERRORLEVEL% equ 0 (
    start "" wt.exe --pos %WT_POS% --size %WT_SIZE% --title "tw" cmd.exe /k "python \"%PYTHON_SCRIPT%\" \"%TARGET_FILE%\""
) else (
    start "tw" cmd.exe /k "python \"%PYTHON_SCRIPT%\" \"%TARGET_FILE%\""
)