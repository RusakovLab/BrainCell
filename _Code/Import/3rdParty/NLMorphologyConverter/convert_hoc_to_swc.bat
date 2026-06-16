@echo off
:: ==========================================================================
:: convert_hoc_to_swc.bat
::
:: Batch-converts every .hoc file in THIS folder to SWC via nlmc_swc.py.
:: Output goes to swc_out\ subfolder (created automatically).
::
:: Usage: double-click, or run from any prompt.
:: ==========================================================================

:: --- Edit this line if Python is not on your PATH --------------------------
:: Example: set "PYTHON=C:\Users\YourName\anaconda3\python.exe"
set "PYTHON=C:\Users\****\anaconda3\python.exe"
:: ---------------------------------------------------------------------------

:: Always run relative to the folder that contains this .bat
cd /d "%~dp0"

echo.
echo ==========================================================================
echo   HOC to SWC batch conversion
echo   Source : %~dp0
echo   Output : %~dp0swc_out\
echo ==========================================================================
echo.

:: Verify that Python is accessible before doing any work
"%PYTHON%" --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python was not found using: %PYTHON%
    echo.
    echo To fix this, do ONE of the following:
    echo   1. Add Anaconda to your system PATH, then re-open this window.
    echo   2. Edit the PYTHON variable at the top of this .bat file to the
    echo        full path of python.exe, for example:
    echo        set "PYTHON=C:\Users\YourName\anaconda3\python.exe"
    echo.
    pause
    exit /b 1
)

:: Run the conversion
"%PYTHON%" nlmc_swc.py --batch "." --pattern "*.hoc" --out "swc_out"

if errorlevel 1 (
    echo.
    echo Conversion finished with one or more errors. See details above.
) else (
    echo.
    echo All files converted successfully.
    echo SWC files are in: %~dp0swc_out\
)

pause
