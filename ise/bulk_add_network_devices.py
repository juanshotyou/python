from pipes import Template
import requests
import urllib3
import base64
import json
import os
import pandas as pd
import jinja2
import sys
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

def getNetworkDevices():
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

def createObjectFromTemplate(object_data) -> dict:
    # This function takes the information for a network device object as inputs and
    # returns a dictionary that can be used in the API call.

    # Default values are declared in the Jinja template.

    NETWORK_DEVICE = """{
        "NetworkDevice":
            {
                "authenticationSettings": {{ name }},
                "snmpsettings": {},
                "trustsecsettings": {
                    "deviceAuthenticationSettings": {},
                    "sgaNotificationAndUpdates": {},
                    "deviceConfigurationDeployment": {}
                        },
                "tacacsSettings": {},
                "NetworkDeviceIPList": [{}],
                "NetworkDeviceGroupList": {}
                }}
    """

    J2_NETWORK_DEVICE = Template(NETWORK_DEVICE)
    return J2_NETWORK_DEVICE.render(object_data)

def buildNetworkDeviceObject(name, ipaddress, description, serialnumber, snmp_string, radius_secret, tacacs_secret, enable_secret, device_user, device_pass):
    # This function includes hard-coded values which apply to the DNACLAB envrionment only. Edit the values here as needed.
    # e.g. CoA port is referenced in the following line:
    #
    # network_device["NetworkDevice"]["coaPort"] = 1700
    # and is hard-coded to be 1700. This can be changed to any port needed for the deplyment this script will be used on.

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
    network_device["NetworkDevice"]["name"] = name
    network_device["NetworkDevice"]["description"] = description
    network_device["NetworkDevice"]["authenticationSettings"]["networkProtocol"] = "RADIUS"
    network_device["NetworkDevice"]["authenticationSettings"]["radiusSharedSecret"] = radius_secret
    network_device["NetworkDevice"]["snmpsettings"]["version"] = "TWO_C"
    network_device["NetworkDevice"]["snmpsettings"]["roCommunity"] = snmp_string
    network_device["NetworkDevice"]["snmpsettings"]["securityLevel"] = "NO_AUTH"
    network_device["NetworkDevice"]["snmpsettings"]["privacyProtocol"] = "TRIPLE_DES"
    network_device["NetworkDevice"]["snmpsettings"]["pollingInterval"] = 0
    network_device["NetworkDevice"]["snmpsettings"]["linkTrapQuery"] = False
    network_device["NetworkDevice"]["snmpsettings"]["macTrapQuery"] = False
    network_device["NetworkDevice"]["snmpsettings"]["originatingPolicyServicesNode"] = "Auto"
    network_device["NetworkDevice"]["trustsecsettings"]["deviceAuthenticationSettings"]["sgaDeviceId"] = serialnumber
    network_device["NetworkDevice"]["trustsecsettings"]["deviceAuthenticationSettings"]["sgaDevicePassword"] = serialnumber
    network_device["NetworkDevice"]["trustsecsettings"]["sgaNotificationAndUpdates"]["downlaodEnvironmentDataEveryXSeconds"] = 86400
    network_device["NetworkDevice"]["trustsecsettings"]["sgaNotificationAndUpdates"]["downlaodPeerAuthorizationPolicyEveryXSeconds"] = 86400
    network_device["NetworkDevice"]["trustsecsettings"]["sgaNotificationAndUpdates"]["reAuthenticationEveryXSeconds"] = 86400
    network_device["NetworkDevice"]["trustsecsettings"]["sgaNotificationAndUpdates"]["downloadSGACLListsEveryXSeconds"] = 86400
    network_device["NetworkDevice"]["trustsecsettings"]["sgaNotificationAndUpdates"]["otherSGADevicesToTrustThisDevice"] = True
    network_device["NetworkDevice"]["trustsecsettings"]["sgaNotificationAndUpdates"]["sendConfigurationToDevice"] = True
    network_device["NetworkDevice"]["trustsecsettings"]["sgaNotificationAndUpdates"]["sendConfigurationToDeviceUsing"] = "ENABLE_USING_COA"
    network_device["NetworkDevice"]["trustsecsettings"]["sgaNotificationAndUpdates"]["coaSourceHost"] = "ISE.dnaclab.net"
    network_device["NetworkDevice"]["trustsecsettings"]["deviceConfigurationDeployment"]["includeWhenDeployingSGTUpdates"] = True
    network_device["NetworkDevice"]["trustsecsettings"]["deviceConfigurationDeployment"]["enableModePassword"] = enable_secret
    network_device["NetworkDevice"]["trustsecsettings"]["deviceConfigurationDeployment"]["execModeUsername"] = device_user
    network_device["NetworkDevice"]["trustsecsettings"]["deviceConfigurationDeployment"]["execModePassword"] = device_pass
    network_device["NetworkDevice"]["tacacsSettings"]["sharedSecret"] = tacacs_secret
    network_device["NetworkDevice"]["tacacsSettings"]["connectModeOptions"] = "ON_LEGACY"
    network_device["NetworkDevice"]["profileName"] = "Cisco"
    network_device["NetworkDevice"]["coaPort"] = 1700
    network_device["NetworkDevice"]["NetworkDeviceIPList"][0]["ipaddress"] = ipaddress
    network_device["NetworkDevice"]["NetworkDeviceIPList"][0]["mask"] = 32
    network_device["NetworkDevice"]["NetworkDeviceGroupList"] = ["Location#All Locations", "Device Type#All Device Types", "IPSEC#Is IPSEC Device#No"]

    return network_device


