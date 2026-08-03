# 🚀 Enterprise Network Automation & NOC Dashboard

A functional, modern Network Operations Center (NOC) management platform built with Python, Netmiko, and Ansible. Designed to streamline L2/L3 provisioning, live telemetry diagnostics, and configuration management across Cisco IOS and MikroTik RouterOS infrastructure.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Framework-Flask%203.1.3-green.svg)
![Ansible](https://img.shields.io/badge/Automation-Ansible%202.17-red.svg)
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

## 🛠️ Tech Stack & Core Libraries

* **Backend:** Python 3.11+, Flask 3.1.3, Flask-SQLAlchemy, Werkzeug
* **Automation Engines:** Netmiko 4.7.0 (SSH Telemetry), Ansible Core 2.17.0 (Configuration Push)
* **Frontend:** Jinja2 Templates, HTML5, CSS3, FontAwesome 6

---

## 🚀 Quick Start & Installation

### 🐧 Running on Linux (Native & Recommended)
Linux is the native home for network automation. Running the project on Ubuntu/Debian/CentOS unlocks 100% of the platform's capabilities.
```bash
git clone [https://github.com/Ali-Moghanni-ir/cisco-mikrotik-noc-panel.git](https://github.com/Ali-Moghanni-ir/cisco-mikrotik-noc-panel.git)
cd cisco-mikrotik-noc-panel
chmod +x run.sh
```
./run.sh
🪟 Running on Windows
Important Architecture Note: Ansible natively does not support Windows as a Control Node. However, this project is built to handle this gracefully through environment markers.

You have 3 options to run this platform on Windows:

Option 1: Windows Subsystem for Linux (WSL) - 🌟 Recommended
This allows you to run the native Linux engine directly inside Windows, unlocking all Ansible automation features.

Open PowerShell as Administrator and run: wsl --install

Restart your computer.

Open the "Ubuntu" terminal from your Start menu, navigate to the project folder, and run:

```Bash
./run.sh
```
💡 WSL Magic: When running inside WSL, Python automatically detects a native Linux environment (sys_platform == 'linux'). Therefore, our requirements.txt will fully install ansible-core and all automation modules without any Windows restrictions!

Option 2: Docker Desktop 🐳
Run the entire platform in an isolated Linux container.

Install Docker Desktop.

Open a terminal in the project folder and run:

```DOS
docker compose up -d
```
Option 3: Native Windows (Limited Mode)
You can run the app directly on Windows using CMD or PowerShell without WSL/Docker.

What works: The Web UI, Database, and Live SSH Telemetry (Netmiko) will work perfectly.

What doesn't: Ansible playbook execution will be safely blocked. The requirements.txt file uses OS-markers to automatically skip installing Ansible on Windows to prevent system crashes.

🔑 Default Credentials
Upon first execution, the system auto-generates the initial administrator account. Access the dashboard at:

URL: http://localhost:5000

Username: admin

Password: admin

(⚠️ Please change the default credentials via the Credentials page after your initial login).
