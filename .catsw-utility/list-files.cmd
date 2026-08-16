@echo off
REM Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
REM Licensed under the MIT License. See LICENSE file in the project root for full license information.
REM Version 1.1

cls
echo ===================================
echo  List Files - Selezione Modalita
echo ===================================
echo  1) TurboAi-Tools
echo  2) ContextBundler
echo ===================================
echo.
set /p CHOICE="Seleziona un'opzione [1-2]: "

if "%CHOICE%"=="1" set TARGET_MODE=TurboAi-Tools
if "%CHOICE%"=="2" set TARGET_MODE=ContextBundler

if not defined TARGET_MODE (
    echo.
    echo Opzione non valida.
    pause
    exit /b 1
)

pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0artifacts\list-files.ps1" -Mode %TARGET_MODE%

if errorlevel 1 pause