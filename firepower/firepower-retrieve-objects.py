import requests
import json
from datetime import datetime
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
SCRIPT_RUN_TIME = datetime.now().strftime("%d-%B-%Y-%I-%M-%p")

#Get FMC IP and credentials and prepare auth cookie

FMC_IP = input("\nPlease input the IP address of the FMC: ")
USER = input("\nPlease input the username for the FMC: ")
PASS = input("\nPlease input the password for the FMC: ")

#Authenticate the session, retrieve domain UUID and print result

AUTH_URL = "https://" + FMC_IP + "/api/fmc_platform/v1/auth/generatetoken"
AUTH_RESPONSE = requests.post(AUTH_URL, auth = (USER, PASS), verify = False)

AUTH_TOKEN = AUTH_RESPONSE.headers["X-auth-access-token"]
AUTH_REFRESH_TOKEN = AUTH_RESPONSE.headers["X-auth-refresh-token"]
DOMAIN_UUID = AUTH_RESPONSE.headers["DOMAIN_UUID"]
HEADERS = {"X-auth-access-token" : AUTH_TOKEN}

print("\nOperation returned code", AUTH_RESPONSE.status_code, "\n")

#Prepare the URL and send the request for the objects

NETWORK_OBJECTS_URL = "https://" + FMC_IP + "/api/fmc_config/v1/domain/" + DOMAIN_UUID + "/object/networks?expanded=true"
HOST_OBJECTS_URL = "https://" + FMC_IP + "/api/fmc_config/v1/domain/" + DOMAIN_UUID + "/object/hosts?expanded=true"
GROUP_OBJECTS_URL = "https://" + FMC_IP + "/api/fmc_config/v1/domain/" + DOMAIN_UUID + "/object/networkgroups?expanded=true"
URL_OBJECTS_URL = "https://" + FMC_IP + "/api/fmc_config/v1/domain/" + DOMAIN_UUID + "/object/urls?expanded=true"
FQDN_OBJECTS_URL = "https://" + FMC_IP + "/api/fmc_config/v1/domain/" + DOMAIN_UUID + "/object/fqdns?expanded=true"

REQUIRED_DATA = (NETWORK_OBJECTS_URL, HOST_OBJECTS_URL, GROUP_OBJECTS_URL, URL_OBJECTS_URL, FQDN_OBJECTS_URL)
RECEIVED_DATA = []

for item in REQUIRED_DATA:
    response = requests.get(item, headers = HEADERS, verify = False)
    json_response = json.loads(response.text)
    RECEIVED_DATA.append(json_response["items"])


for item in RECEIVED_DATA:
    if item[0]["type"] == "Network":
        with open("network-objects-" + SCRIPT_RUN_TIME + ".txt", "a+") as file:
            json.dump(item, file, indent = 2)
    elif item[0]["type"] == "Host":
        with open("host-objects-" + SCRIPT_RUN_TIME + ".txt", "a+") as file:
            json.dump(item, file, indent = 2)
    elif item[0]["type"] == "NetworkGroup":
        with open("group-objects-" + SCRIPT_RUN_TIME + ".txt", "a+") as file:
            json.dump(item, file, indent = 2)
    elif item[0]["type"] == "Url":
        with open("url-objects-" + SCRIPT_RUN_TIME + ".txt", "a+") as file:
            json.dump(item, file, indent = 2)
    elif item[0]["type"] == "FQDN":
        with open("fqdn-objects-" + SCRIPT_RUN_TIME + ".txt", "a+") as file:
            json.dump(item, file, indent = 2)
