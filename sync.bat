@echo off
setlocal enabledelayedexpansion

set SOURCE=D:\devflow\.ai
set TARGET=D:\aprojects\rma-backend\.ai

echo Syncing .ai folder...
echo Source: %SOURCE%
echo Target: %TARGET%
echo.

if not exist "%SOURCE%" (
    echo ERROR: Source not found: %SOURCE%
    pause
    exit /b 1
)

if not exist "%TARGET%\" (
    mkdir "%TARGET%"
)

robocopy "%SOURCE%" "%TARGET%" /MIR /XD ".git" "__pycache__" ".local" /XF "*.pyc" "*.tmp" /NP /NDL /NJH /NJS

if errorlevel 8 (
    echo ERROR: Copy failed
    pause
    exit /b 1
)

echo.
echo ✅ Sync complete: %SOURCE% -^> %TARGET%
pause
