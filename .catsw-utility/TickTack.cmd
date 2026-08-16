@echo off
REM Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
REM Licensed under the MIT License. See LICENSE file in the project root for full license information.
REM Version 1.1
setlocal enabledelayedexpansion

:: 1. Impostazione percorsi e nomi file
set "DOWNLOADS_DIR=%USERPROFILE%\Downloads"
set "SRC_FILE=%DOWNLOADS_DIR%\ToLlm.txt"
set "DEST_DIR=%~dp0"

:: 2. Verifica presenza del file sorgente in Downloads
if not exist "%SRC_FILE%" (
    echo "[ERRORE] File sorgente non trovato in: %SRC_FILE%"
    pause
    exit /b
)

:: 3. Generazione del timestamp nel formato YYYYMMDD-HHMMSS
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set "dt=%%I"
set "YYYY=%dt:~0,4%"
set "MM=%dt:~4,2%"
set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%"
set "Min=%dt:~10,2%"
set "Sec=%dt:~12,2%"
set "TIMESTAMP=%YYYY%%MM%%DD%-%HH%%Min%%Sec%"

:: 4. Copia del file con il nuovo nome timestamped
set "DEST_FILE=%DEST_DIR%%TIMESTAMP%-ToLlm.txt"
copy /Y "%SRC_FILE%" "%DEST_FILE%" >nul

echo "Copiato con successo: %TIMESTAMP%-ToLlm.txt"

endlocal