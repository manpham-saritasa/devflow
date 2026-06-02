@echo off
setlocal enabledelayedexpansion

set SOURCE=D:\devflow\.ai
set ERROR_COUNT=0

:: ── Edit these paths ──────────────────────────────────────
set TARGETS[0]=D:\aprojects\rma-backend\.ai
set TARGETS[1]=D:\aprojects\other-project\.ai
:: ──────────────────────────────────────────────────────────

echo Syncing .ai folder to %TARGETS_COUNT% projects...
echo Source: %SOURCE%
echo.

if not exist "%SOURCE%" (
    echo ERROR: Source not found: %SOURCE%
    pause
    exit /b 1
)

set INDEX=0
:loop
    call set TARGET=%%TARGETS[%INDEX%]%%
    if "!TARGET!"=="" goto done

    echo ── !TARGET!
    if not exist "!TARGET!" (
        echo   SKIP: Target does not exist — run sync.bat first time to create
        set /a ERROR_COUNT+=1
        goto next
    )

    robocopy "%SOURCE%" "!TARGET!" /MIR /XD .git __pycache__ .local /XF *.pyc *.tmp /NP /NDL /NJH /NJS
    if errorlevel 8 (
        echo   FAIL
        set /a ERROR_COUNT+=1
    ) else (
        echo   OK
    )

:next
    set /a INDEX+=1
    goto loop

:done
echo.
if %ERROR_COUNT% GTR 0 (
    echo %ERROR_COUNT% target(s) failed or skipped
)
echo Done.
pause
