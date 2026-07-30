import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

# 1. Initialize App & Security Keys
app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-noc-key-2026' # Required to secure cookies
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database/panel.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 2. Bind Extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # Kicks unauthenticated users to the login route

db_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database'))
if not os.path.exists(db_dir):
    os.makedirs(db_dir)

from app import models

# 3. Tell Flask how to load the current user from the database
@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))

# 4. Generate Database & Default Admin
with app.app_context():
    db.create_all()
    # If no admin exists, create one with username: admin | password: admin
    if not models.User.query.filter_by(username='admin').first():
        hashed_password = bcrypt.generate_password_hash('admin').decode('utf-8')
        default_admin = models.User(username='admin', password=hashed_password)
        db.session.add(default_admin)
        db.session.commit()

from app import routes