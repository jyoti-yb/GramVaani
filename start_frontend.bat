@echo off
setlocal
title Gram Vaani Frontend

echo Starting Gram Vaani Frontend...

rem Navigate to frontend directory (handles spaces in path)
pushd "%~dp0frontend" || goto :error

rem Ensure Node is available
where node >nul 2>&1 || (
  echo Node.js not found on PATH. Please install Node 18+ and retry.
  goto :end
)

echo Installing dependencies...
npm install || goto :error

echo Starting development server...
npm run dev || goto :error

goto :end

:error
echo.
echo There was an error starting the frontend. See messages above.

:end
popd >nul 2>&1
pause
endlocal
