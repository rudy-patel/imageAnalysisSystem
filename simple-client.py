import requests

hardcoded_url = "http://127.0.0.1:5000/1/facial-detection-event"

x = requests.get(hardcoded_url)
open('passed.pickle', 'wb').write(x.content)
