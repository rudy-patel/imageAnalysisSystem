from server.main import Users, Event, Camera
from server.enums.cameraEnums import CameraMode, CameraStatus
from server.enums.eventEnums import EventType
import datetime

def test_new_user():
    name = "Test"
    email = 'test@gmail.com'

    user = Users(name=name, email=email)
    
    assert user.name == name
    assert user.email == email

def test_new_event():
    user_id = 1
    camera_id = 1
    type = EventType.FACIAL_MATCH_SUCCESS
    timestamp = datetime.date(2022, 4, 4)

    event = Event(user_id=user_id, camera_id=camera_id, type=type, timestamp=timestamp)
    
    assert event.user_id == user_id
    assert event.camera_id == camera_id
    assert event.type == type
    assert event.timestamp == timestamp

def test_new_camera():
    name = "test camera"
    user_id = 1
    status = CameraStatus.ONLINE
    mode = CameraMode.FACIAL_RECOGNITION

    camera = Camera(name=name, user_id=user_id, status=status, mode=mode)
    
    assert camera.name == name
    assert camera.user_id == user_id
    assert camera.status == status
    assert camera.mode == mode
