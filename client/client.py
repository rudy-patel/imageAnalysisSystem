
import imutils
from imutils.video import VideoStream
import face_recognition
import imagezmq
import argparse
import socket
import time
import cv2
import pickle
import requests
import random
import string
import os
#from server.enums.cameraEnums import CameraMode, CameraStatus
from datetime import datetime
from collections import defaultdict
import circle_fault_detect as cfd
import numpy as np



class Client():

    def __init__(self, ip, port):
        self.port = port
        self.ip = ip
        #For now, 1 = facial detection and 0 = fault detection
        self.mode = "FAULT_DETECT"
        self.sender = imagezmq.ImageSender(connect_to="tcp://{}:{}".format(ip, "5555"))
        #ON CONFIG the camera will get its ID and asscoiated user
        self.camera_id = 1
        self.name = socket.gethostname()
        self.vs = VideoStream(usePiCamera=True).start()
        self.encode_data = pickle.loads(open("encodings.pickle", "rb").read())
        self.timeouts = defaultdict(int)
        self.timeout_duration = 60
        self.location = "/home/pi/imageAnalysisSystem/client"
        self.is_primary = True
        self.heartbeat_interval = 60
        self.last_heartbeat = 0
        self.circle_detection_timeout = 5
        #Camera warmup sleep
        time.sleep(2.0)


    def run(self):
        #Main loop
        while True:
            #Send heartbeat
            #self.heartbeat()
            frame = self.vs.read()
            if self.mode == "FACIAL_RECOGNITION":
                frame = self.facial_req(frame, self.encode_data)
            else:
                frame = self.circle_detect(frame)
            if self.is_primary:
                self.sender.send_image(self.camera_id, frame)


    def heartbeat(self):
        #Send get request to the server every X seconds
        now = int(time.time())
        if now - self.last_heartbeat > self.heartbeat_interval:
            #Send another heartbeat
            new_data = requests.get("http://" + self.ip + ":" + self.port + "/v1/heartbeat/" + str(self.camera_id)).json()
            #parse new data
            self.mode = new_data['mode']
            self.is_primary = new_data['is_primary']
            print("Heartbeat response:")
            print(new_data)
            
            #Set last_heartbeat 
            self.last_heartbeat = now
    
    def circle_detect(self, frame):
        now = int(time.time())
        if now - self.timeouts["circle_detect"] < self.circle_detection_timeout:
            return frame
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.2, 100)
        # ensure at least some circles were found
        if circles is not None:
            # convert the (x, y) coordinates and radius of the circles to integers
            circles = np.round(circles[0, :]).astype("int")
            # loop over the (x, y) coordinates and radius of the circles
            for (x, y, r) in circles:
                # draw the circle in the output image, then draw a rectangle
                # corresponding to the center of the circle
                cv2.circle(frame, (x, y), r, (0, 255, 0), 4)
                cv2.rectangle(frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
                print("Circle detected")
        return frame
        
        
    
    def circle_fault_detect(self, frame):
        print("Attempting fault detection")
        stamp = int(time.time())
        #Check timeout
        if stamp - self.timeouts["fault_detect"] < self.fault_detection_timeout:
            return
        print("Timeout check passed")
        #convert to jpg
        #theImage = cv2.imdecode(frame, cv2.IMREAD_GRAYSCALE)
        theImage = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        threshold = cfd.findThreshold(theImage)
        theImage = cfd.thresholdImage(theImage, threshold)
        theImage = cfd.applyBinaryMorph(theImage)
        labeled_frame = cfd.applyImageCCL(theImage)
        is_defective, frame = cfd.renderLabeledImage(labeled_frame)
        
        if is_defective:
            print("Send fault detect event")
            #send event
        else:
            print("No fault detected")
            
        self.timeouts["fault_detect"] = int(time.time())
            

            

    #Send a POST request to the server event route
    def facial_req_event(self, name, frame):
        stamp = int(time.time())
        #Check timeout
        if stamp - self.timeouts[name] < self.timeout_duration:
            return
        #Convert to jpg and save temp file
        #10 digit random string with very low collision probability
        rand_string = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))
        filename = "face-" + name + "_" + rand_string + ".jpg"
        cv2.imwrite(filename, frame)

        #Build post and send request
        data = {
            "user_id": 4,
            "name": name,
            "event_type": "FACIAL_MATCH_SUCCESS",
            "timestamp": datetime.now(), 
            }

        file = {
            "image": (filename, open(filename, "rb"), 'image/jpg')
        }

        print("Sending request, Name: " + name)
        requests.post("http://" + self.ip + ":" + self.port + "/v1/" + str(self.camera_id) + "/facial-detection-event", files=file, data=data)
        
        #Delete temp file
        path = os.path.join(self.location, filename)
        os.remove(path)
        #Set new timeout
        self.timeouts[name] = stamp


    def update_encodings(self):
        self.data = pickle.loads(open("encodings.pickle", "rb").read())


    #takes a frame and returns a cv2 facial req boxed frame
    def facial_req(self, frame, data):
        match = False
        currentname = "Unknown"
        frame = imutils.resize(frame, width=500)
        # Detect the fce boxes
        boxes = face_recognition.face_locations(frame)

        if boxes:
            #AT LEAST ONE FACE WAS FOUND
            match = True
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
                # each recognized face
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
        if match:
            self.facial_req_event(names[0], frame)
        # display the image to our screen
        return frame


def main():

    client = Client("127.0.0.1", "5000")
    client.run()


if __name__ == "__main__":
    main()   


    
    
    