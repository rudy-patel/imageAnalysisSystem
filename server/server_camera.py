import imagezmq
import threading
import time 






#Event like class to signla clients when frames are available 
class CameraEvent:
    def __init__(self):
        self.events = {}

    def wait(self):
        
        ident = threading.get_ident()
        if ident not in self.events:
            # this is a new client
            # add an entry for it in the self.events dict
            # each entry has two elements, a threading.Event() and a timestamp
            self.events[ident] = [threading.Event(), time.time()]
        return self.events[ident][0].wait()

    def set(self):
        now = time.time()
        remove = None
        for ident, event in self.events.items():
            if not event[0].isSet():
                # if this client's event is not set, then set it
                # also update the last set timestamp to now
                event[0].set()
                event[1] = now
            else:
                # if the client's event is already set, it means the client
                # did not process a previous frame
                # if the event stays set for more than 5 seconds, then assume
                # the client is gone and remove it
                if now - event[1] > 5:
                    remove = ident
        if remove:
            del self.events[remove]


    def clear(self):
        self.events[threading.get_ident()][0].clear()



class Camera():

    frame = None
    event = None
    last_access = None
    thread = None


    def __init__(self):

        #self.unique_name = (feed_type, device)
        Camera.event = CameraEvent()
        Camera.last_access = time.time()

        # start background frame thread
        Camera.thread = threading.Thread(target=self._thread)
        Camera.thread.start()
        print("Streaming thread started")

        # wait until frames are available
        while self.get_frame() is None:
            time.sleep(0)



    #Returns the current camera frame
    @classmethod
    def get_frame(cls):
        #Camera.last_access = time.time()

        # wait for a signal from the camera thread
        cls.event.wait()
        cls.event.clear()

        return Camera.frame


    #calls imagehub.recv_image and returns a frame/ multiple frames????
    @classmethod
    def frames(cls, image_hub):
        #num_frames = 0
        #total_time = 0

        #time_start = time.time()

        print("Attempting to receive image")
        cam_id, frame = image_hub.recv_image()
        image_hub.send_reply(b'OK')  # this is needed for the stream to work with REQ/REP pattern

        #num_frames += 1

        #time_now = time.time()
        #total_time += time_now - time_start
        #fps = num_frames / total_time

        # uncomment below to see FPS of camera stream
        # cv2.putText(frame, "FPS: %.2f" % fps, (int(20), int(40 * 5e-3 * frame.shape[0])), 0, 2e-3 * frame.shape[0],(255, 255, 255), 2)

        return cam_id, frame




    #Thread function, collects frames from the specified IP/port
    def _thread(cls):
    
        port = 5555
        image_hub = imagezmq.ImageHub(open_port='tcp://*:{}'.format(port))
        print("Opened image hub, waiting for frames")
        while True:
            new_frame = cls.frames(image_hub)
            try:
                #print("New frame set")
                Camera.frame = new_frame
                Camera.event.set()

            except Exception as e:
                #frames_iterator.close()
                image_hub.zmq_socket.close()
                print('Closing server socket at port {}.'.format(port))
                print('Stopping server thread for device due to error.')
                print(e)


