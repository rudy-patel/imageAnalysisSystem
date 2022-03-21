import requests
import argparse

hardcoded_url = "http://127.0.0.1:5000/pi"

test_obj = {'requestkey': 'requestvalue'}

x = requests.post(hardcoded_url, data = test_obj)
print(x.text)