$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Starting RetailPulse AI Full-Stack Platform" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan

# 1. Start FastAPI Backend in background
Write-Host "1. Starting FastAPI REST Engine on http://127.0.0.1:8000..." -ForegroundColor Yellow
$backendJob = Start-Process -FilePath "$scriptDir\venv\Scripts\python.exe" -ArgumentList "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload" -PassThru

Start-Sleep -Seconds 3

# 2. Start Vite Frontend
Write-Host "2. Starting React Vite Frontend on http://localhost:5173..." -ForegroundColor Yellow
Start-Process -FilePath "cmd.exe" -ArgumentList "/k", "cd /d `"$scriptDir\frontend`" && npm.cmd run dev"

Start-Sleep -Seconds 2

# 3. Open Web Browser
Write-Host "3. Launching browser to http://localhost:5173..." -ForegroundColor Yellow
Start-Process "http://localhost:5173"

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  RetailPulse AI Platform is now LIVE!" -ForegroundColor Green
Write-Host "  - React App: http://localhost:5173" -ForegroundColor White
Write-Host "  - API Docs:  http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "===================================================" -ForegroundColor Cyan
