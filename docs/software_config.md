Software Configuration from New 
(note that this will download the full repository and the files could be seperated by client and server if desired)
April 20th, 2022

1)  Create and go into a desired project folder (currently ~/LFIAS) and run:
  * git clone https://github.com/rudy-patel/imageAnalysisSystem.git .
2)  Create a virtual environment, activate it, and install all Python packages from the requirements.txt file, this will take some time
    (note that the activate command will need to be run to restart the venv to run the program, more info can be found here:
    https://docs.python.org/3/tutorial/venv.html)
  * python -m venv env
  * source env/bin/activate
  * python -m pip install -r requirements.txt
3)  Place the AWS config and credentials files in the place where Linux expects them:
  * sudo mkdir ~/.aws
  * copy the config and credentials files into this directory
4)  Export the expected environment variables
  * export FLASK_APP=server.main.py
  * export DB_PASSWORD=*insert password here*
6)  Fix any software package related configuration issues:
  * Example 1: numpy didn't work by default so by tracing the error it was fixed by installing required dependencies (sudo apt-get install libatlas-base-dev)
  * Example 2: psycopg2 was throwing an error and after researching it the following dependency was installed (sudo apt-get install postgresql)
