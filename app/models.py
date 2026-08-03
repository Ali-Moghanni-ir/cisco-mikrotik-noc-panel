from app import db
from datetime import datetime
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    logs = db.relationship('AuditLog', backref='admin', lazy=True)

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    devices = db.relationship('Device', backref='group', lazy=True)

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), default='admin')
    password = db.Column(db.String(100), default='')
    os_type = db.Column(db.String(50), nullable=False, default='cisco_ios')
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=True)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    target_ip = db.Column(db.String(50), nullable=False)
    action_type = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    output = db.Column(db.Text, nullable=True)