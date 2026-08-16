@echo off
setlocal enabledelayedexpansion
title Narsika NOC Panel - Windows Runner

echo ===================================================
echo          Narsika NOC Panel - Windows Setup        
echo ===================================================

:: 1. Check if Python is installed and accessible in PATH
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Python is not installed or not added to system PATH.
    echo     Please install Python 3.10+ and check "Add Python to PATH".
    pause
    exit /b 1
)

:: 2. Create virtual environment if it does not exist
if not exist "venv\Scripts\activate.bat" (
    echo [*] Initializing virtual environment (venv)...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [X] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: 3. Activate virtual environment
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat

:: 4. Upgrade pip and install required dependencies
echo [*] Verifying Python dependencies...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

:: 5. Native Windows execution note regarding Ansible
echo.
echo [!] NOTE: Telemetry and Inventory management work natively on Windows.
echo     To execute Ansible Playbooks, run via WSL using ./run_linux.sh.
echo.

:: 6. Start the Narsika NOC Server
echo ===================================================
echo   🚀 Narsika NOC Server is Ready                   
echo   🔗 Access URL: http://127.0.0.1:5000             
echo ===================================================
python app.py

pause