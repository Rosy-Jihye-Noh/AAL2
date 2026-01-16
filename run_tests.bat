@echo off
REM AAL Project Test Runner for Windows
REM Usage: run_tests.bat [options]

echo.
echo ============================================================
echo   AAL Project Test Runner
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    exit /b 1
)

REM Run the Python test runner script
python run_tests.py %*

exit /b %errorlevel%
