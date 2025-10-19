@echo off
setlocal ENABLEDELAYEDEXPANSION
title Gram Vaani Backend

echo Starting Gram Vaani Backend...

rem Navigate to backend directory (handles spaces in path)
pushd "%~dp0backend" || goto :error

rem Ensure Python is available
where py >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
  where python >nul 2>&1 || (
    echo Python not found on PATH. Please install Python 3.11+ and retry.
    goto :end
  )
)

rem Create venv if missing
if not exist .venv (
  echo Creating virtual environment...
  py -3 -m venv .venv || python -m venv .venv
)

rem Upgrade pip and install deps
echo Installing dependencies...
".venv\Scripts\python" -m pip install --upgrade pip >nul
echo Trying minimal requirements first...
".venv\Scripts\python" -m pip install -r requirements-minimal.txt || (
  echo Minimal install failed, trying with specific versions...
  ".venv\Scripts\python" -m pip install fastapi uvicorn openai python-multipart requests python-dotenv pydantic aiofiles httpx
)

rem Start server
echo Starting server...
".venv\Scripts\python" main.py || goto :error

goto :end

:error
echo.
echo There was an error starting the backend. See messages above.

:end
popd >nul 2>&1
pause
endlocal
