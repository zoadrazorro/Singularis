@echo off
REM Singularis Beta v2 - Quick Launch Script
REM Windows batch file for easy launching

echo.
echo ========================================
echo   Singularis Beta v2 Quick Launch
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH
    echo Please install Python 3.10+ and add to PATH
    pause
    exit /b 1
)

echo [INFO] Python found
echo.

REM Show menu
echo Select mode:
echo   1. Standard (30 min, async)
echo   2. Quick Test (5 min, fast mode)
echo   3. Long Session (2 hours)
echo   4. Conservative (1 hour, low API usage)
echo   5. Integration Tests
echo   6. Custom...
echo.

set /p choice="Enter choice (1-6): "

if "%choice%"=="1" (
    echo.
    echo [LAUNCH] Standard mode - 30 minutes
    python run_singularis_beta_v2.py --duration 1800 --mode async
) else if "%choice%"=="2" (
    echo.
    echo [LAUNCH] Quick test - 5 minutes, fast mode
    python run_singularis_beta_v2.py --duration 300 --fast
) else if "%choice%"=="3" (
    echo.
    echo [LAUNCH] Long session - 2 hours
    python run_singularis_beta_v2.py --duration 7200 --mode async
) else if "%choice%"=="4" (
    echo.
    echo [LAUNCH] Conservative mode - 1 hour, low API usage
    python run_singularis_beta_v2.py --duration 3600 --conservative
) else if "%choice%"=="5" (
    echo.
    echo [LAUNCH] Running integration tests
    python run_singularis_beta_v2.py --test
) else if "%choice%"=="6" (
    echo.
    set /p duration="Enter duration in seconds: "
    set /p mode="Enter mode (async/sequential): "
    echo.
    echo [LAUNCH] Custom: %duration%s in %mode% mode
    python run_singularis_beta_v2.py --duration %duration% --mode %mode%
) else (
    echo.
    echo [ERROR] Invalid choice
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Session Complete
echo ========================================
pause
