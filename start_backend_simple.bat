@echo off
setlocal
title Gram Vaani Backend (Simple)

echo Starting Gram Vaani Backend (Simple Mode)...
echo This avoids Rust compilation issues.

rem Navigate to backend directory
pushd "%~dp0backend" || goto :error

rem Create venv if missing
if not exist .venv (
  echo Creating virtual environment...
  py -3 -m venv .venv || python -m venv .venv
)

rem Install packages one by one to avoid compilation issues
echo Installing core dependencies...
".venv\Scripts\python" -m pip install --upgrade pip
".venv\Scripts\python" -m pip install fastapi
".venv\Scripts\python" -m pip install uvicorn
".venv\Scripts\python" -m pip install openai
".venv\Scripts\python" -m pip install python-multipart
".venv\Scripts\python" -m pip install requests
".venv\Scripts\python" -m pip install python-dotenv
".venv\Scripts\python" -m pip install pydantic
".venv\Scripts\python" -m pip install aiofiles
".venv\Scripts\python" -m pip install httpx

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
