[![Build](https://img.shields.io/github/workflow/status/rudy-patel/imageAnalysisSystem/Python%20application/main)](https://github.com/rudy-patel/imageAnalysisSystem/actions/workflows/python-app.yml)
[![Issues](https://img.shields.io/github/issues/rudy-patel/imageAnalysisSystem)](https://github.com/rudy-patel/imageAnalysisSystem/issues)
[![Pull Requests](https://img.shields.io/github/issues-pr/rudy-patel/imageAnalysisSystem)](https://github.com/rudy-patel/imageAnalysisSystem/pulls)
![Repo Size](https://img.shields.io/github/repo-size/rudy-patel/imageAnalysisSystem)
[![License](https://img.shields.io/github/license/rudy-patel/imageAnalysisSystem)](https://www.apache.org/licenses/LICENSE-2.0.txt)

# Image Analysis System
This system is a low-footprint versatile application involving hardware and software componenets for recognition of objects and/or faces through machine learning algorithms.

### First time setup
This project runs inside a Python virtual environment. To set up your environment, follow these steps:
1. Navigate to the root directory in terminal
2. Create a virtual environment using: `python3 -m venv env`

To setup the hardware unit, follow the instructions [here](https://github.com/rudy-patel/imageAnalysisSystem/wiki/Hardware-Configuration).

On **Linux/MacOS**:
- Run `source env/bin/activate` to **start** the Python virtual environment.
- Run `deactivate` to **stop** the Python virtual environment.
- If you need to set an environment variable use: `export <variable>=<value>`. This is only saved in your current terminal.

On **Windows**:
- Run `.\env\Scripts\activate` to **start** the Python virtual environment.
- Run `deactivate` to **stop** the Python virtual environment.
- If you need to set an environment variable use: `set <variable>=<value>`. This is only saved in your current terminal.

You have now created the virtual environment in the project directory, continue following the steps to run the server.

### Running the server
To run the server:

1. Navigate to the root directory in terminal.
2. Start the Python virtual environment, following the instructions in First Time Setup.
3. Install the dependencies by running `pip install -r requirements.txt`.
4. Run `python3 -m server.main` to start the server.

You're all set! The server should now be running on `127.0.0.1:5000`.

### Running the client
To run the client:

### Resources used
* [Login using Flask-Login and SQLAlchemy](https://www.youtube.com/watch?v=8aTnmsDMldY)
* [Data tables with bootstrap4](https://www.youtube.com/watch?v=yGBk9Nalyq8)
* [Data models in Flask](https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/)
* [Adding flask-migrate to existing project](https://blog.miguelgrinberg.com/post/how-to-add-flask-migrate-to-an-existing-project)
* [Flask Multi-Camera Streaming](https://gitee.com/huzhuhua/Flask-Multi-Camera-Streaming-With-YOLOv4-and-Deep-SORT/tree/master)
### Contributors
| Name | Email  |
|---|---|
|  Rudy Patel | rutvik@ualberta.ca |
|  Kaden Dreger | kaden@ualberta.ca |
|  Jacob Paetsch | jpaetsch@ualberta.ca |
|  Braden Stolte | bstolte@ualberta.ca |
