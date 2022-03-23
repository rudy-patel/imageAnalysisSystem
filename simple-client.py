import requests
from datetime import datetime

hardcoded_url = "http://127.0.0.1:5000/v1/events"

a = datetime.now()
testid = 2

test_obj = {
    "user_id": 4,
    "camera_id": testid,
    "event_type": "IMAGE_CAPTURE_FAILED",
    "timestamp": a
}

x = requests.post(hardcoded_url, data = test_obj)
print(x.text)