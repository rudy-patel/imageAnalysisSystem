from flask import json
from server.models.models import Users, Camera
import datetime

def test_event(test_client):
    input_data = { 
        "user_id": 5,
        "camera_id": 2,
        "event_type": "IMAGE_CAPTURE_FAILED",
        "timestamp": datetime.date(2022, 1, 1)
    }
    
    response = test_client.post("/v1/events", data=input_data)
    response_data = json.loads(response.get_data(as_text=True))
    
    assert response_data['success'] == True

def test_heartbeat(test_client):
    cameraID = 2
    response = test_client.get("/v1/heartbeat/" + str(cameraID))
    response_data = json.loads(response.get_data(as_text=True))

    cam = Camera.query.filter_by(id = cameraID).first()
    user_primary_cam = Users.query.filter_by(id=cam.user_id).first().primary_camera
    
    assert response_data['camera_id'] == cam.id
    assert response_data['mode'] == cam.mode.value
    assert response_data['is_primary'] == (user_primary_cam == cameraID)
    assert response_data['encodings'] == None
    