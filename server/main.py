from ast import Pass
from crypt import methods
from datetime import datetime
# from db_classes.users import Users
# from db_classes.event import Event
# from db_classes.camera import Camera
from enums.cameraEnums import CameraMode, CameraStatus
from enums.eventEnums import EventType
from flask import Flask, redirect, url_for, render_template, request, flash, Response, session
from flask_session import Session 
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from Forms import LoginForm, SignUpForm
from imutils import build_montages
from os import environ
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from importlib import import_module
import argparse
import boto3
import cv2
import imagezmq
import imutils
import numpy as np
import os
import time
import datetime

# Configuration and settings
app = Flask(__name__)
app.config['SECRET_KEY'] = 'imageanalysissystem'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:' + environ["DB_PASSWORD"] + '@lfiasdb.cwtorsyu3gx6.us-west-2.rds.amazonaws.com/postgres'

Bootstrap(app)

db = SQLAlchemy(app)

loginManager = LoginManager()
loginManager.init_app(app)
loginManager.login_view = 'login'



#Generating funtion for video stream, produces frames from the PI one by one 
def generate_frame(camera_stream):
    #unique_name = (feed_type, device)

    #while True:
    #    cam_id, frame = camera_stream.get_frame()
    #    if frame is None:
    #        break
    cam_id, frame = camera_stream.get_frame()
    # Write the camera name
    #cv2.putText(frame, cam_id, (int(20), int(20 * 5e-3 * frame.shape[0])), 0, 2e-3 * frame.shape[0], (255, 255, 255), 2)

    frame = cv2.imencode('.jpg', frame)[1].tobytes()  # Remove this line for test camera
    return (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



#Video stream, should be the soucre of the homepage video image
@app.route('/video_feed')
def video_feed():

    camera_stream = import_module('server_camera').Camera
    resp = Response(generate_frame(camera_stream=camera_stream()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
    resp.headers["Cache-Control"] = "no-cache"
    return resp 
    





class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    events = db.relationship('Event', backref='users', lazy=True)
    cameras = db.relationship('Camera', backref='users', lazy=True)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    camera_id = db.Column(db.Integer, db.ForeignKey('camera.id'), nullable=False)
    type = db.Column(db.Enum(EventType), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

class Camera(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    status = db.Column(db.Enum(CameraStatus), nullable=False)
    mode = db.Column(db.Enum(CameraMode), nullable=False)
    
@loginManager.user_loader
def loadUser(id):
    return Users.query.get(int(id))

@app.route("/addEvent")
@login_required
def testAddEvent():
    
    newEvent = Event(user_id=current_user.id, camera_id=1, type=EventType.FACIAL_MATCH_SUCCESS, timestamp=datetime.now())

    db.session.add(newEvent)
    db.session.commit()

    return redirect(url_for('home'))

@app.route("/addCamera")
@login_required
def testAddCamera():
    
    newCamera = Camera(user_id=current_user.id, name="Camera #" + str(current_user.id), status=CameraStatus.OFFLINE, mode=CameraMode.FACIAL_RECOGNITION)

    db.session.add(newCamera)
    db.session.commit()
    
    return redirect(url_for('home'))

@app.route("/home")
@app.route("/")
@login_required
def home():
    return render_template("home.html", name=current_user.name)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('home'))
        flash("Invalid email/password")
    return render_template("login.html", form=form)

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = SignUpForm()

    if form.validate_on_submit():
        hashedPassword = generate_password_hash(form.password.data, method='sha256')

        isUserExisting = Users.query.filter_by(email=form.email.data).first()

        if not isUserExisting:
            newUser = Users(name=form.name.data, email= form.email.data, password=hashedPassword)

            db.session.add(newUser)
            db.session.commit()

            return redirect(url_for('login'))
            
        flash("A user already exists with that email!")
    return render_template("signup.html", form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/events")
@login_required
def events():
    return render_template("events.html")

@app.route("/cameras")
@login_required
def cameras():
    return render_template("cameras.html")

@app.route("/train")
@login_required
def train():
    return render_template("train.html")


@app.route("/train", methods=['POST'])
def upload_file():
    file = request.files['file']
    if file.filename != '':
        if file:
            file.filename = secure_filename(file.filename)
            output = send_to_s3(file, "lfiasimagestore")
            return str(output)
    else:
        return redirect("/")
    return redirect(url_for('train'))


def send_to_s3(file, bucket_name):
        session = boto3.Session(profile_name='default')
        s3 = session.client('s3')
        try:
            s3.upload_fileobj(
                file,
                bucket_name,
                file.filename,
                ExtraArgs={
                    "ContentType": file.content_type    #Set appropriate content type as per the file
                }
            )
        except Exception as e:
            print("Something Happened: ", e)
            return e
        return "{} recieved {}".format("us-west-2", file.filename)

if __name__ == "__main__":
    app.run(host="127.0.0.1", threaded=True, debug=True)