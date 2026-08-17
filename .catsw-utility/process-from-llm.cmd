@echo off
REM Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
REM Licensed under the MIT License. See LICENSE file in the project root for full license information.
REM Version 1.2
REM Unified orchestrator stub: replaces context-bundler.cmd + process-zip-and-scripts-from-llm.cmd
chcp 65001 >nul
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

REM cleanup dei file context-* e FromLlm-*
call "%~dp0move-to-history.cmd"

py "%~dp0artifacts\process-from-llm.py"
set "ExitCode=%ERRORLEVEL%"
echo.

REM questo serve per quelle chat llm che cachano il file ToLlm.txt e se gle lo si riallegano 
REM non vedono il nuovo file. Alternando il nome si evita il problema.
call "%~dp0tick-tack.cmd"

timeout /t 20
exit /b %ExitCode%
