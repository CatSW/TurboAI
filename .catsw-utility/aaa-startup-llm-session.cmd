@echo off
REM Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
REM Licensed under the MIT License. See LICENSE file in the project root for full license information.
REM Version 1.1

setlocal
chcp 65001 >nul
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

REM Verifica e avvia from-llm-watcher se non è già in esecuzione
powershell -NoProfile -Command "if (Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object {$_.CommandLine -like '*from-llm-watcher.py*'}) { exit 0 } else { exit 1 }" >nul 2>&1
if errorlevel 1 (
    if exist "%~dp0from-llm-watcher.cmd" (
        call "%~dp0from-llm-watcher.cmd"
    )
)

REM Verifica la presenza del file ToLlm.txt in Download
if not exist "%USERPROFILE%\Downloads\ToLlm.txt" (
	type null > "%USERPROFILE%\Downloads\ToLlm.txt"
)

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
