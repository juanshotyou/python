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

    try:
        response = requests.get(url, headers=headers, verify = False)
    except requests.exceptions.Timeout:
        print("Operation timed out!")
        raise SystemError(e)
    except requests.exceptions.ConnectionError:
        print("Connection error - please check network connectivity!")
        raise SystemExit(e)
    except requests.exceptions.HTTPError as e:
        print("HTTP error encountered!")
        raise SystemExit(e)
    data = json.loads(response.content)

    print(f'Authentication test successfull!\
        \nPrinting node information:\n\
        \nPID: { data["ERSDeploymentInfo"]["deploymentInfo"]["nodeList"]["nodeAndNodeCountAndCountInfo"][0]["value"]["content"][7]["value"] }\
        \nSN: { data["ERSDeploymentInfo"]["deploymentInfo"]["nodeList"]["nodeAndNodeCountAndCountInfo"][0]["value"]["content"][2]["value"] }\
        \nVersion: { data["ERSDeploymentInfo"]["deploymentInfo"]["nodeList"]["nodeAndNodeCountAndCountInfo"][0]["value"]["content"][5]["value"] }\
        \nPatch: { data["ERSDeploymentInfo"]["deploymentInfo"]["nodeList"]["nodeAndNodeCountAndCountInfo"][0]["value"]["content"][6]["value"] }\
        \nRoles enabled: { data["ERSDeploymentInfo"]["deploymentInfo"]["nodeList"]["nodeAndNodeCountAndCountInfo"][0]["value"]["content"][0]["value"] }\
        \nNodes in deployment: { data["ERSDeploymentInfo"]["deploymentInfo"]["nodeList"]["nodeAndNodeCountAndCountInfo"][2]["value"] }\
        ')

def main():
    testAuthentication()
    

if __name__ == "__main__":
    global script_run_time 
    script_run_time = datetime.now().strftime("%d-%B-%Y-%I-%M-%p")
    main()