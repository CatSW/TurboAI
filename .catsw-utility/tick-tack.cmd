@echo off
REM Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
REM Licensed under the MIT License. See LICENSE file in the project root for full license information.
REM Version 1.2
setlocal enabledelayedexpansion

set "SRC_FILE=%USERPROFILE%\Downloads\ToLlm.txt"
set "DEST_DIR=%~dp0"

if not exist "%SRC_FILE%" exit /b 1

for /f "usebackq delims=" %%I in (`python -c "from datetime import datetime; print(datetime.now().strftime('%%Y%%m%%d-%%H%%M%%S'))"`) do set "TIMESTAMP=%%I"

copy /Y "%SRC_FILE%" "%DEST_DIR%%TIMESTAMP%-ToLlm.txt" >nul
endlocal