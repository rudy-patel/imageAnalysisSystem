from ast import Pass
from crypt import methods
from datetime import datetime
from flask import Flask, redirect, url_for, render_template, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import flash
from Forms import LoginForm, SignUpForm
import boto3
from enums.cameraEnums import CameraMode, CameraStatus
from os import environ

app = Flask(__name__)
app.config['SECRET_KEY'] = 'imageanalysissystem'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:' + os.environ["DB_PASSWORD"] + '@lfiasdb.cwtorsyu3gx6.us-west-2.rds.amazonaws.com/postgres'


Bootstrap(app)

db = SQLAlchemy(app)

loginManager = LoginManager()
loginManager.init_app(app)
loginManager.login_view = 'login'

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    events = db.relationship('Event', backref='user', lazy=True)
    cameras = db.relationship('Camera', backref='user', lazy=True)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    camera_id = db.Column(db.Integer, db.ForeignKey('camera.id'), nullable=False)
    type = db.Column(db.Enum(EventType), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

class Camera(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
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
    app.run(debug=True)
