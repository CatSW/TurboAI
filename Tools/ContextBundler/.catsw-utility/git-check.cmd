@echo off
REM Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
REM Licensed under the MIT License. See LICENSE file in the project root for full license information.
REM Version 1.1

setlocal

rem Imposta UTF-8 per visualizzare correttamente l'emoji
chcp 65001 >nul

rem Verifica se il working tree contiene modifiche
set "WorkingTreeDirty="

for /f "delims=" %%G in ('git -C .. status --short') do (
    set "WorkingTreeDirty=1"
)

if defined WorkingTreeDirty (
    echo git -C .. status --short
    git -C .. status --short
) else (
    powershell.exe -NoProfile -Command ^
        "Write-Host 'Working Tree Clean' -ForegroundColor Green"
)

echo.
echo git -C .. log -2 --oneline
git -C .. log -2 --oneline

echo.
echo Premere Invio o Esc 😀
pause

endlocal