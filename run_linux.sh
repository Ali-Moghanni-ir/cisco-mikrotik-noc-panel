#!/bin/bash

echo "==================================================="
echo "  Montazeri NOC Panel - Linux Auto-Setup"
echo "==================================================="

# بررسی و ساخت محیط مجازی
if [ ! -d "venv" ]; then
    echo "[!] Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

# فعال‌سازی محیط مجازی
echo "[*] Activating virtual environment..."
source venv/bin/activate

# نصب پیش‌نیازها
echo "[*] Installing/Updating dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

# اجرای سرور
echo ""
echo "[*] Starting the NOC Server..."
echo "[*] Accessible on network at port 5000"
echo ""
python3 app.py