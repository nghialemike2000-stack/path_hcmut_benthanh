@echo off
setlocal EnableDelayedExpansion

:: =========================================================
:: Collect all Python files into save_python.txt
:: Includes:
::   - Full file path
::   - UTF-8 safe output
::   - Python filename
::   - Source code content
:: =========================================================

:: Output file
set OUTPUT=save_python.txt

:: Create UTF-8 BOM file
> "%OUTPUT%" (
    powershell -NoProfile -Command ^
    "[System.IO.File]::WriteAllText('%OUTPUT%', '', (New-Object System.Text.UTF8Encoding($true)))"
)

:: Search recursively for .py files
for /r %%F in (*.py) do (

    echo Processing: %%F

    >> "%OUTPUT%" echo ==================================================
    >> "%OUTPUT%" echo FILE: %%~nxF
    >> "%OUTPUT%" echo FULL PATH: %%~fF
    >> "%OUTPUT%" echo ==================================================
    >> "%OUTPUT%" echo.

    :: Read file safely with UTF-8 support
    powershell -NoProfile -Command ^
    "$content = Get-Content -LiteralPath '%%~fF' -Raw -Encoding UTF8; " ^
    "[System.IO.File]::AppendAllText('%OUTPUT%', $content + [Environment]::NewLine + [Environment]::NewLine, (New-Object System.Text.UTF8Encoding($true)))"

    >> "%OUTPUT%" echo.
    >> "%OUTPUT%" echo.
)

echo.
echo Done. Saved all Python code into %OUTPUT%
pause