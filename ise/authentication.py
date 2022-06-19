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

ISE_IP = os.environ.get("IP")
ISE_FQDN = os.environ.get("FQDN")
ISE_USER = os.environ.get("USERNAME")
ISE_PASS = os.environ.get("PASSWORD")

AUTH2ENCODE = ISE_USER + ":" + ISE_PASS
AUTH = base64.b64encode(AUTH2ENCODE.encode('UTF-8')).decode('ASCII')
HEADERS = {
        "Accept": "application/json",
        "AUTHorization": "Basic " + AUTH,
        "Content-Type": "application/json"
    }

def testAuthentication(string: AUTH):
    # Enable if interactive authentication is required
    # username = input("Please input the ISE username: ")
    # password = getpass("Please input the ISE password: ")

    # Enable if credentials are present in the environment

    url = "https://" + ISE_IP + "/ers/config/deploymentinfo/getAllInfo"

    try:
        response = requests.get(url, headers=HEADERS, verify = False)
    except requests.exceptions.Timeout as e:
        print("Operation timed out!")
        raise SystemError(e)
    except requests.exceptions.ConnectionError as e:
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
    testAuthentication(AUTH)
    

if __name__ == "__main__":
    script_start_time = datetime.now()
    print(f'Script was started at {script_start_time.strftime("%d-%B-%Y-%I-%M-%p")}\n')
    main()
    script_end_time = datetime.now()
    print(f'\nScript was completed at {script_end_time.strftime("%d-%B-%Y-%I-%M-%p")}. \nTotal execution time was {script_end_time - script_start_time}')