from flask import json


def test_test_post(client):
    response = client.post("/test")
    data = json.loads(response.get_data(as_text=True))
    assert data['data'] == 'post_request'

def test_test_get(client):
    response = client.get("/test")
    data = json.loads(response.get_data(as_text=True))
    assert data['data'] == 'get_request'
