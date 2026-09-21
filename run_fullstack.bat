@echo off
setlocal enabledelayedexpansion

:: Change directory to the folder where this batch file is located
cd /d "%~dp0"

echo =========================================================
echo       RetailPulse AI Platform - Full-Stack Launcher
echo =========================================================
echo Working Directory: %CD%
echo.

:: 1. Launch FastAPI Backend
echo [1/3] Starting FastAPI REST Engine on http://127.0.0.1:8000...
start "RetailPulse - FastAPI Backend" cmd /k "cd /d "%~dp0" && "%~dp0venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

:: Wait 3 seconds for backend to start
ping 127.0.0.1 -n 4 >nul

:: 2. Launch React + Vite Frontend
echo [2/3] Starting React 18 + Vite Frontend on http://localhost:5173...
start "RetailPulse - React Frontend" cmd /k "cd /d "%~dp0frontend" && npm.cmd run dev"

:: Wait 3 seconds for frontend to start
ping 127.0.0.1 -n 4 >nul

:: 3. Launch Web Browser
echo [3/3] Launching web browser...
start http://localhost:5173

echo.
echo =========================================================
echo   RetailPulse AI Platform is now LIVE!
echo   - Web Application: http://localhost:5173
echo   - Interactive API: http://127.0.0.1:8000/docs
echo =========================================================
echo Keep the backend and frontend terminal windows open.
echo.
pause
