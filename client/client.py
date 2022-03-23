
import imutils
from imutils.video import VideoStream
import face_recognition
import imagezmq
import argparse
import socket
import time
import cv2
import pickle

def facial_req(frame, data):
    currentname = "unknown"
    frame = imutils.resize(frame, width=500)
    # Detect the fce boxes
    boxes = face_recognition.face_locations(frame)
    # compute the facial embeddings for each face bounding box
    encodings = face_recognition.face_encodings(frame, boxes)
    names = []

    # loop over the facial embeddings
    for encoding in encodings:
        # attempt to match each face in the input image to our known
        # encodings
        matches = face_recognition.compare_faces(data["encodings"],
            encoding)
        name = "Unknown" #if face is not recognized, then print Unknown

        # check to see if we have found a match
        if True in matches:
            # find the indexes of all matched faces then initialize a
            # dictionary to count the total number of times each face
            # was matched
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}

            # loop over the matched indexes and maintain a count for
            # each recognized face face
            for i in matchedIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name, 0) + 1

            # determine the recognized face with the largest number
            # of votes (note: in the event of an unlikely tie Python
            # will select first entry in the dictionary)
            name = max(counts, key=counts.get)

            #If someone in your dataset is identified, print their name on the screen
            if currentname != name:
                currentname = name
                print(currentname)

        # update the list of names
        names.append(name)

    # loop over the recognized faces
    for ((top, right, bottom, left), name) in zip(boxes, names):
        # draw the predicted face name on the image - color is in BGR
        cv2.rectangle(frame, (left, top), (right, bottom),
            (0, 255, 225), 2)
        y = top - 15 if top - 15 > 15 else top + 15
        cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
            .8, (0, 255, 255), 2)

    # display the image to our screen
    return frame
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
# vs = VideoStream(usePiCamera=True, resolution=(xx, yy)).start()

# Allow the camera sensor time to warm up
time.sleep(2.0)
#Initialize 'currentname' to trigger only when a new person is identified.
currentname = "unknown"
#Determine faces from encodings.pickle file model created from train_model.py
encodingsP = "encodings.pickle"

# load the known faces and embeddings along with OpenCV's Haar
# cascade for face detection
print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(encodingsP, "rb").read())

while True:
    # Read the frame from the camera, perform facial req, send it to the server
    frame = vs.read()
    
    rec_frame = facial_req(frame, data)
    
    sender.send_image(camera_id, rec_frame)
    #Frame rate throttle
    time.sleep(0.1)
    
    

    
    
    
    