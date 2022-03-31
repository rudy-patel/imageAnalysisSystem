from datetime import datetime
from enum import Enum
from server.enums.cameraEnums import CameraMode, CameraStatus
from server.enums.eventEnums import EventType
from server.models.models import Users, Event, Camera
from flask import Flask, Blueprint, redirect, url_for, render_template, request, jsonify, flash, Response, abort
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from server.Forms import LoginForm, SignUpForm, TrainingForm
from os import environ
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import boto3
import cv2
from server import server_camera
from flask_migrate import Migrate
from apscheduler.schedulers.background import BackgroundScheduler
import numpy as np
import urllib.request
import face_recognition
import pickle

bp = Blueprint('myapp', __name__)
migrate = Migrate()

loginManager = LoginManager()

camera_stream = None  

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

    app.jinja_env.filters['enum_to_string'] = enum_to_string
    app.jinja_env.filters['timestamp_to_string'] = timestamp_to_string
    app.jinja_env.filters['camera_name_from_id'] = camera_name_from_id

    scheduler = BackgroundScheduler()
    scheduler.add_job(update_camera_status, trigger='interval', seconds=60)
    scheduler.start()

    try:
        return app
    except:
        scheduler.shutdown() # shutdown if app occurs except

@loginManager.user_loader
def loadUser(id):
    return Users.query.get(int(id))

def update_camera_status():
    with app.app_context():
        online_cameras = Camera.query.filter_by(status = CameraStatus.ONLINE).all()
        for cam in online_cameras:
            if  datetime.now().timestamp() - cam.last_heartbeat.timestamp() > 60:
                cam.status = CameraStatus.OFFLINE
                cam.update()

# In progress: threaded encodings.pickle file generation to update the client-side
# recognized faces
def generate_face_encodings():
    s3 = boto3.resource('s3')    
    bucket_name = 'lfiasimagestore'

    # initialize the list of known encodings and known names
    knownEncodings = []
    knownNames = []
    
    for item in s3.Bucket(bucket_name).objects.filter(Prefix="{}/face_training/".format(current_user.id)):
        current_name = item.key.split('/')[2]

        image = url_to_image("https://{}.s3.us-west-2.amazonaws.com/{}".format(bucket_name, item.key))

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # detect the (x, y)-coordinates of the bounding boxes
        # corresponding to each face in the input image
        boxes = face_recognition.face_locations(rgb_image, model="hog")
        
        # compute the facial embedding for the face
        encodings = face_recognition.face_encodings(rgb_image, boxes)
        
        # loop over the encodings
        for encoding in encodings:
            # add each encoding + name to our set of known names and encodings
            knownEncodings.append(encoding)
            knownNames.append(current_name)
            
    # dump the facial encodings + names to disk
    data = {"encodings": knownEncodings, "names": knownNames}
    f = open("encodings.pickle", "wb")
    f.write(pickle.dumps(data))
    f.close()      

    
