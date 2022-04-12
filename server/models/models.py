from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import sys
from server.enums.cameraEnums import CameraMode, CameraStatus
from server.enums.eventEnums import EventType

sys.path.append("..\server")

db = SQLAlchemy()

# This model describes a user and maps to the users table
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    primary_camera = db.Column(db.Integer, nullable=True)
    events = db.relationship('Event', backref='users', lazy=True)
    cameras = db.relationship('Camera', backref='users', lazy=True)

    # this function creates a new user in the database
    def create(self):
        db.session.add(self)
        db.session.commit()

    def get_id(self):
        return self.id
    
    # this function updates the current user in the database
    def update(self):
        db.session.commit()

# This model describes an event and maps to the events table
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    camera_id = db.Column(db.Integer, db.ForeignKey('camera.id'), nullable=False)
    name = db.Column(db.String(50), nullable=True)
    type = db.Column(db.Enum(EventType), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    image_link = db.Column(db.String(200), nullable=True)

    # this function creates a new event in the database
    def create(self):
        db.session.add(self)
        db.session.commit()

# This model describes a camera and maps to the cameras table
class Camera(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    status = db.Column(db.Enum(CameraStatus), nullable=False)
    mode = db.Column(db.Enum(CameraMode), nullable=False)
    last_heartbeat = db.Column(db.DateTime, nullable=True)

    # this function creates a new camera in the database
    def create(self):
        db.session.add(self)
        db.session.commit()
    
    # this function updates the current event in the database
    def update(self):
        db.session.commit()
