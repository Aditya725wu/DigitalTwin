@echo off
REM DiabetesTwin Installation Script for Windows

echo.
echo ==========================================
echo DiabetesTwin Installation Script
echo ==========================================
echo.

REM Check Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python 3.10+ from python.org
    exit /b 1
)

REM Setup Backend
echo [2/5] Setting up Backend...
cd backend
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
python generate_synthetic_data.py
python train_models.py
cd ..

REM Setup Frontend
echo [3/5] Setting up Web Dashboard...
cd web-dashboard
call npm install
cd ..

REM Setup Mobile
echo [4/5] Setting up Mobile App...
cd mobile-app
call npm install
cd ..

REM Create directories
echo [5/5] Creating directories...
if not exist "data" mkdir data
if not exist "models" mkdir models
if not exist "logs" mkdir logs

echo.
echo ==========================================
echo Installation Complete!
echo ==========================================
echo.
echo To start the applications:
echo.
echo Backend ^(FastAPI^):
echo   cd backend
echo   venv\Scripts\activate.bat
echo   uvicorn main:app --reload
echo.
echo Frontend ^(Next.js^):
echo   cd web-dashboard
echo   npm run dev
echo.
echo Mobile ^(Expo^):
echo   cd mobile-app
echo   npx expo start
echo.
pause