# Get an image from a url and manipulate it in RAM instead of downloading and playing around in disk
def url_to_image(url):
    # Download the image into local memory instead of disk
    resp = urllib.request.urlopen(url).read()
    image = np.asarray(bytearray(resp), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    # return the image
    return image

  
@bp.route("/v1/heartbeat/<int:camera_id>", methods=["GET"])
def heartbeat(camera_id):
    cam = Camera.query.filter_by(id = camera_id).first()
    cam.status = CameraStatus.ONLINE
    cam.last_heartbeat = datetime.now() # Renew heartbeat timestamp
    cam.update()
    
    user = Users.query.filter_by(id = cam.user_id).first()
    if user.primary_camera == cam.id:
        is_primary = True
    else:
        is_primary = False
    
    return jsonify({'camera_id': camera_id, 'mode': cam.mode.value, 'is_primary': is_primary, 'encodings': None})

# Update the users primary camera
@bp.route("/make_primary/<int:camera_id>")
@login_required
def make_primary(camera_id):
    user = Users.query.filter_by(id = current_user.id).first()
    user.primary_camera = camera_id
    user.update()
    
    return redirect(url_for('myapp.cameras'))

# This is for posting a new facial recognition
@bp.route("/v1/<int:camera_id>/facial-detection-event", methods=["POST"])
def face_detected(camera_id):
    user_id = request.form.get("user_id")
    name = request.form.get("name")
    event_type = request.form.get("event_type")
    timestamp = request.form.get("timestamp")

    image = request.files["image"]
    image.filename = "{}/{}/face_images/{}/{}".format(user_id, camera_id, name, image.filename)
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

# This is for posting a new ring fault analysis event
@bp.route("/v1/<int:camera_id>/ring-fault-analysis-event", methods=["POST"])
def fault_analysis(camera_id):
    user_id = request.form.get("user_id")
    name = request.form.get("name")
    event_type = request.form.get("event_type")
    timestamp = request.form.get("timestamp")

    analyzed_image = request.files["analyzed_image"]
    analyzed_image.filename = "{}/{}/ring_fault_images/{}/{}".format(user_id, camera_id, name, analyzed_image.filename)
    image_link = send_to_s3(analyzed_image, "lfiasimagestore")

    try:
        newEvent = Event(user_id=user_id, camera_id=camera_id, name=name, type=event_type, timestamp=timestamp, image_link=image_link)
        newEvent.create()
        
        return jsonify({
            'success': True
        })
    except Exception as e:
        print(e)
        abort(422)

# Generating funtion for video stream, produces frames from the Pi
def generate_frame(camera_stream, primary_camera):
    cam_id, frame = camera_stream.get_frame()
    frame = cv2.imencode('.jpg', frame)[1].tobytes()  # Remove this line for test camera
    return (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Video stream, should be the source of the home page video image
@bp.route('/video_feed/<int:primary_camera>')
def video_feed(primary_camera):
    global camera_stream
    
    if not camera_stream:
        camera_stream = server_camera.Camera()
    
    resp = Response(generate_frame(camera_stream, primary_camera),
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

def enum_to_string(obj):
    if isinstance(obj, Enum):
        return obj.value

    return obj # For all other types, let Jinja use default behavior

def timestamp_to_string(obj):
    return obj.strftime("%d-%b-%Y %H:%M")

def camera_name_from_id(id):
    camera = Camera.query.filter_by(id=id).first()
    return camera.name

@bp.route("/home")
@bp.route("/", methods=['GET', 'POST'])
@login_required
def home():
    events = Event.query.filter_by(user_id=current_user.id).order_by(Event.timestamp.desc()).limit(3).all()
    camera = Camera.query.filter_by(id=current_user.primary_camera).first()
    
    if request.method == 'POST':
        if request.form['submit_button'] == 'Facial Recognition':
            camera.mode = CameraMode.FACIAL_RECOGNITION
        elif request.form['submit_button'] == 'Fault Detection':
            camera.mode = CameraMode.FAULT_DETECTION
        else:
            pass # unknown
        
        camera.update()
        
        return redirect(url_for('myapp.home'))
    
    return render_template("home.html", camera=camera, events=events)

@bp.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=True, force=True)
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
    events = Event.query.filter_by(user_id=current_user.id).order_by(Event.timestamp.desc()).all()
    return render_template("events.html", events=events)

@bp.route("/view_event/<int:event_id>")
@login_required
def event_view(event_id):
    event = Event.query.filter_by(id=event_id).first()
    return render_template("event_view.html", event=event)

@bp.route("/cameras")
@login_required
def cameras():
    cameras = Camera.query.filter_by(user_id=current_user.id).order_by(Camera.status).all()
    return render_template("cameras.html", cameras=cameras)

@bp.route("/train", methods=['GET', 'POST'])
@login_required
def train():
    form = TrainingForm()

    if form.validate_on_submit():
        if form.file.data.filename != '':
            if form.file:
                form.file.data.filename = secure_filename(form.file.data.filename)

                if form.personSelect.data:
                    form.file.data.filename = "{}/face_training/{}/{}".format(current_user.id, form.personSelect.data[0], form.file.data.filename)
                else:
                    form.file.data.filename = "{}/face_training/{}/{}".format(current_user.id, form.newPersonName.data, form.file.data.filename)

                filepath = send_to_s3(form.file.data, "lfiasimagestore")
                
                flash("Saved image successfully at: {}".format(str(filepath)))

                generate_face_encodings()

                return redirect(url_for('myapp.train'))
        else:
            return redirect("myapp.home")
    
    return render_template("train.html", form=form)

@bp.route("/download/<int:event_id>")
@login_required
def download(event_id):
    event = Event.query.filter_by(id=event_id).first()
    
    session = boto3.Session(profile_name='default')
    s3_client = session.client('s3')

    try:
        bucket_name = "lfiasimagestore"
        file_name = "event-" + str(event_id) + ".jpg"
        object_name = event.image_link.split(".com/",1)[1] 

        file = s3_client.get_object(Bucket=bucket_name, Key=object_name)
        
        return Response(
            file['Body'].read(),
            mimetype='text/plain',
            headers={"Content-Disposition": "attachment;filename="+file_name}
        )

    except Exception as e:
        print("Something Happened: ", e)
        return e

def send_to_s3(file, bucket_name):
        session = boto3.Session(profile_name='default')
        s3 = session.client('s3')
        
        try:
            s3.upload_fileobj(
                file,
                bucket_name,
                file.filename,
                ExtraArgs={
                    "ContentType": file.content_type #Set appropriate content type as per the file
                }
            )
        except Exception as e:
            print("Something Happened: ", e)
            
            return e
        
        return "https://{}.s3.us-west-2.amazonaws.com/{}".format(bucket_name, file.filename)

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, use_reloader=False)
