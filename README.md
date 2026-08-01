# 🚀 Enterprise Network Automation & NOC Dashboard

A functional, modern Network Operations Center (NOC) management platform built with Python (Flask), Netmiko, and Ansible. Designed to streamline L2/L3 provisioning, live telemetry diagnostics, and configuration management across Cisco IOS and MikroTik RouterOS infrastructure.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Framework-Flask-green.svg)
![Ansible](https://img.shields.io/badge/Automation-Ansible-red.svg)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20(WSL)-lightgrey.svg)

---

## ✨ Key Features

* 📊 **Logical Infrastructure Topology:** Group hardware into custom network zones and track manageability.
* 📡 **Live Hardware Telemetry:** Real-time diagnostics (CPU, Memory, Uptime, Temperature) via Netmiko SSH transport.
* 🔌 **L2 VLAN Provisioning:** Dynamic 802.1Q VLAN deployment and destruction using automated playbooks.
* 🛡️ **ACL Security Builder:** Policy deployment tool supporting multi-vendor (Cisco IOS & MikroTik RouterOS) rule generation.
* ⚡ **No-Code Automation Runner:** Upload custom `.yml` playbooks directly from the UI or execute pre-defined tasks.
* 📝 **Execution Audit Trail:** Detailed execution logging tracking operator identity, timestamps, target IPs, and raw Ansible output traces.
* 🔐 **Auto-Initialization & RBAC:** Automatic SQLite database creation with default seed credentials and Bcrypt password hashing.

---

## 🛠️ Tech Stack

* **Backend:** Python 3.11, Flask, Flask-SQLAlchemy, Werkzeug
* **Automation Engines:** Netmiko (SSH Telemetry), Ansible Core (Configuration Push)
* **Frontend:** Jinja2 Templates, HTML5, CSS3, FontAwesome 6

---

## 🚀 Quick Start & Installation

### 🐧 Running on Linux (Native & Recommended)
Linux is the native home for Ansible. Running the project on Ubuntu/Debian/CentOS unlocks 100% of the platform's capabilities.
```bash
git clone [https://github.com/Ali-Moghanni-ir/cisco-mikrotik-noc-panel](https://github.com/Ali-Moghanni-ir/cisco-mikrotik-noc-panel)
cd network-automation-dashboard
chmod +x run_linux.sh
./run_linux.sh
```
### 🪟 Running on Windows
Important Architecture Note: Ansible natively does not support Windows as a Control Node. However, this project is built to handle this gracefully.

You have 3 options to run this platform on Windows:

Option 1: Windows Subsystem for Linux (WSL) - 🌟 Recommended
This allows you to run the native Linux engine directly inside Windows, unlocking all Ansible automation features.

Open PowerShell as Administrator and run: wsl --install

Restart your computer.

Open the "Ubuntu" terminal from your Start menu, navigate to the project folder, and run:

```Bash
./run_linux.sh 
```
Option 2: Docker Desktop 🐳
Run the entire platform in an isolated Linux container.

```
Install Docker Desktop.
```

Open terminal in the project folder and run:

```DOS
docker compose up -d
```
Option 3: Native Windows (Limited Mode)
You can run the app directly on Windows without WSL or Docker by double-clicking run_win.bat.

What works: The Web UI, Database, and Live SSH Telemetry (Netmiko) will work perfectly.

What doesn't: Ansible playbook execution will be safely blocked by the system with an on-screen warning to prevent crashes.

🔑 Default Credentials
Upon first execution, the system auto-generates the initial administrator account:

URL: http://localhost:5000

Username: admin

Password: admin

(⚠️ Please change the default credentials via the Credentials page after initial login).

📁 Repository Structure
Plaintext
├── app/
│   ├── models.py          # SQLAlchemy Database Schemas
│   ├── routes.py          # Flask Endpoints & Automation Logic (Cross-platform aware)
│   └── templates/         # Jinja2 HTML Templates
├── backups/               # Auto-generated device configuration backups
├── database/              # SQLite DB Storage (.panel.db created at runtime)
├── playbooks/             # Ansible Playbooks Repository (.yml)
├── app.py                 # Application Entry Point & Auto-DB Initializer
├── requirements.txt       # Dependencies with OS-specific markers
├── run_linux.sh           # One-Click Linux Launch Script
└── run_win.bat            # One-Click Windows Launch Script
