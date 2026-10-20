@echo off
setlocal
set ROOT=%~dp0

echo Starting CardioTwin backend and web dashboard...

if not exist "%ROOT%backend\venv\Scripts\activate.bat" (
  echo Backend virtual environment not found. Run the setup steps in SETUP.md first.
  pause
  exit /b 1
)
if not exist "%ROOT%web-dashboard\node_modules" (
  echo Web dependencies not found. Run npm install in web-dashboard first.
  pause
  exit /b 1
)

start "CardioTwin Backend" cmd /k "cd /d %ROOT%backend && call venv\Scripts\activate.bat && uvicorn main:app --reload --host 0.0.0.0 --port 8000"
start "CardioTwin Web Dashboard" cmd /k "cd /d %ROOT%web-dashboard && npm run dev"

echo.
echo Backend:  http://localhost:8000/docs
echo Dashboard: http://localhost:3000/dashboard
echo.
pause
