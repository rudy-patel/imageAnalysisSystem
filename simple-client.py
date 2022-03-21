import requests
import argparse

# Argument parser
# ap = argparse.ArgumentParser()
# ap.add_argument("-s", "--server-ip", required=True, help="IP address of the server this client connects to")
# ap.add_argument("-p", "--port-number", required=True, help="Port of the server this client connects to (NOTE 5555, 5556)")
# args = vars(ap.parse_args())

# hardcoded_url = "http://{}:{}/pi".format(args["server-ip"], args["port-number"])
hardcoded_url = "http://127.0.0.1:5000/pi"

test_obj = {'requestkey': 'requestvalue'}

x = requests.post(hardcoded_url, data = test_obj)
print(x.text)