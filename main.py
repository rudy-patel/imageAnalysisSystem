from flask import Flask, redirect, url_for, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html", content="Home")

@app.route("/events")
def events():
    return render_template("events.html", content="Events")

@app.route("/cameras")
def cameras():
    return render_template("cameras.html", content="Cameras")

@app.route("/train")
def train():
    return render_template("train.html", content="Train")



# this url route will take the input passed in and display it
# @app.route("/<name>/")
# def testURLInput(name):
#     return f"Hello {name}!"

# this url route will redirect to the home page
# @app.route("/admin/")
# def redirectWithoutParam():
#     return redirect(url_for("home"))

# this url route will redirect to the /name page with a specific param
# @app.route("/admin_param/")
# def redirectWithParam():
#     return redirect(url_for("testURLInput", name="Dr. Huda"))

if __name__ == "__main__":
    app.run(debug=True)
