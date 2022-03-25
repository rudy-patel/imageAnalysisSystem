import requests
from datetime import datetime

hardcoded_url = "http://127.0.0.1:5000/v1/1/facial-detection-event"

a = datetime.now()
testid = 2

test_obj = {
    "user_id": 4,
    "name": "Jacob",
    "event_type": "FACIAL_MATCH_SUCCESS",
    "timestamp": a
    }

test_file = {
    "image": ('Jacob-testuniqueid2', open('Screenshot_20220210-080248_Chrome.jpg', 'rb'), 'image/jpg')
}

x = requests.post(hardcoded_url, files=test_file, data=test_obj)
print(x.text)