@echo off
rem ===========================================================================
rem from-llm-watcher.cmd
rem Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
rem Version 1.0
rem
rem Avvia from-llm-watcher.py all'interno di Windows Terminal (wt.exe)
rem specificando posizione e dimensioni della finestra.
rem ===========================================================================

setlocal

rem Cartella artifacts dove risiede lo script Python
set "SCRIPT_DIR=%~dp0artifacts"
set "PYTHON_SCRIPT=%SCRIPT_DIR%\from-llm-watcher.py"

rem Parametri di posizionamento e dimensione per Windows Terminal
set "WT_POS=2695,700"
set "WT_SIZE=110,28"

rem Verifica presenza di Windows Terminal (wt.exe)
where wt.exe >nul 2>&1
if %ERRORLEVEL% equ 0 (
    rem Avvio tramite Windows Terminal con geometria e titolo corretti
    start "" wt.exe --pos %WT_POS% --size %WT_SIZE% --title "from-llm-watcher" cmd.exe /k "python \"%PYTHON_SCRIPT%\""
) else (
    rem Fallback su console classica (cmd.exe) se wt.exe non è disponibile
    start "from-llm-watcher" cmd.exe /k "python \"%PYTHON_SCRIPT%\""
)

endlocal