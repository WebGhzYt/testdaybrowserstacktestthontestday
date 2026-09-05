@echo off
setlocal enabledelayedexpansion

echo ==============================================================================
echo  BrowserStack Testathon - Automated Test Execution Runner (Windows)
echo  Project: webghzyt ^| Target: https://bugbash.online/
echo ==============================================================================

REM 1. Virtual Environment Setup
if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Creating Python virtual environment in .venv...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment. Ensure Python is installed.
        pause
        exit /b %ERRORLEVEL%
    )
)

echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat

REM 2. Install Dependencies
echo [INFO] Verifying / Installing dependencies from requirements.txt...
pip install -r requirements.txt --quiet

REM 3. Execute Pytest Suite via BrowserStack SDK
echo ==============================================================================
echo  Launching Pytest Suite
echo ==============================================================================

REM If BROWSERSTACK_USERNAME and ACCESS_KEY are present, use browserstack-sdk
browserstack-sdk pytest tests/ -v
if %ERRORLEVEL% neq 0 (
    echo [WARN] Some tests failed or browserstack-sdk returned exit code %ERRORLEVEL%.
)

REM 4. Generate & Verify Reports
echo ==============================================================================
echo  Exporting Excel and PDF Reports
echo ==============================================================================
python -m utils.report_utils

echo.
echo ==============================================================================
echo  Execution Complete!
echo  Reports available at:
echo    - Excel: reports\test_execution_report.xlsx
echo    - PDF:   reports\test_execution_report.pdf
echo ==============================================================================

pause
