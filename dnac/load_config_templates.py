import requests
import os
import json
import base64
import urllib3
import sys
from dotenv import load_dotenv

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DNAC_IP = os.environ.get("IP")
DNAC_FQDN = os.environ.get("FQDN")
DNAC_USER = os.environ.get("USERNAME")
DNAC_PASS = os.environ.get("PASSWORD")

def getAuthenticationToken():
    url = "https://" + DNAC_IP + "/dna/system/api/v1/auth/token"
    auth2encode = DNAC_USER + ":" + DNAC_PASS
    auth = base64.b64encode(auth2encode.encode('UTF-8')).decode('ASCII')
    headers = {
            "Accept": "application/json",
            "Authorization": "Basic " + auth,
            "Content-Type": "application/json"
        }

    try:
        response = requests.post(url, headers=headers, verify = False)
    except requests.exceptions.Timeout as e:
        print("Operation timed out!")
        raise SystemError(e)
    except requests.exceptions.ConnectionError as e:
        print("Connection error - please check network connectivity!")
        raise SystemExit(e)
    except requests.exceptions.HTTPError as e:
        print("HTTP error encountered!")
        raise SystemExit(e)
    
    if response.status_code >=200 and response.status_code<=299:
        print("Authentication successfull!\n")
    else:
        print("Authentication failed! See message below for more info!\n", response.content)
        sys.exit()
    token = json.loads(response.content)

    return token["Token"]

def createProject(token):
    url = "https://" + DNAC_IP + "/dna/intent/api/v1/template-programmer/project"
    headers = {
        "Accept": "application/json",
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }
    body = {
        "description": "TEST",
        "name": "TEST",
    }

    try:
        response = requests.post(url, data=body, headers=headers, verify = False)
    except requests.exceptions.Timeout as e:
        print("Operation timed out!")
        raise SystemError(e)
    except requests.exceptions.ConnectionError as e:
        print("Connection error - please check network connectivity!")
        raise SystemExit(e)
    except requests.exceptions.HTTPError as e:
        print("HTTP error encountered!")
        raise SystemExit(e)
    print(response.content)

def main():
    token = getAuthenticationToken()
    createProject(token)

if __name__ == "__main__":
    main()