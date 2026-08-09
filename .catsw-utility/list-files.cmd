@echo off
REM Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
REM Licensed under the MIT License. See LICENSE file in the project root for full license information.
REM Version 1.0
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0artifacts\list-files.ps1"

if errorlevel 1 pause
