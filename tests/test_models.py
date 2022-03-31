from server.main import Users, Event, Camera
from server.enums.cameraEnums import CameraMode, CameraStatus
from server.enums.eventEnums import EventType
import datetime

def test_user():
    name = "Test"
    email = 'test@gmail.com'
    primary_camera = 1

    user = Users(name=name, 
                 email=email, 
                 primary_camera=primary_camera)
    
    assert user.name == name
    assert user.email == email
    assert user.primary_camera == primary_camera

def test_event():
    user_id = 5
    camera_id = 6
    name = "test event"
    image_link = "test.com"
    type = EventType.FACIAL_MATCH_SUCCESS
    timestamp = datetime.date(2021, 4, 4)

    event = Event(user_id=user_id, 
                  camera_id=camera_id, 
                  name=name, 
                  type=type,
                  image_link=image_link,
                  timestamp=timestamp)
    
    assert event.user_id == user_id
    assert event.camera_id == camera_id
    assert event.type == type
    assert event.name == name
    assert event.image_link == image_link
    assert event.timestamp == timestamp

def test_camera():
    name = "test camera"
    user_id = 5
    status = CameraStatus.ONLINE
    mode = CameraMode.FACIAL_RECOGNITION
    last_heartbeat = datetime.date(2021, 4, 4)

    camera = Camera(name=name, 
                    user_id=user_id, 
                    status=status,
                    last_heartbeat=last_heartbeat,
                    mode=mode)
    
    assert camera.name == name
    assert camera.user_id == user_id
    assert camera.status == status
    assert camera.mode == mode
    assert camera.last_heartbeat == last_heartbeat
