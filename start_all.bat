@echo off
title StatKarmaYogi Platform Launcher
echo ============================================================
echo   StatKarmaYogi - Launching Platform
echo ============================================================
echo.
echo [1/2] Launching Backend Server on http://localhost:8000...
start "StatKarmaYogi - Backend Server" cmd /k "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

timeout /t 3 >nul

echo [2/2] Launching Frontend Server on http://localhost:3000...
if not exist "frontend\node_modules" (
    echo [INFO] First-time setup detected: Installing frontend dependencies...
    cd frontend && call npm install && cd ..
)
start "StatKarmaYogi - Frontend Server" cmd /k "cd frontend && npm run dev"

echo.
echo ============================================================
echo   Platform is booting up!
echo   - Frontend: http://localhost:3000
echo   - Backend API Docs: http://localhost:8000/docs
echo   - Ollama (AI): http://localhost:11434
echo ============================================================
pause
