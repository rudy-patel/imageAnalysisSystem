# from flask_login import UserMixin
# from flask_sqlalchemy import SQLAlchemy

# class Users(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), nullable=False)
#     email = db.Column(db.String(50), unique=True, nullable=False)
#     password = db.Column(db.String(80), nullable=False)
#     events = db.relationship('Event', backref='users', lazy=True)
#     cameras = db.relationship('Camera', backref='users', lazy=True)