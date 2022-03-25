from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import sys
sys.path.append("..\server")
from server.enums.cameraEnums import CameraMode, CameraStatus
from server.enums.eventEnums import EventType

db = SQLAlchemy()

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    events = db.relationship('Event', backref='users', lazy=True)
    cameras = db.relationship('Camera', backref='users', lazy=True)

    def create(self):
        db.session.add(self)
        db.session.commit()

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    camera_id = db.Column(db.Integer, db.ForeignKey('camera.id'), nullable=False)
    name = db.Column(db.String(50), nullable=True)
    type = db.Column(db.Enum(EventType), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    image_link = db.Column(db.String(200), nullable=True)

    def create(self):
        db.session.add(self)
        db.session.commit()

class Camera(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    status = db.Column(db.Enum(CameraStatus), nullable=False)
    mode = db.Column(db.Enum(CameraMode), nullable=False)

    def create(self):
        db.session.add(self)
        db.session.commit()