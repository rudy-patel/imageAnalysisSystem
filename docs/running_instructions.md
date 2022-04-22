### Running Instructions

Instructions for after setup - running the client and server either locally or on a network
Note: ensure that FLASK_APP and DB_PASSWORD environment variables have been set and that the aws configuration files are in the correct location as per the
software configuration document

Running the Client and Server **locally** on the Pi:
1) Navigate to the `client/` folder and run the following command inside to run on `localhost`: `python client.py`
2) In a *seperate* terminal, navigate to the `server/` folder and run the following command inside to run on `localhost`: `flask run`
3) Access the site via `127.0.0.1/5000` on the Pi web browser

Running the Client and Server over **LAN** (preferred):
1) Navigate to the `client/` folder and run the following command inside to run on the device where the server is running. Note that `<ip_address>` and `<port>` should be typed out as additional arguments to tell the client the ip/port to connect to: `python client.py <ip_address> <port>`
2) On the seperate device where the server will be run, navigate to the `server/` folder and run the following command inside: `flask run`
3) Access the site via `127.0.0.1/5000` on the server device's web browser
