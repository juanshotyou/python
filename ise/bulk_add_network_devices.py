import requests
import urllib3
import base64
import json
import os
from dotenv import load_dotenv
from datetime import datetime

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

def getNetworkDevices(string: AUTH):
    url = "https://" + ISE_IP + "/ers/config/networkdevice"

    network_devices = []

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

    for item in data["SearchResult"]["resources"]:
        url = "https://" + ISE_IP + "/ers/config/networkdevice/" + item["id"]
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
        network_devices.append(json.loads(response.content))
        # print(json.dumps(json.loads(response.content), indent =4))
        # data = json.loads(response.content)

    return network_devices


def addNetworkDeviceManually(string: AUTH):
    url = "https://" + ISE_IP + "/ers/config/networkdevice/"

    network_device = {"NetworkDevice": \
        {\
            "authenticationSettings": {},\
            "snmpsettings": {},\
            "trustsecsettings": {\
                "deviceAuthenticationSettings": {},\
                "sgaNotificationAndUpdates": {},\
                "deviceConfigurationDeployment": {}\
                    },\
            "tacacsSettings": {},\
            "NetworkDeviceIPList": [{}],\
            "NetworkDeviceGroupList": {}\
            }}

    print('Please provide the following details for the network device you wish to add to ISE:\
        \n-name\
        \n-description\
        \n-authentication settings\
        \n-SNMP settings\
        \n-TrustSec settings\
        \n-TACACS settings\
        \n-profile name\
        \n-CoA port\
        \n-device IPs list\
        \n-device group list\
        \n')

    network_device["NetworkDevice"]["name"] = input("Name: ")
    network_device["NetworkDevice"]["description"] = input("Description: ")
    network_device["NetworkDevice"]["authenticationSettings"]["networkProtocol"] = "RADIUS"
    network_device["NetworkDevice"]["authenticationSettings"]["radiusSharedSecret"] = input("RADIUS key: ")
    network_device["NetworkDevice"]["snmpsettings"]["version"] = "TWO_C"
    network_device["NetworkDevice"]["snmpsettings"]["roCommunity"] = input("SNMP RO key: ")
    network_device["NetworkDevice"]["snmpsettings"]["securityLevel"] = "NO_AUTH"
    network_device["NetworkDevice"]["snmpsettings"]["privacyProtocol"] = "TRIPLE_DES"
    network_device["NetworkDevice"]["snmpsettings"]["pollingInterval"] = 0
    network_device["NetworkDevice"]["snmpsettings"]["linkTrapQuery"] = False
    network_device["NetworkDevice"]["snmpsettings"]["macTrapQuery"] = False
    network_device["NetworkDevice"]["snmpsettings"]["originatingPolicyServicesNode"] = "Auto"
    network_device["NetworkDevice"]["trustsecsettings"]["deviceAuthenticationSettings"]["sgaDeviceId"] = input("TrustSec ID: ")
    network_device["NetworkDevice"]["trustsecsettings"]["deviceAuthenticationSettings"]["sgaDevicePassword"] = input("TrustSec password: ")
    network_device["NetworkDevice"]["trustsecsettings"]["sgaNotificationAndUpdates"]["downlaodEnvironmentDataEveryXSeconds"] = 86400
    network_device["NetworkDevice"]["trustsecsettings"]["sgaNotificationAndUpdates"]["downlaodPeerAuthorizationPolicyEveryXSeconds"] = 86400
    network_device["NetworkDevice"]["trustsecsettings"]["sgaNotificationAndUpdates"]["reAuthenticationEveryXSeconds"] = 86400
    network_device["NetworkDevice"]["trustsecsettings"]["sgaNotificationAndUpdates"]["downloadSGACLListsEveryXSeconds"] = 86400
    network_device["NetworkDevice"]["trustsecsettings"]["sgaNotificationAndUpdates"]["otherSGADevicesToTrustThisDevice"] = True
    network_device["NetworkDevice"]["trustsecsettings"]["sgaNotificationAndUpdates"]["sendConfigurationToDevice"] = True
    network_device["NetworkDevice"]["trustsecsettings"]["sgaNotificationAndUpdates"]["sendConfigurationToDeviceUsing"] = "ENABLE_USING_COA"
    network_device["NetworkDevice"]["trustsecsettings"]["sgaNotificationAndUpdates"]["coaSourceHost"] = "ISE.dnaclab.net"
    network_device["NetworkDevice"]["trustsecsettings"]["deviceConfigurationDeployment"]["includeWhenDeployingSGTUpdates"] = True
    network_device["NetworkDevice"]["trustsecsettings"]["deviceConfigurationDeployment"]["enableModePassword"] = input("Enable secret: ")
    network_device["NetworkDevice"]["trustsecsettings"]["deviceConfigurationDeployment"]["execModeUsername"] = input("TACACS username: ")
    network_device["NetworkDevice"]["trustsecsettings"]["deviceConfigurationDeployment"]["execModePassword"] = input("TACACS password: ")
    network_device["NetworkDevice"]["tacacsSettings"]["sharedSecret"] = input("TACACS key: ")
    network_device["NetworkDevice"]["tacacsSettings"]["connectModeOptions"] = "ON_LEGACY"
    network_device["NetworkDevice"]["profileName"] = "Cisco"
    network_device["NetworkDevice"]["coaPort"] = 1700
    network_device["NetworkDevice"]["NetworkDeviceIPList"][0]["ipaddress"] = input("IP address: ")
    network_device["NetworkDevice"]["NetworkDeviceIPList"][0]["mask"] = 32
    network_device["NetworkDevice"]["NetworkDeviceGroupList"] = ["Location#All Locations", "Device Type#All Device Types", "IPSEC#Is IPSEC Device#No"]

    print("The following object is ready for deployment:\n")
    print(json.dumps(network_device, indent =4))
    decision = input("Type \"YES\" (without quotes) to load the object: ")
    if decision=="YES":
        try:
            response = requests.post(url, headers=HEADERS, data=json.dumps(network_device), verify = False)
            if response.status_code >= 200 and response.status_code <= 299:
                print(f"\nNetwork device created successfully!")
            else:
                print("\nAn error was encountered while trying to create the network device. See below for more info:\n", json.dumps(json.loads(response.content), indent = 4))
        except requests.exceptions.Timeout as e:
            print("Operation timed out!")
            raise SystemError(e)
        except requests.exceptions.ConnectionError as e:
            print("Connection error - please check network connectivity!")
            raise SystemExit(e)
        except requests.exceptions.HTTPError as e:
            print("HTTP error encountered!")
            raise SystemExit(e)
    else:
        print("Operation aborted!")

def addNetworkDevicesFromFile():

def main():
    # network_devices = getNetworkDevices(AUTH)
    # addNetworkDeviceManually(AUTH)
    addNetworkDevicesFromFile():
    
if __name__ == "__main__":
    script_start_time = datetime.now()
    print(f'Script was started at {script_start_time.strftime("%d-%B-%Y-%I-%M-%p")}\n')
    main()
    script_end_time = datetime.now()
    print(f'\nScript was completed at {script_end_time.strftime("%d-%B-%Y-%I-%M-%p")}. \nTotal execution time was {script_end_time - script_start_time}')