from flask import json, jsonify
import datetime


def test_test_post(client):
    response = client.post("/test")
    data = json.loads(response.get_data(as_text=True))
    assert data['data'] == 'post_request'

def test_test_get(client):
    response = client.get("/test")
    data = json.loads(response.get_data(as_text=True))
    assert data['data'] == 'get_request'

# TODO figure out how to set up this api and test as we were getting json and response data errors
# def test_event(test_client):
#     """Test the endpoint for posting events"""
#     json_data = { 
#         "user_id": 4,
#         "camera_id": 2,
#         "event_type": "IMAGE_CAPTURE_FAILED",
#         "timestamp": datetime.date(2022, 4, 4)
#     }
#     response = test_client.post("/v1/events", json=jsonify(json_data))

#     data = json.loads(response.get_data(as_text=True))
#     assert data['success'] == True
