@echo off
title Montazeri NOC Automation Panel
color 0B
echo ===================================================
echo   Montazeri NOC Panel - Windows Auto-Setup
echo ===================================================

:: بررسی وجود محیط مجازی
if not exist "venv\Scripts\activate.bat" (
    echo [!] Virtual environment not found. Creating one...
    python -m venv venv
)

:: فعال‌سازی محیط مجازی
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat

:: نصب و آپدیت پیش‌نیازها
echo [*] Checking dependencies from requirements.txt...
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt

:: اجرای سرور
echo.
echo [*] Starting the NOC Server...
echo [*] Please open your browser and navigate to http://127.0.0.1:5000
echo.
python app.py

pause