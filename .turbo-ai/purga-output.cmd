@echo off
REM Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
REM Licensed under the MIT License. See LICENSE file in the project root for full license information.
REM Version 1.2
setlocal EnableExtensions
set "TARGET=%~dp0output"

if not exist "%TARGET%\" (
  echo [INFO] Cartella output non esiste: "%TARGET%"
  exit /b 0
)

python -c "import shutil, pathlib, sys; p=pathlib.Path(r'%TARGET%'); [shutil.rmtree(c) if c.is_dir() else c.unlink() for c in p.iterdir()]; print('[OK] Contenuto di output svuotato.')"
set "EC=%ERRORLEVEL%"
if not "%EC%"=="0" (
  echo [ERRORE] Purga fallita con codice %EC%
  exit /b %EC%
)
exit /b 0

