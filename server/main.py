from datetime import datetime
from server.enums.cameraEnums import CameraMode, CameraStatus
from server.enums.eventEnums import EventType
from server.models.models import Users, Event, Camera
from flask import Flask, Blueprint, redirect, url_for, render_template, request, jsonify, flash, Response, abort
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from server.Forms import LoginForm, SignUpForm
from os import environ
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import boto3
import cv2
from server import server_camera
from importlib import import_module
from flask_migrate import Migrate

bp = Blueprint('myapp', __name__)
migrate = Migrate()

loginManager = LoginManager()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'imageanalysissystem'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:' + environ["DB_PASSWORD"] + '@lfiasdb.cwtorsyu3gx6.us-west-2.rds.amazonaws.com/postgres'

    Bootstrap(app)

    loginManager.init_app(app)
    loginManager.login_view = 'myapp.login'

    app.register_blueprint(bp)

    from server.models.models import db
    db.init_app(app)
    migrate.init_app(app, db)

    return app
  
 # API Endpoints
# TODO integrate with our token-based security to lock down these endpoints as per best practices

# This is a generic example that posts a new event
@bp.route("/v1/events", methods=["POST"])
def new_event(): 
    data = jsonify(request.form).json
    user_id = data["user_id"]
    camera_id = data["camera_id"]
    event_type = data["event_type"]
    timestamp = data["timestamp"]

    try:
        newEvent = Event(user_id=user_id, camera_id=camera_id, type=event_type, timestamp=timestamp, name = "yo", image_link="bro")
        newEvent.create()
        return jsonify({
            'success': True
        })

    except:
        abort(422)

# This is for posting a new facial recognition
@bp.route("/v1/<int:camera_id>/facial-detection-event", methods=["POST"])
def face_detected(camera_id):
    print("attempting to get request files")
    image = request.files["image"]
    print("attempting to save file")
    # image.save(secure_filename(image.filename))

    print("getting the remainder of the data")
    # data = jsonify(request.form).json
    user_id = request.form.get("user_id")
    name = request.form.get("name")
    event_type = request.form.get("event_type")
    timestamp = request.form.get("timestamp")

    print("Sending to s3")
    image_link = send_to_s3(image, "lfiasimagestore")

    try:
        newEvent = Event(user_id=user_id, camera_id=camera_id, name=name, type=event_type, timestamp=timestamp, image_link=image_link)
        newEvent.create()
        
        return jsonify({
            'success': True
        })

    except Exception as e:
        print(e)
        abort(422)

# ------------

@loginManager.user_loader
def loadUser(id):
    return Users.query.get(int(id))

@bp.route("/test", methods=["GET", "POST"])
def test():
    getData = 'get_request'
    postData = 'post_request'
    if(request.method == "POST"):
        return jsonify({'data': postData})
    elif (request.method == "GET"):
        return jsonify({'data': getData})

#Generating funtion for video stream, produces frames from the PI one by one 
def generate_frame(camera_stream):

    cam_id, frame = camera_stream.get_frame()

    frame = cv2.imencode('.jpg', frame)[1].tobytes()  # Remove this line for test camera
    return (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



#Video stream, should be the soucre of the homepage video image
@bp.route('/video_feed')
def video_feed():

    camera_stream = server_camera.Camera

    resp = Response(generate_frame(camera_stream=camera_stream()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp 

@bp.route("/addEvent")
@login_required
def testAddEvent():
    
    newEvent = Event(user_id=current_user.id, camera_id=1, type=EventType.IMAGE_CAPTURE_SUCCESS, timestamp=datetime.now())

    newEvent.create()

    return redirect(url_for('myapp.home'))

@bp.route("/addCamera")
@login_required
def testAddCamera():
    newCamera = Camera(user_id=current_user.id, name="Camera #" + str(current_user.id), status=CameraStatus.OFFLINE, mode=CameraMode.FACIAL_RECOGNITION)
    newCamera.create()

    return redirect(url_for('myapp.home'))

@bp.route("/home")
@bp.route("/")
@login_required
def home():
    events = Event.query.order_by(Event.timestamp.desc()).limit(3).all()
    for event in events:
        event.type = event.type.value
    return render_template("home.html", name=current_user.name, events=events)

@bp.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('myapp.home'))
        flash("Invalid email/password")
    return render_template("login.html", form=form)

@bp.route("/signup", methods=['GET', 'POST'])
def signup():
    form = SignUpForm()

    if form.validate_on_submit():
        hashedPassword = generate_password_hash(form.password.data, method='sha256')

        isUserExisting = Users.query.filter_by(email=form.email.data).first()

        if not isUserExisting:
            newUser = Users(name=form.name.data, email= form.email.data, password=hashedPassword)

            newUser.create()

            return redirect(url_for('myapp.login'))
            
        flash("A user already exists with that email!")
    return render_template("signup.html", form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('myapp.login'))

@bp.route("/events")
@login_required
def events():
    events = Event.query.order_by(Event.timestamp.desc()).all()
    for event in events:
        event.type = event.type.value
    return render_template("events.html", events=events)

@bp.route("/cameras")
@login_required
def cameras():
    cameras = Camera.query.order_by(Camera.status).all()
    for camera in cameras:
        camera.status = camera.status.value
        camera.mode = camera.mode.value
    return render_template("cameras.html", cameras=cameras)

@bp.route("/train")
@login_required
def train():
    return render_template("train.html")

@bp.route("/train", methods=['POST'])
def upload_file():
    file = request.files['file']
    if file.filename != '':
        if file:
            file.filename = secure_filename(file.filename)
            output = send_to_s3(file, "lfiasimagestore")
            return str(output)
    else:
        return redirect("myapp.home")
    return redirect(url_for('myapp.train'))

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
        return "https://lfiasimagestore.s3.us-west-2.amazonaws.com/{}".format(file.filename)

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)