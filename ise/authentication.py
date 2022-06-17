import requests
import urllib3
import base64
import json
import os
from dotenv import load_dotenv
from datetime import datetime
from getpass import getpass

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ISE_IP = "10.221.0.101:9060"
ISE_FQDN = "ise.dnaclab.net:9060"
ISE_USER = os.environ.get("USERNAME")
ISE_PASS = os.environ.get("PASSWORD")


def testAuthentication():
    # Enable if interactive authentication is required
    # username = input("Please input the ISE username: ")
    # password = getpass("Please input the ISE password: ")

    # Enable if credentials are present in the environment

    username = ISE_USER
    password = ISE_PASS

    auth2encode = username + ":" + password
    auth = base64.b64encode(auth2encode.encode('UTF-8')).decode('ASCII')
    url = "https://" + ISE_IP + "/ers/config/deploymentinfo/getAllInfo"
    headers = {
        "Accept": "application/json",
        "Authorization": "Basic " + auth,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers, verify = False)
    data = json.loads(response.content)
    print(json.dumps(data, indent = 4))

def main():
    testAuthentication()
    

if __name__ == "__main__":
    global script_run_time 
    script_run_time = datetime.now().strftime("%d-%B-%Y-%I-%M-%p")
    main()