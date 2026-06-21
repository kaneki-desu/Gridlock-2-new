@echo off
REM TrafficTwin AI - Complete Setup Script for Windows
REM Automates backend and frontend setup

setlocal enabledelayedexpansion

echo ================================================
echo TrafficTwin AI - Complete Setup
echo ================================================

REM Check prerequisites
echo.
echo Checking prerequisites...

python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 3 is not installed
    exit /b 1
)
echo ✓ Python 3 found

npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm is not installed
    exit /b 1
)
echo ✓ npm found

REM Setup Backend
echo.
echo Setting up Backend...

cd backend

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo ⚠ Please edit backend\.env with your PostgreSQL credentials
)

echo ✓ Backend dependencies installed

REM Setup Frontend
echo.
echo Setting up Frontend...

cd ..\frontend

REM Install Node dependencies
echo Installing Node dependencies...
call npm install

REM Create .env.local file if it doesn't exist
if not exist .env.local (
    echo Creating .env.local file from template...
    copy .env.example .env.local
)

echo ✓ Frontend dependencies installed

REM Summary
echo.
echo ================================================
echo ✓ Setup Complete!
echo ================================================
echo.
echo Next Steps:
echo 1. Set up PostgreSQL database:
echo    createdb traffic_twin_ai
echo    psql traffic_twin_ai ^< ..\backend\schema.sql
echo.
echo 2. Edit backend\.env with your database URL
echo.
echo 3. Train ML models (from backend directory):
echo    python train_model.py --data-path C:\path\to\data.csv
echo.
echo 4. Build FAISS index (from backend directory):
echo    python build_rag_index.py --data-path C:\path\to\data.csv
echo.
echo 5. Start backend (from backend directory):
echo    python app.py
echo.
echo 6. Start frontend (from frontend directory):
echo    npm run dev
echo.
echo 7. Access the application:
echo    Backend API: http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo    Frontend: http://localhost:3000
echo.

pause
