@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo    Explainable Fake Review Detector
echo ==========================================

:: Detect Python command
set PYTHON_CMD=python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    set PYTHON_CMD=py
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        set PYTHON_CMD=python3
    )
)

:: Path to the virtual environment's Python
set VENV_PYTHON=".\.venv\Scripts\python.exe"

:: 1. Backend (Flask) Setup & Launch
echo [1/2] Syncing AI Engine (Python)...
if not exist ".venv" (
    echo [.venv folder not found. Creating it...]
    %PYTHON_CMD% -m venv .venv
)

echo Checking dependencies...
%VENV_PYTHON% -m pip install --quiet -r requirements.txt

echo Launching AI Backend (Flask)...
start "AI Backend" /min cmd /k "%VENV_PYTHON% app.py"

:: 2. Frontend (Vite) Setup & Launch
echo [2/2] Syncing UI (React)...
cd frontend
if not exist "node_modules" (
    echo [node_modules folder not found. Installing...]
    call npm install --quiet
)

echo Launching Web UI (Vite)...
start "Web UI" cmd /k "npm run dev"

echo.
echo ==========================================
echo    PROJECT IS RUNNING!
echo ==========================================
echo 1. AI Backend: http://127.0.0.1:5000
echo 2. Web UI:     http://localhost:5173
echo.
echo Use the newly opened windows to see the logs.
echo ==========================================
pause
