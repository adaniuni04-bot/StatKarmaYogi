@echo off
title StatKarmaYogi - Install Dependencies
echo ============================================================
echo   StatKarmaYogi Platform - Installing Dependencies
echo ============================================================
echo.

echo [1/2] Installing Backend Python Requirements...
cd backend
python -m pip install -r requirements.txt
cd ..

echo.
echo [2/2] Installing Frontend Node.js Packages...
cd frontend
call npm install
cd ..

echo.
echo ============================================================
echo   Dependencies Installed Successfully!
echo   You can now double-click "start_all.bat" to launch.
echo ============================================================
pause
