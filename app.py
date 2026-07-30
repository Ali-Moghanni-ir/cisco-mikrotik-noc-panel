from app import app, db
from app.models import User
from app import bcrypt  
import os

def init_db():
    """ساخت خودکار دیتابیس و جداول در صورت عدم وجود"""
    with app.app_context():
        # مطمئن می‌شویم پوشه database وجود دارد
        db_dir = os.path.join(app.root_path, '..', 'database')
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
            print("[+] Database directory created.")

        # ساخت تمام جداول تعریف شده در models.py
        db.create_all()
        print("[+] Database tables checked/created successfully.")

        # ساخت کاربر ادمین پیش‌فرض در صورت خالی بودن دیتابیس
        if not User.query.filter_by(username='admin').first():
            # رمز عبور و نام کاربری هر دو admin تنظیم شدند
            hashed_pw = bcrypt.generate_password_hash('admin').decode('utf-8')
            default_admin = User(username='admin', password=hashed_pw)
            db.session.add(default_admin)
            db.session.commit()
            print("[+] Default admin user created! (User: admin | Pass: admin)")

if __name__ == '__main__':
    # ابتدا دیتابیس را بررسی و آماده می‌کند
    init_db()
    
    print("\n===================================================")
    print(" [+] Montazeri NOC System Initialized Successfully")
    print(" [+] Server running on: http://127.0.0.1:5000")
    print("===================================================\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)