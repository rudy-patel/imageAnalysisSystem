# from flask_sqlalchemy import SQLAlchemy


# class Event(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#     camera_id = db.Column(db.Integer, db.ForeignKey('camera.id'), nullable=False)
#     type = db.Column(db.Enum(EventType), nullable=False)
#     timestamp = db.Column(db.DateTime, nullable=False)