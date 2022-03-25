
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

class Client():


    def __init__(self, ip, port):
        #Set up ports/ip infos
        self.port = port
        self.ip = ip
        #For now, 1 = facial detection and 0 = fault detection
        self.facial_mode = True 
        self.sender = imagezmq.ImageSender(connect_to="tcp://{}:{}".format(ip, port))
        self.camera_id = socket.gethostname()
        self.vs = VideoStream(usePiCamera=True).start()
        self.data = pickle.loads(open("encodings.pickle", "rb").read())
        #Only send one event per name every 10 second interval
        #Before sending and event make sure time.now() - timeout[NAME] > 10s
        #When an event is sent, store the timestamp in timeouts[NAME]
        self.timeouts = {}

        #Camera warmup sleep
        time.sleep(2.0)




    def run(self):
        #Main loop
        while True:
            #Check for heartbeat/configure
            #Get frame
            frame = self.vs.read()
            #get
            if self.facial_mode:
                frame = Client.facial_req(frame, self.data)
            else:
                #Fault detection here
                pass

            self.sender.send_image(self.camera_id, frame)
            #send frame to live.datastream


    #Send a POST request to the server event route
    def facial_req_event(self, name, frame):
        stamp = int(time.time())
        #Check timeout
        if stamp - self.timeouts[name] < 10:
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
            "timestamp": stamp, #Stamp may need to be reformatted
            }

        file = {
            "image": ("filename", open(filename, "rb"), 'image/jpg')
        }
        requests.post("https://127.0.0.1:5000/v1/" + self.camera_id + "/facial-detection-event", files=file, data=data)

        #Delete temp file
        os.remove(filename)
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

    client = Client("127.0.0.1", "5555")
    client.run()


if __name__ == "__main__":
    main()   


    
    
    