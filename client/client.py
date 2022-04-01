import imutils
from imutils.video import VideoStream
import face_recognition
import imagezmq
import socket
import time
import cv2
import pickle
import requests
import random
import string
import os
from datetime import datetime
from collections import defaultdict
import numpy as np
import hashlib

class Client():
    def __init__(self, ip, port):
        self.port = port
        self.ip = ip
        self.mode = "SHAPE_DETECT"
        self.sender = imagezmq.ImageSender(connect_to="tcp://{}:{}".format(ip, "5555"))
        self.camera_id = 1
        self.name = socket.gethostname()
        self.vs = VideoStream(usePiCamera=True).start()
        self.encoding_data = pickle.loads(open("encodings.pickle", "rb").read())
        self.timeouts = defaultdict(int)
        self.timeout_duration = 60
        self.location = "/home/pi/imageAnalysisSystem/client"
        self.heartbeat_interval = 10
        self.last_heartbeat = 0
        self.circle_detection_timeout = 5
        self.is_primary = True
         #get hash of encoding
        self.encoding_hash = Client.calc_hash()
        time.sleep(2.0) # Camera warmup sleep

    def run(self):
        while True:
            self.heartbeat() # send heartbeat
            frame = self.vs.read() # read frame
            if self.mode == "FACIAL_RECOGNITION":
                frame = self.facial_req(frame, self.encoding_data)
            else:
                frame = self.circle_detect(frame)
            if self.is_primary:
                self.sender.send_image(self.camera_id, frame)

    def heartbeat(self):
        now = int(time.time())
        if now - self.last_heartbeat > self.heartbeat_interval:
            self.last_heartbeat = now
            # Send another heartbeat
            try:
                new_data = requests.get("http://" + self.ip + ":" + self.port + "/v1/heartbeat/" + str(self.camera_id)).json()
                
                self.mode = new_data['mode']
                self.is_primary = new_data['is_primary']
                if not self.encoding_hash == new_data['encodings_hash']:
                    self.get_new_encodings()
                print("Heartbeat response:")
                print(new_data)
            except:
                return



    def get_new_encodings(self):
            try:
                encodings = requests.get("http://" + self.ip + ":" + self.port + "/v1/encodings")
            except:
                print("couldnt get pickle :(")
                return
            os.remove("encodings.pickle")
            open('encodings.pickle', 'wb').write(encodings.content)
            self.encoding_data = pickle.loads(open("encodings.pickle", "rb").read())
            #Update hash
            self.encoding_hash = Client.calc_hash()
            print("Updated encodings file")
            
            
    def calc_hash():
        BUF_SIZE = 65536
        sha1 = hashlib.sha1()
        with open("encodings.pickle", 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                sha1.update(data)
        return sha1.hexdigest()


    
    # circle_detect algorithm from: https://pyimagesearch.com/2014/07/21/detecting-circles-images-using-opencv-hough-circles/
    def circle_detect(self, frame):
        now = int(time.time())
        if now - self.timeouts["circle_detect"] < self.circle_detection_timeout:
            return frame
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.2, 100)
        
        # ensure at least some circles were found
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int") # convert the (x, y) coordinates and radius of the circles to integers
            
            for (x, y, r) in circles:
                cv2.circle(frame, (x, y), r, (0, 255, 0), 4) # draw the circle in the output image
                cv2.rectangle(frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1) # draw the rectangle in the output image
                self.circle_detect_event(frame)
        
        return frame
        
    
    def circle_detect_event(self, frame):
        stamp = int(time.time())
        if stamp - self.timeouts["circle"] < self.timeout_duration: # Check for timeout
            return

        # Convert to jpg and save temp file
        # 10 digit random string with very low collision probability
        rand_string = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))
        filename = "circle_" + rand_string + ".jpg"
        cv2.imwrite(filename, frame)

        data = {
            "user_id": 4,
            "name": "circle",
            "event_type": "SHAPE_DETECT_SUCCESS",
            "timestamp": datetime.now(), 
            }

        file = {
            "image": (filename, open(filename, "rb"), 'image/jpg')
        }

        print("Sending request, circle detection")
        requests.post("http://" + self.ip + ":" + self.port + "/v1/" + str(self.camera_id) + "/ring-shape-analysis-event", files=file, data=data)
        
        # Delete temp file
        path = os.path.join(self.location, filename)
        os.remove(path)
        
        self.timeouts["circle"] = stamp # update timeout



    # Send a POST request to the server event route
    def facial_req_event(self, name, frame):
        stamp = int(time.time())
        if stamp - self.timeouts[name] < self.timeout_duration: # Check for timeout
            return

        # Convert to jpg and save temp file
        # 10 digit random string with very low collision probability
        rand_string = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))
        filename = "face-" + name + "_" + rand_string + ".jpg"
        cv2.imwrite(filename, frame)

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
        
        # Delete temp file
        path = os.path.join(self.location, filename)
        os.remove(path)
        
        self.timeouts[name] = stamp # update timeout


    # Takes a frame and returns a cv2 facial req boxed frame
    def facial_req(self, frame, data):
        match = False
        currentname = "Unknown" # the default name
        
        frame = imutils.resize(frame, width=500)
        
        boxes = face_recognition.face_locations(frame) # Detect the face boxes

        if boxes: # if at least one face is found
            match = True
        
        # compute the facial embeddings for each face bounding box
        encodings = face_recognition.face_encodings(frame, boxes)
        names = []
        
        # loop over the facial embeddings
        for encoding in encodings:
            # attempt to match each face in the input image to our known encodings
            matches = face_recognition.compare_faces(data["encodings"], encoding)
            name = "Unknown" # if face is not recognized, then Unknown

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

                # If someone in the dataset is identified, print their name
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
        
        return frame # display the image to our screen


def main():
    client = Client("127.0.0.1", "5000")
    client.run()

if __name__ == "__main__":
    main()
    