# Quickstart script for Windows PowerShell
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " India's Official Statistical System - Skill Intelligence   " -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan

$env:PYTHONPATH = "$PSScriptRoot\backend"

Write-Host "`n[1/3] Checking Python environment..." -ForegroundColor Green
python --version

Write-Host "`n[2/3] Seeding database with demo data..." -ForegroundColor Green
python -m backend.app.db.seed.seed_data

Write-Host "`n[3/3] Starting Backend API server on http://localhost:8000..." -ForegroundColor Green
Write-Host "Open API Docs at: http://localhost:8000/docs" -ForegroundColor Yellow
uvicorn backend.app.main:app --reload --port 8000
