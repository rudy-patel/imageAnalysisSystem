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

def test_event(test_client):
    """Test the endpoint for posting events"""
    input_data = { 
        "user_id": 5,
        "camera_id": 2,
        "event_type": "IMAGE_CAPTURE_FAILED",
        "timestamp": datetime.date(2022, 4, 4)
    }
    response = test_client.post("/v1/events", data=input_data)
    response_data = json.loads(response.get_data(as_text=True))
    assert response_data['success'] == True
