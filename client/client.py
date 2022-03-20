from imutils.video import VideoStream
import imagezmq
import argparse
import socket
import time

# Argument parser
ap = argparse.ArgumentParser()
ap.add_argument("-s", "--server-ip", required=True, help="IP address of the server this client connects to")
args = vars(ap.parse_args())
# Initialize ImageSender object with the socket address of the server
sender = imagezmq.ImageSender(connect_to="tcp://{}:5555".format(args["server_ip"]))

# Get the host name, initialize the video stream, and allow the camera sensor time to warm up
rpiName = socket.gethostname()
vs = VideoStream(usePiCamera=True).start()

#vs = VideoStream(src=0).start()  // any USB camera can be used if this line replaces the one above

# If there is lag, too many pixels are being sent (max is used with no specification)
# Could set the video resolution here, see https://picamera.readthedocs.io/en/release-1.12/fov.html V2 camera section
# vs = VideoStream(usePiCamera=True, resolution=(xx, yy)).start()

 time.sleep(2.0)

while True:
	# Read the frame from the camera, send it to the server
	frame = vs.read()
	sender.send_image(rpiName, frame)