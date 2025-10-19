@echo off
setlocal
title Gram Vaani - Launcher

echo Starting Gram Vaani - Complete Application
echo.
echo This will start both backend and frontend servers
echo.

rem Start Backend in its own window (handles spaces, creates venv)
start "Gram Vaani Backend" cmd /k "call "%~dp0start_backend.bat""

echo.
echo Waiting 7 seconds for backend to start...
timeout /t 7 /nobreak > nul
echo.

rem Start Frontend in its own window
start "Gram Vaani Frontend" cmd /k "call "%~dp0start_frontend.bat""

echo.
echo Both servers are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo You can close this window now.
pause > nul
endlocal