def addNetworkDeviceManually():
    url = "https://" + ISE_IP + "/ers/config/networkdevice/"

    network_device_name = input("Name: ")
    network_device_description = input("Description: ")
    network_device_radius = input("RADIUS key: ")
    network_device_snmp = input("SNMP RO key: ")
    network_device_serial = input("TrustSec ID: ")
    network_device_enable = input("Enable secret: ")
    network_device_user = input("TACACS username: ")
    network_device_pass = input("TACACS password: ")
    network_device_tacacs = input("TACACS key: ")
    network_device_ip = input("IP address: ")

    network_device = buildNetworkDeviceObject(network_device_name, network_device_ip, network_device_description, network_device_serial, network_device_snmp, network_device_radius, network_device_tacacs, network_device_enable, network_device_user, network_device_pass)

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
    # Common parameters used to create network device - edit as needed

    network_device_description = "Added via network automation - index "
    network_device_serial = "FXCV12345" 
    network_device_snmp = "SNMPString" 
    network_device_radius = "RADIUSKey" 
    network_device_tacacs = "TACACSKey" 
    network_device_enable = "EnableKey" 
    network_device_user = "Username" 
    network_device_pass = "Password"

    index = 0
    network_device = {}
    url = "https://" + ISE_IP + "/ers/config/networkdevice/"

    data_sources = os.listdir(os.getcwd() + "/data_sources")
    if len(data_sources)>=2:
        print("Only one .csv or .xlsx file must be present in the \"data_sources\" folder!\nPlease place in the folder only one file containing the devices you want to add to ISE and re-run the script.\nTerminating!")
        sys.exit()
    elif len(data_sources)==0:
        print("No file found in the \"data_sources\" folder!\nPlease place in the folder a .csv or .xlsx file containing the devices you want to add to ISE and re-run the script.\nTerminating!")
        sys.exit()
    file_path = os.getcwd() + "/data_sources/" + data_sources[0]
    file_type = os.path.splitext(data_sources[0])[1]

    if file_type == ".xlsx":
        network_devices = pd.read_excel(file_path)
    elif file_type == ".csv":
        network_devices = pd.read_csv(file_path)
    else:
        print("No supported files found in the data sources directory. \nPlease check the directory contents and try again!\nTerminating script!")
        sys.exit()

    for device in range(len(network_devices)):
            index += 1
            network_device = buildNetworkDeviceObject(network_devices.iloc[device][0], network_devices.iloc[device][1], network_device_description + str(index), network_device_serial + str(index), network_device_snmp, network_device_radius, network_device_tacacs, network_device_enable, network_device_user, network_device_pass)
            try:
                response = requests.post(url, headers=HEADERS, data=json.dumps(network_device), verify = False)
                if response.status_code >= 200 and response.status_code <= 299:
                    print(f"Device {network_devices.iloc[device][0]} was created successfully!")
                else:
                    print(f"\nAn error was encountered while trying to create device {network_devices.iloc[device][0]}. See below for more info:\n", json.dumps(json.loads(response.content), indent = 4))
            except requests.exceptions.Timeout as e:
                print("Operation timed out!")
                raise SystemError(e)
            except requests.exceptions.ConnectionError as e:
                print("Connection error - please check network connectivity!")
                raise SystemExit(e)
            except requests.exceptions.HTTPError as e:
                print("HTTP error encountered!")
                raise SystemExit(e)
            network_device = {}
def main():
    # network_devices = getNetworkDevices()
    # addNetworkDeviceManually()
    addNetworkDevicesFromFile()
    
if __name__ == "__main__":
    script_start_time = datetime.now()
    print(f'Script was started at {script_start_time.strftime("%d-%B-%Y-%I-%M-%p")}\n')
    main()
    script_end_time = datetime.now()
    print(f'\nScript was completed at {script_end_time.strftime("%d-%B-%Y-%I-%M-%p")}. \nTotal execution time was {script_end_time - script_start_time}')