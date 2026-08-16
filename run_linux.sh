#!/usr/bin/env bash

set -e

echo "==================================================="
echo "         Narsika NOC Panel - Universal Setup       "
echo "==================================================="

# 1. Prevent execution as root/sudo to avoid file permission conflicts
if [ "$EUID" -eq 0 ]; then
    echo "[!] Please execute this script as a standard user (without sudo)."
    echo "    Usage: ./run_linux.sh"
    exit 1
fi

# 2. Verify Python 3 presence
if ! command -v python3 &> /dev/null; then
    echo "[X] Python3 was not found. Please install Python 3.10+."
    exit 1
fi

# Function to install missing OS-level packages
install_system_packages() {
    echo ""
    echo "[!] Missing core system packages (python3-venv / pip / sshpass)."
    read -p "[?] Install required system packages via sudo? [Y/n] " choice
    choice=${choice:-Y}

    if [[ ! "$choice" =~ ^[Yy]$ ]]; then
        echo "[X] Setup cancelled by user."
        exit 1
    fi

    PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    echo "[*] Installing dependencies for Python ${PY_VER}..."

    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y "python${PY_VER}-venv" python3-pip sshpass openssh-client || \
        sudo apt-get install -y python3-venv python3-pip sshpass openssh-client
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y python3-pip sshpass openssh-clients
    elif command -v pacman &> /dev/null; then
        sudo pacman -Sy --noconfirm python-pip sshpass openssh
    elif command -v zypper &> /dev/null; then
        sudo zypper install -y python3-pip sshpass openssh
    else
        echo "[X] Unsupported package manager. Please install python3-venv manually."
        exit 1
    fi
}

# 3. Robust Virtual Environment Setup and Self-Healing
setup_venv() {
    if [ -d "venv" ]; then
        if [ ! -w "venv" ] || [ ! -f "venv/bin/activate" ]; then
            echo "[*] Removing damaged or permission-locked virtual environment..."
            if ! rm -rf venv 2>/dev/null; then
                echo "[!] Root permissions required to clean up locked venv directory:"
                sudo rm -rf venv
            fi
        fi
    fi

    if [ ! -d "venv" ]; then
        echo "[*] Creating isolated virtual environment (venv)..."
        if ! python3 -m venv venv 2>/dev/null; then
            install_system_packages
            rm -rf venv
            python3 -m venv venv
        fi
    fi
}

setup_venv

# 4. Activate virtual environment
echo "[*] Activating virtual environment..."
source venv/bin/activate

# 5. Install pre-compiled wheel dependencies
echo "[*] Installing dependencies from requirements.txt..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

# 6. Verify and install Ansible Galaxy collections
if ! ansible-galaxy collection list 2>/dev/null | grep -q "community.routeros"; then
    echo "[*] Installing required Ansible network collections..."
    ansible-galaxy collection install community.network community.routeros cisco.ios --force-with-deps &> /dev/null || true
fi

# 7. Start the Narsika NOC Application Server
echo ""
echo "==================================================="
echo "  🚀 Narsika NOC Server is Ready                   "
echo "  🔗 Access URL: http://127.0.0.1:5000              "
echo "==================================================="
python3 app.py