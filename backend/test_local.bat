@echo off
REM Quick test script for Windows to verify the fix works locally

echo ========================================
echo AWS App Runner Compatibility Test
echo ========================================
echo.

echo Step 1: Testing Python imports...
python test_apprunner_compatibility.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Compatibility test failed!
    echo Please fix the issues before deploying.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Step 2: Installing dependencies...
echo ========================================
pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Step 3: Starting server...
echo ========================================
echo.
echo Server will start on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
echo Test endpoints:
echo   - Health: http://localhost:8000/health
echo   - Docs: http://localhost:8000/docs
echo.

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
