from imutils.video import VideoStream
import imagezmq
import argparse
import socket
import time
import cv2

# Argument parser
#ap = argparse.ArgumentParser()
#ap.add_argument("-s", "--server-ip", required=True, help="IP address of the server this client connects to")
#ap.add_argument("-s", "--port-number", required=True, help="Port of the server this client connects to (NOTE 5555, 5556)")
#args = vars(ap.parse_args())
# Initialize ImageSender object with the socket address of the server thread
port = "5555"
ip = "127.0.0.1"
sender = imagezmq.ImageSender(connect_to="tcp://{}:{}".format(ip, port))

# Get the host name, initialize the video stream
camera_id = socket.gethostname()
vs = VideoStream(usePiCamera=True).start()

# Any USB camera can be used if this line is used instead
# vs = VideoStream(src=0).start()

# Change to your IP stream address (need to get from manufacturer or set up)
# See https://help.angelcam.com/en/articles/372649-finding-rtsp-addresses-for-ip-cameras-nvrs-dvrs
# path = "rtsp://<client-ip>:<client-port>//<idk.sdp>"
# vs = VideoStream(path)

# If there is lag, too many pixels are being sent (max is used with no specification) - set video resolution
# See https://picamera.readthedocs.io/en/release-1.12/fov.html
# vs = VideoStream(usePiCamera=True, resolution=(xx, yy)).start()

# Allow the camera sensor time to warm up
time.sleep(2.0)

while True:
	# Read the frame from the camera, send it to the server
	frame = vs.read()
	
	
	
	sender.send_image(camera_id, frame)
	#Frame rate throttle
	time.sleep(0.1)