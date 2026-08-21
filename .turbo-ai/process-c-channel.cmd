@echo off
REM Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
REM Licensed under the MIT License. See LICENSE file in the project root for full license information.
REM Version 1.1

setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

cd /d "%~dp0"

echo.
echo === process-c-channel v1.0 ===
echo Working dir: %CD%
echo.

REM --- 1. Purga output ---
if not exist "%~dp0purga-output.cmd" (
    echo ERRORE: purga-output.cmd non trovato in %CD%
    goto :FAIL
)
echo [1/3] Chiamo purga-output.cmd ...
call "%~dp0purga-output.cmd"
if errorlevel 1 (
    echo ERRORE: purga-output.cmd ha restituito errore.
    goto :FAIL
)
echo.

REM --- 2. Genera ZIP ---
if not exist "%~dp0genera-zip.cmd" (
    echo ERRORE: genera-zip.cmd non trovato in %CD%
    goto :FAIL
)
echo [2/3] Chiamo genera-zip.cmd ...
call "%~dp0genera-zip.cmd"
if errorlevel 1 (
    echo ERRORE: genera-zip.cmd ha restituito errore.
    goto :FAIL
)
echo.

REM --- 3. Sposta lo ZIP da output\ a Downloads ---
REM     (dopo purga + genera-zip c'e' al massimo un FromLlm-*.zip)
set "OUTDIR=%~dp0output"
if not exist "%OUTDIR%" (
    echo ERRORE: cartella output non trovata: %OUTDIR%
    goto :FAIL
)

set "ZIPFILE="
for %%F in ("%OUTDIR%\FromLlm-*.zip") do (
    set "ZIPFILE=%%~fF"
    set "ZIPNAME=%%~nxF"
)

if not defined ZIPFILE (
    echo ERRORE: nessun FromLlm-*.zip trovato in output\
    goto :FAIL
)

set "DEST=%USERPROFILE%\Downloads\%ZIPNAME%"
echo [3/3] Sposto "%ZIPNAME%" in Downloads ...
move /Y "%ZIPFILE%" "%DEST%" >nul
if errorlevel 1 (
    echo ERRORE: impossibile spostare lo ZIP in Downloads.
    goto :FAIL
)

echo.
echo === Completato ===
echo ZIP spostato in: %DEST%
echo Il watcher dovrebbe prenderlo in carico.
echo.
goto :EOF

:FAIL
echo.
echo === FALLITO ===
echo.
exit /b 1

