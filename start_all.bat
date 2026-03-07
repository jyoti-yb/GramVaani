@echo off
echo Starting Gram Vaani Backend and Frontend...
echo.

start "Backend Server" cmd /k "cd /d backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

start "Frontend Server" cmd /k "cd /d frontend && npm run dev"

echo.
echo Both servers are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
pause
