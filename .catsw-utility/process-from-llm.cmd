@echo off
REM Copyright (c) 2026 Stefano Vesco (IK0VCK) - CatSW. All rights reserved.
REM Licensed under the MIT License. See LICENSE file in the project root for full license information.
REM Version 1.0
REM Unified orchestrator stub: replaces context-bundler.cmd + process-zip-and-scripts-from-llm.cmd

py "%~dp0artifacts\process-from-llm.py"
set "ExitCode=%ERRORLEVEL%"
echo.
timeout /t 20
exit /b %ExitCode%
