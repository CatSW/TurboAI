@echo off
REM Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
REM Licensed under the MIT License. See LICENSE file in the project root for full license information.
REM genera-zip.cmd – unbundle + crea FromLlm-<descrizione>.zip in output\
REM Version.1.0
setlocal EnableExtensions
cd /d "%~dp0"

set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

python "%~dp0artifacts\genera_zip.py" %*
set "EC=%ERRORLEVEL%"
if not "%EC%"=="0" (
  echo.
  echo [ERRORE] GeneraZip terminato con codice %EC%
  pause
  exit /b %EC%
)
echo.
echo ZIP pronto in: %~dp0output\
exit /b 0
