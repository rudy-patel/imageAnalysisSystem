#made with the help of https://gitee.com/huzhuhua/Flask-Multi-Camera-Streaming-With-YOLOv4-and-Deep-SORT/tree/master
import imagezmq
import threading
import time


#Event like class to signal clients when frames are available 
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
                if now - event[1] > 10:
                    remove = ident
        if remove:
            del self.events[remove]


    def clear(self):
        self.events[threading.get_ident()][0].clear()


#Server side camera, starts a thread to collect frames from the client 
class Camera():

    frame = None
    event = None
    last_access = None
    thread = None
    instance = None


    def __init__(self):
        
        if Camera.thread:
            return          

        Camera.event = CameraEvent()
        Camera.last_access = time.time()

        # start frame collection thread
        Camera.thread = threading.Thread(target=self._thread)
        Camera.thread.start()
        print("Streaming thread started")

        # wait until frames are available
        while self.get_frame() is None:
            time.sleep(0)


    #Returns the current camera frame
    @classmethod
    def get_frame(cls):
        #It is possible to use last_access to setup a timeout for the thread
        #Camera.last_access = time.time()
        if Camera.frame == None:
            return None, None
        # wait for a signal from the camera thread
        cls.event.wait()
        cls.event.clear()
        return Camera.frame


    #calls imagehub.recv_image and returns a frame
    @classmethod
    def collect_frame(cls, image_hub):
        cam_id, frame = image_hub.recv_image()
        image_hub.send_reply(b'OK')  # this is needed for the stream to work with REQ/REP pattern

        return cam_id, frame


    #Thread function, collects frames from the specified port
    def _thread(cls):
    
        port = 5555
        image_hub = imagezmq.ImageHub(open_port='tcp://*:{}'.format(port))
        print("Opened image hub, waiting for frames")
        while True:
            new_frame = cls.collect_frame(image_hub)
            try:
                Camera.frame = new_frame
                Camera.event.set()

            except Exception as e:
                image_hub.zmq_socket.close()
                print('Closing server socket at port {}.'.format(port))
                print('Stopping server thread for device due to error.')
                print(e)