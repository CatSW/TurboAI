@echo off
REM Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
REM Licensed under the MIT License. See LICENSE file in the project root for full license information.
REM unbundler.cmd – wrapper Windows per unbundler.py
REM Version 1.1
setlocal EnableExtensions
cd /d "%~dp0"

set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

python "%~dp0artifacts\unbundler.py" %*
set "EC=%ERRORLEVEL%"
if not "%EC%"=="0" (
  echo.
  echo [ERRORE] Unbundler terminato con codice %EC%
  pause
  exit /b %EC%
)
exit /b 0
