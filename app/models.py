from app import db
from flask_login import UserMixin
from datetime import datetime

# 1. Admin Access Control
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False) 

# 2. Network Grouping Model
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    devices = db.relationship('Device', backref='group', lazy=True)

# 3. Router & Switch Inventory Model
class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)       
    ip_address = db.Column(db.String(45), nullable=False)   
    username = db.Column(db.String(50), nullable=False)     
    password = db.Column(db.String(100), nullable=False)    
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=True)

from datetime import datetime

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id')) # Make sure 'user.id' matches your admin/user table name
    target_ip = db.Column(db.String(50))
    action_type = db.Column(db.String(100))
    status = db.Column(db.String(50))
    output = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)    