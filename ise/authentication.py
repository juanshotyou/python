import requests
import urllib3
import base64
from datetime import datetime
from getpass import getpass

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ISE_IP = "10.221.0.101:9060"
ISE_FQDN = "ise.dnaclab.net:9060"


def testAuthentication():
    username = input("Please input the ISE username: ")
    password = getpass("Please input the ISE password: ")

    auth2encode = username + ":" + password
    auth = base64.b64encode(auth2encode.encode('UTF-8')).decode('ASCII')
    url = ISE_IP + "/ers/config/sessionservicenode/versioninfo"
    headers = {
        "Accept": "application/json",
        "Authorization": "Basic " + auth,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers, verify = False)
    prrint(response)

def main():
    testAuthentication()

if __name__ == "__main__":
    global script_run_time 
    script_run_time = datetime.now().strftime("%d-%B-%Y-%I-%M-%p")
    main()