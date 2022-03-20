# from flask_sqlalchemy import SQLAlchemy


# class Camera(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#     name = db.Column(db.String(50), nullable=False)
#     status = db.Column(db.Enum(CameraStatus), nullable=False)
#     mode = db.Column(db.Enum(CameraMode), nullable=False)