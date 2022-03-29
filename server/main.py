from datetime import datetime
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
from importlib import import_module
from flask_migrate import Migrate
from apscheduler.schedulers.background import BackgroundScheduler

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

    scheduler = BackgroundScheduler()
    # in your case you could change seconds to hours
    scheduler.add_job(update_camera_status, trigger='interval', seconds=60)
    scheduler.start()
    try:
    # To keep the main thread alive
        return app
    except:
    # shutdown if app occurs except 
        scheduler.shutdown()

  

def update_camera_status():

    with app.app_context():
        online_cameras = Camera.query.filter_by(status = CameraStatus.ONLINE).all()
        for cam in online_cameras:
            if  datetime.now().timestamp() - cam.last_heartbeat.timestamp() > 60:
                cam.status = CameraStatus.OFFLINE
                cam.update()
    

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



@bp.route("/v1/heartbeat/<int:camera_id>", methods=["GET"])
def heartbeat(camera_id):
    #Renew heartbeat timestamp
    cam = Camera.query.filter_by(id = camera_id).first()
    cam.status = CameraStatus.ONLINE
    cam.last_heartbeat = datetime.now()
    cam.update()
    #Get primary camera ID for user
    return jsonify({'camera_id': camera_id, 'mode': cam.mode.value, 'is_primary': True, 'encodings': None})




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
        event.timestamp = event.timestamp.strftime("%d-%b-%Y %I:%M %p")
    return render_template("events.html", events=events)

@bp.route("/view_event/<int:event_id>")
@login_required
def event_view(event_id):
    event = Event.query.filter_by(id=event_id).first()
    event.type = event.type.value
    event.timestamp = event.timestamp.strftime("%d-%b-%Y %I:%M %p")
    return render_template("event_view.html", event=event)

@bp.route("/cameras")
@login_required
def cameras():
    cameras = Camera.query.order_by(Camera.status).all()
    for camera in cameras:
        camera.status = camera.status.value
        camera.mode = camera.mode.value
        camera.last_heartbeat = camera.last_heartbeat.strftime("%d-%b-%Y %I:%M %p")
    return render_template("cameras.html", cameras=cameras)

@bp.route("/train", methods=['GET', 'POST'])
@login_required
def train():
    form = TrainingForm()

    if form.validate_on_submit():
        if form.file.data.filename != '':
            if form.file:
                form.file.data.filename = secure_filename(form.file.data.filename)
                filepath = send_to_s3(form.file.data, "lfiasimagestore")
                flash("Saved image successfully at: {}".format(str(filepath)))
                return redirect(url_for('myapp.train'))
        else:
            return redirect("myapp.home")
    
    return render_template("train.html", form=form)

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