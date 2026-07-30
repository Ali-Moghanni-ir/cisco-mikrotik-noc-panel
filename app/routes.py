import os
import json
import logging
import platform
import subprocess
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.wrappers import Response as WerkzeugResponse
from werkzeug.utils import secure_filename

from app import app, db, bcrypt
from app.models import Device, Group, AuditLog, User

# ==========================================
# ⚙️ Configuration & Logging
# ==========================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("Montazeri_NOC")

ALLOWED_PLAYBOOKS = {
    'cisco_acl.yml', 
    'manage-vlan.yml', 
    'mikrotik_acl.yml', 
    'test_connection.yml', 
    'backup_config.yml', 
    'check_interfaces.yml'
}
ANSIBLE_TIMEOUT = 300 

# ==========================================
# 🔐 1. Authentication
# ==========================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            logger.info(f"Operator {username} authenticated successfully.")
            return redirect(url_for('index'))
        else:
            flash('نام کاربری یا کلمه عبور اشتباه است.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not bcrypt.check_password_hash(current_user.password, current_password):
            flash('رمز عبور فعلی نامعتبر است.', 'danger')
        elif new_password != confirm_password:
            flash('رمز عبور جدید و تکرار آن مطابقت ندارند.', 'danger')
        else:
            current_user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            db.session.commit()
            flash('رمز عبور با موفقیت تغییر کرد.', 'success')
            
    return render_template('change_password.html')


# ==========================================
# 📊 2. Dashboard & Inventory
# ==========================================
@app.route('/')
@login_required
def index():
    devices = Device.query.all()
    groups = Group.query.all()
    return render_template('index.html', devices=devices, groups=groups)

@app.route('/add-group', methods=['POST'])
@login_required
def add_group():
    group_name = request.form.get('group_name')
    if group_name:
        try:
            new_group = Group(name=group_name.strip())
            db.session.add(new_group)
            db.session.commit()
            flash(f'Zone {group_name} initialized.', 'success')
        except Exception:
            db.session.rollback()
            flash('ایجاد زون با خطا مواجه شد.', 'danger')
    return redirect(url_for('index'))

@app.route('/add-device', methods=['POST'])
@login_required
def add_device():
    name = request.form.get('device_name')
    ip_address = request.form.get('ip_address')
    group_id = request.form.get('group_id')
    username = request.form.get('username')
    password = request.form.get('password')

    if not name or not ip_address:
        flash('نام و آدرس IP الزامی است.', 'danger')
        return redirect(url_for('index'))

    try:
        new_device = Device(
            name=name.strip(),
            ip_address=ip_address.strip(),
            group_id=group_id if group_id else None,
            username=username.strip() if username else 'admin',
            password=password.strip() if password else ''
        )
        db.session.add(new_device)
        db.session.commit()
        flash(f'تجهیز {name} اضافه شد.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('خطا در ثبت پایگاه داده.', 'danger')

    return redirect(url_for('index'))


# ==========================================
# 🛡️ 3. Audit & Live Telemetry
# ==========================================
@app.route('/logs')
@login_required
def view_logs():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(200).all()
    return render_template('logs.html', logs=logs)

@app.route('/health/<int:device_id>')
@login_required
def device_health(device_id):
    device = Device.query.get_or_404(device_id)
    
    health_data = {
        'status': 'Offline', 
        'cpu': 'N/A', 
        'memory': 'N/A',
        'temperature': 'N/A', 
        'uptime': 'N/A'
    }

    param = '-n' if platform.system().lower() == 'windows' else '-c'
    ping_status = subprocess.call(['ping', param, '1', device.ip_address], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    
    if ping_status == 0:
        health_data['status'] = 'Online'
        try:
            from netmiko import ConnectHandler
            connection = ConnectHandler(
                device_type='cisco_ios',
                host=device.ip_address,
                username=device.username,
                password=device.password,
                timeout=5
            )
            
            sh_version = connection.send_command("show version")
            for line in sh_version.split('\n'):
                if "uptime is" in line:
                    health_data['uptime'] = line.split("uptime is ")[-1]
                    
            sh_cpu = connection.send_command("show processes cpu sorted | include CPU")
            if "five seconds:" in sh_cpu:
                health_data['cpu'] = sh_cpu.split("five seconds: ")[1].split(";")[0]

            sh_mem = connection.send_command("show memory statistics | include Processor")
            if "Processor" in sh_mem:
                health_data['memory'] = "Active"

            sh_env = connection.send_command("show env temperature status")
            if "Celsius" in sh_env or "OK" in sh_env:
                health_data['temperature'] = "Normal"

            connection.disconnect()
        except Exception as e:
            logger.error(f"ارتباط Netmiko برای مانیتورینگ تجهیز {device.ip_address} شکست خورد: {e}")

    return render_template('health.html', device=device, health=health_data)


# ==========================================
# 🌐 4. Core Network (VLAN & ACL)
# ==========================================
@app.route('/vlan', methods=['GET', 'POST'])
@login_required
def vlan_manager():
    devices = Device.query.all()
    log_output = None

    if request.method == 'POST':
        device_id = request.form.get('device_id')
        vlan_id = request.form.get('vlan_id')
        vlan_name = request.form.get('vlan_name')
        action = request.form.get('action', 'present')

        device = Device.query.get_or_404(device_id)
        playbook_path = os.path.abspath(os.path.join(app.root_path, '..', 'playbooks', 'manage-vlan.yml'))

        extra_vars = {
            'ansible_host': device.ip_address,
            'ansible_user': device.username,
            'ansible_password': device.password,
            'vlan_id': vlan_id,
            'vlan_name': vlan_name,
            'state': action
        }

        try:
            command = ['ansible-playbook', playbook_path, '--extra-vars', json.dumps(extra_vars)]
            result = subprocess.run(command, capture_output=True, text=True, timeout=ANSIBLE_TIMEOUT)
            log_output = result.stdout if result.returncode == 0 else result.stderr

            log_entry = AuditLog(
                admin_id=current_user.id,
                target_ip=device.ip_address,
                action_type=f"VLAN Controller: ID {vlan_id} ({action})",
                status="Success" if result.returncode == 0 else "Failed",
                output=log_output
            )
            db.session.add(log_entry)
            db.session.commit()
        except subprocess.TimeoutExpired:
            log_output = "Timeout: ارتباط با تجهیز برقرار نشد."
        except Exception as e:
            log_output = f"Critical Execution Error: {str(e)}"

    return render_template('vlan.html', devices=devices, log=log_output)


@app.route('/acl', methods=['GET', 'POST'])
@login_required
def acl_manager():
    devices = Device.query.all()
    log_output = None

    if request.method == 'POST':
        device_id = request.form.get('device_id')
        os_type = request.form.get('os_type')
        action = request.form.get('action')
        protocol = request.form.get('protocol')
        acl_name = request.form.get('acl_name')
        src_ip = request.form.get('src_ip')
        dst_ip = request.form.get('dst_ip')
        port = request.form.get('port')

        device = Device.query.get_or_404(device_id)
        
        playbook_file = 'cisco_acl.yml' if os_type == 'cisco' else 'mikrotik_acl.yml'
        playbook_path = os.path.abspath(os.path.join(app.root_path, '..', 'playbooks', playbook_file))

        extra_vars = {
            'ansible_host': device.ip_address,
            'ansible_user': device.username,
            'ansible_password': device.password,
            'action': action,
            'protocol': protocol,
            'acl_name': acl_name,
            'src_ip': src_ip,
            'dst_ip': dst_ip,
            'port': port
        }

        try:
            command = ['ansible-playbook', playbook_path, '--extra-vars', json.dumps(extra_vars)]
            result = subprocess.run(command, capture_output=True, text=True, timeout=ANSIBLE_TIMEOUT)
            log_output = result.stdout if result.returncode == 0 else result.stderr

            log_entry = AuditLog(
                admin_id=current_user.id,
                target_ip=device.ip_address,
                action_type=f"ACL Rule: {acl_name} ({action})",
                status="Success" if result.returncode == 0 else "Failed",
                output=log_output
            )
            db.session.add(log_entry)
            db.session.commit()
        except subprocess.TimeoutExpired:
            log_output = "Timeout: ارتباط با تجهیز برقرار نشد."
        except Exception as e:
            log_output = f"Critical Execution Error: {str(e)}"

    return render_template('acl.html', devices=devices, log=log_output)


# ==========================================
# 🚀 5. No-Code Playbook Runner (Dynamic)
# ==========================================
@app.route('/playbooks')
@app.route('/playbook-runner', endpoint='playbook_runner')
@login_required
def list_playbooks():
    devices = Device.query.all()
    
    # اسکن پوشه playbooks و پیدا کردن تمام فایل‌های YML
    playbook_dir = os.path.abspath(os.path.join(app.root_path, '..', 'playbooks'))
    if not os.path.exists(playbook_dir):
        os.makedirs(playbook_dir) # اگر پوشه نبود بسازد
        
    available_playbooks = [f for f in os.listdir(playbook_dir) if f.endswith(('.yml', '.yaml'))]
    
    return render_template('playbook.html', devices=devices, available_playbooks=available_playbooks)


@app.route('/upload-playbook', methods=['POST'])
@login_required
def upload_playbook():
    """آپلود فایل‌های کاستوم Ansible"""
    if 'file' not in request.files:
        flash('هیچ فایلی ارسال نشده است.', 'danger')
        return redirect(url_for('playbook_runner'))
        
    file = request.files['file']
    if file.filename == '':
        flash('فایلی انتخاب نشده است.', 'danger')
        return redirect(url_for('playbook_runner'))
        
    # بررسی امنیت: فقط فایل‌های YAML مجاز هستند
    if file and (file.filename.endswith('.yml') or file.filename.endswith('.yaml')):
        # ایمن‌سازی نام فایل (جلوگیری از هک مسیر)
        filename = secure_filename(file.filename)
        playbook_dir = os.path.abspath(os.path.join(app.root_path, '..', 'playbooks'))
        
        file.save(os.path.join(playbook_dir, filename))
        logger.info(f"فایل پلی‌بوک جدید توسط {current_user.username} آپلود شد: {filename}")
        flash(f'فایل {filename} با موفقیت به سرور اضافه شد.', 'success')
    else:
        flash('فقط فایل‌های با فرمت .yml یا .yaml مجاز هستند!', 'danger')
        
    return redirect(url_for('playbook_runner'))


@app.route('/run-playbook', methods=['POST'])
@login_required
def run_playbook():
    device_id = request.form.get('device_id')
    # استفاده از secure_filename برای جلوگیری از اجرای فایل‌های مخرب خارج از پوشه
    playbook_name = secure_filename(request.form.get('playbook_name'))

    device = Device.query.get_or_404(device_id)
    playbook_path = os.path.abspath(os.path.join(app.root_path, '..', 'playbooks', playbook_name))
    
    if not os.path.exists(playbook_path):
        flash('فایل Playbook روی سرور یافت نشد.', 'danger')
        return redirect(url_for('playbook_runner'))

    extra_vars = {
        'ansible_host': device.ip_address,
        'ansible_user': device.username,
        'ansible_password': device.password
    }

    try:
        command = ['ansible-playbook', playbook_path, '--extra-vars', json.dumps(extra_vars)]
        result = subprocess.run(command, capture_output=True, text=True, timeout=ANSIBLE_TIMEOUT)
        
        log_entry = AuditLog(
            admin_id=current_user.id,
            target_ip=device.ip_address,
            action_type=f"Custom Playbook: {playbook_name}",
            status="Success" if result.returncode == 0 else "Failed",
            output=result.stdout if result.returncode == 0 else result.stderr
        )
        db.session.add(log_entry)
        db.session.commit()
        
        if result.returncode == 0:
            flash(f'فایل {playbook_name} روی {device.name} اجرا شد.', 'success')
        else:
            flash(f'خطا در اجرای پلی‌بوک. گزارشات را بررسی کنید.', 'danger')
            
    except Exception as e:
        flash(f"System Error: {str(e)}", 'danger')
        
    return redirect(url_for('playbook_runner'))

@app.route('/list-playbooks')
def fallback_list_playbooks():
    return redirect(url_for('playbook_runner'))