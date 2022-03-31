from flask import json
from server.models.models import Users, Camera

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
    