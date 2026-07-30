# cisco-mikrotik-noc-panel
A lightweight, cross-platform Network Operations Center (NOC) dashboard built with Flask, Netmiko, and Ansible for automated Cisco &amp; MikroTik orchestration and live telemetry.
The startup script automatically builds a isolated virtual environment (venv), installs all specified dependencies from requirements.txt, initializes the panel.db SQLite database, and creates the default administrator account.

Upon first execution, the system auto-generates the initial administrator account:

URL: http://127.0.0.1:5000

Username: admin
Password: admin
