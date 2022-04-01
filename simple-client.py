import requests
from datetime import datetime

hardcoded_url = "http://127.0.0.1:5000/v1/heartbeat/1"

x = requests.get(hardcoded_url)
open('passed.pickle', 'wb').write(x.content)

# print(x.text)