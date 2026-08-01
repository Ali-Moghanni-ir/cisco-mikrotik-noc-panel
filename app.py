import os
import sys
import socket
import platform
import logging
from app import app, db
from app.models import User
from app import bcrypt

# تنظیمات پایه لاگر برای چاپ پیام‌های تمیز
logging.basicConfig(level=logging.INFO, format='%(message)s')

def check_port(port):
    """بررسی می‌کند که آیا پورت مورد نظر در سیستم اشغال است یا خیر"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0

def ensure_directories():
    """بررسی و ساخت پوشه‌های ضروری پروژه با دسترسی مناسب"""
    base_dir = os.path.abspath(os.path.join(app.root_path, '..'))
    required_dirs = ['database', 'playbooks', 'backups', 'logs']
    
    for d in required_dirs:
        dir_path = os.path.join(base_dir, d)
        
        # اگر پوشه وجود نداشت آن را می‌سازد
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
                print(f"[+] Created missing directory: {d}/")
            except Exception as e:
                print(f"[!] Critical Error: Could not create directory '{d}'. Reason: {e}")
                sys.exit(1)
        
        # بررسی دسترسی نوشتن روی پوشه (بسیار مهم برای دیتابیس و بکاپ)
        if not os.access(dir_path, os.W_OK):
            print(f"[!] Warning: The system does not have WRITE permission for: {d}/")

def init_db():
    """اتصال به دیتابیس، ساخت جداول و ایجاد کاربر ادمین"""
    with app.app_context():
        try:
            db.create_all()
            
            # بررسی وجود ادمین
            if not User.query.filter_by(username='admin').first():
                hashed_pw = bcrypt.generate_password_hash('admin').decode('utf-8')
                default_admin = User(username='admin', password=hashed_pw)
                db.session.add(default_admin)
                db.session.commit()
                print("[+] Default administrator account provisioned. (User: admin | Pass: admin)")
            else:
                print("[+] Database connection verified successfully.")
                
        except Exception as e:
            print(f"[!] Critical Database Error: {e}")
            print("[!] Please check database file permissions or structure.")
            sys.exit(1)

def print_banner(os_name, port):
    """چاپ بنر گرافیکی و اطلاعات سیستمی در کنسول"""
    print("\n" + "="*55)
    print(" 🚀 Montazeri NOC Automation Panel - Initializing...")
    print("="*55)
    print(f" [*] Operating System : {os_name}")
    print(f" [*] Python Version   : {platform.python_version()}")
    print(f" [*] App Service Port : {port}")
    
    if os_name == "Windows":
        print(" [!] WARNING: Running on Windows OS.")
        print(" [!] Native Ansible execution is limited. SSH Telemetry is active.")
        
    print("="*55)
    print(f" [+] Web Interface is LIVE at: http://0.0.0.0:{port}")
    print(" [+] Press CTRL+C to gracefully shutdown the server.")
    print("="*55 + "\n")

if __name__ == '__main__':
    PORT = 5000
    os_name = platform.system()
    
    # 1. بررسی پورت
    if check_port(PORT):
        print(f"\n[!] Error: Port {PORT} is already in use by another service.")
        print("[!] Please stop the conflicting service or change the port in app.py")
        sys.exit(1)

    # 2. اعتبارسنجی پوشه‌ها
    ensure_directories()

    # 3. آماده‌سازی دیتابیس
    init_db()

    # 4. چاپ بنر سیستمی
    print_banner(os_name, PORT)

    # 5. روشن کردن سرور
    try:
        # برای جلوگیری از شلوغ شدن لاگ‌ها در محیط پروداکشن
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        
        # use_reloader=False از اجرای دوبارِ اسکریپت‌ها در حالت دیباگ جلوگیری می‌کند
        app.run(host='0.0.0.0', port=PORT, debug=True, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\n\n[-] Shutting down NOC Automation Engine safely... Goodbye!")
        sys.exit(0)