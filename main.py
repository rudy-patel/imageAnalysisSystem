from ast import Pass
from crypt import methods
from flask import Flask, redirect, url_for, render_template, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import flash
from Forms import LoginForm, SignUpForm
import boto3



app = Flask(__name__)
app.config['SECRET_KEY'] = 'imageanalysissystem'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
#CONFIG AWS KEYS/BUCKET DETAILS
#app.config["S3_LOCATION"] = "us-west-2"
Bootstrap(app)

db = SQLAlchemy(app)

loginManager = LoginManager()
loginManager.init_app(app)
loginManager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    
@loginManager.user_loader
def loadUser(id):
    return User.query.get(int(id))

@app.route("/home")
@app.route("/")
@login_required
def home():
    return render_template("home.html", name=current_user.name)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
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
        newUser = User(name=form.name.data, email= form.email.data, password=hashedPassword)

        db.session.add(newUser)
        db.session.commit()

        return redirect(url_for('login'))

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
        print("Got file" + file.filename)
        #uploaded_file.save(uploaded_file.filename)
        if file:
            file.filename = secure_filename(file.filename)
            output = send_to_s3(file, "lfiasimagestore")
            return str(output)
    else:
        return redirect("/")
    return redirect(url_for('train'))


def send_to_s3(file, bucket_name):
        s3 = boto3.client('s3', 
                    aws_access_key_id="AKIAVFCBRF2YXLFX7GJX", 
                    aws_secret_access_key="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", 
                    region_name="us-west-2"
                    )
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
