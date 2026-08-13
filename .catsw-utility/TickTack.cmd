@echo off
REM Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
REM Licensed under the MIT License. See LICENSE file in the project root for full license information.
REM Version 1.0
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

:: 3. Cancellazione di eventuali vecchi file ToLlm_*.txt presenti nella cartella
if exist "%DEST_DIR%ToLlm_*.txt" (
    echo "Rimozione vecchio file ToLlm_*.txt in corso..."
    del /q "%DEST_DIR%ToLlm_*.txt"
)

:: 4. Generazione del timestamp nel formato HHMMSS (es. 143015)
set "TM=%TIME: =0%"
set "TIMESTAMP=%TM:~0,2%%TM:~3,2%%TM:~6,2%"

:: 5. Copia del file con il nuovo suffisso
set "DEST_FILE=%DEST_DIR%ToLlm_%TIMESTAMP%.txt"
copy /Y "%SRC_FILE%" "%DEST_FILE%" >nul

echo "Copiato con successo: ToLlm_%TIMESTAMP%.txt"

endlocal