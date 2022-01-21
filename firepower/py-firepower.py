import requests
import urllib3
import base64
import sys
import json
from datetime import datetime
from getpass import getpass
from simple_term_menu import TerminalMenu

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def getTokenAndDomain():

    username = input("Please input the FMC username: ")
    password = getpass("Please input the FMC password: ")
    
    auth2encode = username + ":" + password
    auth = base64.b64encode(auth2encode.encode('UTF-8')).decode('ASCII')

    url = base_url + "/api/fmc_platform/v1/auth/generatetoken"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic " + auth
    }
    response = requests.request("POST", url, headers = headers, verify = False)

    if response.status_code == 204:
        print("\n## Authentication successfull!\n")
        return response.headers["X-auth-access-token"], response.headers["DOMAIN_UUID"]
    else:
        print("\n## Authentication failed! Terminating script!\n")
        sys.exit()

def getDevices():

    devices = []

    url = base_url + "/api/fmc_config/v1/domain/" + domain_uuid + "/devices/devicerecords"
    response = requests.request("GET", url, headers = headers, verify = False)

    if response.status_code == 200:
        print("\n## Device list retrieved successfully!\n")
    else:
        print("\n## Error while retrieving device list! Terminating script!\n")
        sys.exit()

    formatted_response = json.loads(response.text)

    for item in formatted_response["items"]:
        devices.append(item)

    return devices

def getAccessPolicies():

    policies = []

    url = base_url + "/api/fmc_config/v1/domain/" + domain_uuid + "/policy/accesspolicies"
    response = requests.request("GET", url, headers = headers, verify = False)

    if response.status_code == 200:
        print("\n## Policies list retrieved successfully!\n")
    else:
        print("\n## Error while retrieving policies list! Terminating script!\n")
        sys.exit()

    formatted_response = json.loads(response.text)

    for item in formatted_response["items"]:
        policies.append(item["id"])

    return policies

def getAccessPoliciesContents(policies:list):

    policy_contents = []

    for policy_id in policies:
        url = base_url + "/api/fmc_config/v1/domain/" + domain_uuid + "/policy/accesspolicies/" + policy_id + "/accessrules?expanded=true"
        response = requests.request("GET", url, headers = headers, verify = False)

        if response.status_code == 200:
            print(f"\n## Access rule for policy {policy_id} retrieved successfully!\n")
        else:
            print("\n## Error while retrieving policies contents! Terminating script!\n")
            sys.exit()

        formatted_response = json.loads(response.text)

        policy_contents.append("Start of rules for policy - " + policy_id)
        if "items" in formatted_response:
            policy_contents.append(formatted_response["items"])
        else:
            policy_contents.append("This policy is empty")

    return policy_contents

def printAccessPolicyContents(policy_contents:list):

    for item in policy_contents:
        if "Start" in item or "empty" in item:
            print(item)
        else:
            for i in range(len(item)):
                print(json.dumps(item[i], indent = 4))

def createNetworkObject():

    #Unused function

    obj_name = input("Please input a name for this network object (no spaces allowed): ")
    obj_value = input("Please input the value for this network object (formatted as X.X.X.X/YY): ")
    obj_description = input("Please input a description for this network object: ")

    network_object = {
        "name" : obj_name,
        "value" : obj_value,
        "overridable" : False,
        "description" : obj_description,
        "type" : "Network"
    }

    print("Your object is\n\n", json.dumps(network_object, indent = 4), "\n")

    deploy_object = input("Input 1 if you would like to deploy this object or anything else to discard it: ")
    if deploy_object == "1":
        try:
            url = base_url + "/api/fmc_config/v1/domain/" + domain_uuid + "/object/networks"
            response = requests.request("POST", url, headers = headers, data = json.dumps(network_object), verify = False)
            print(f"\nThe request returned status code {response.status_code}.")
            if response.status_code == 201 or response.status_code == 202:
                print("Object successfully deployed!")
            else:
                response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print("Reason Code: " + str(err))
        finally:
            if response:
                response.close()

def getNetworkObjects():

    #Unused function

    url = base_url + "/api/fmc_config/v1/domain/" + domain_uuid + "/object/networks"
    response = requests.request("GET", url, headers = headers, verify = False)

    network_objects = json.loads(response.text)

    print("Currently configured objects in FMC:\n")
    for item in network_objects["items"]:
        print(json.dumps(item, indent=4))

    return network_objects

def getAllObjects():

    result = 0

    network_objects_url = base_url + "/api/fmc_config/v1/domain/" + domain_uuid + "/object/networks?expanded=true"
    host_objects_url = base_url + "/api/fmc_config/v1/domain/" + domain_uuid + "/object/hosts?expanded=true"
    group_objects_url = base_url + "/api/fmc_config/v1/domain/" + domain_uuid + "/object/networkgroups?expanded=true"
    url_objects_url = base_url + "/api/fmc_config/v1/domain/" + domain_uuid + "/object/urls?expanded=true"
    fqdn_objects_url = base_url + "/api/fmc_config/v1/domain/" + domain_uuid + "/object/fqdns?expanded=true"

    required_data = [network_objects_url, host_objects_url, group_objects_url, url_objects_url, fqdn_objects_url]
    objects = []

    for item in required_data:
        response = requests.get(item, headers = headers, verify = False)
        
        if response.status_code == 200:
            result+=1
        else:
            print("\nThere was an error while retrieving some of the objects!\n")
        
        json_response = json.loads(response.text)
        objects.append(json_response["items"])

    if result == 5:
        print("\n## Objects successfully downloaded!\n")
    elif result <= 0:
        print("\n## Objects downloaded with some errors. Please check the downloaded data manually.\n")
    else:
        print("\## An error was encountered during the download. No objects have been retrieved.\n")
    result = 0

    return objects

def main():

    global base_url, token, domain_uuid, headers

    has_authenticated = False
    devices, policies, policy_contents, objects = [], [], [], []

    #Initialize the menu

    menu_choice_list = [
        "1. Authenticate to FMC", 
        "2. Download device list", 
        "3. Download access policies list and contents",
        "4. Download objects (host, network, group, FQDN and URL)",
        "5. Export all downloaded information to local file",
        "6. Print all downloaded information to terminal",
        "7. Exit script"
        ]
    menu_exit = False
    terminal_menu = TerminalMenu(menu_choice_list, title = "FMC data exporter (JSON formatted)")

    while not menu_exit:
        menu_choice = terminal_menu.show()

        if menu_choice == 0:
            ip_address = input("Please input the FMC IP address: ")
            base_url = "https://" + ip_address
            token, domain_uuid = getTokenAndDomain()
            headers = {
                "Content-Type" : "application/json",
                "X-auth-access-token" : token
            }
            has_authenticated = True

        elif menu_choice == 1:
            if not has_authenticated:
                print("Session needs to be authenticated before data can be downloaded.")
            else:
                devices = getDevices()

        elif menu_choice == 2:
            if not has_authenticated:
                print("Session needs to be authenticated before data can be downloaded.")
            else:
                policies = getAccessPolicies()
                policy_contents = getAccessPoliciesContents(policies)

        elif menu_choice == 3:
            if not has_authenticated:
                print("Session needs to be authenticated before data can be downloaded.")
            else:
                objects = getAllObjects()

        elif menu_choice == 4:
            if not has_authenticated:
                print("Session needs to be authenticated before data can be downloaded and saved.")
            else:
                data_export_list = [devices, policies, policy_contents, objects]
                with open("FMC-configuration-data-" + script_run_time + ".txt", "a+") as file:
                    for item in data_export_list:
                        json.dump(item, file, indent = 2)
                        file.write("\n================================================================\n")

        elif menu_choice == 5:
            if not has_authenticated:
                print("Session needs to be authenticated before data can be downloaded and saved.")
            else:
                data_export_list = [devices, policies, policy_contents, objects]
                print(f"\nThe following information has been downloaded from the FMC at {ip_address}:")
                print("\nRegistered devices:\n\n", json.dumps(devices, indent = 2),"\n")
                print("\nPolicy IDs:\n\n", json.dumps(policies, indent = 2),"\n")
                print("\nPolicy contents:\n\n", json.dumps(policy_contents, indent = 2),"\n")
                print("\nObjects:\n\n", json.dumps(objects, indent = 2),"\n")

        elif menu_choice == 6:
            menu_exit = True
   
    
    
    # printAccessPolicyContents(policy_contents)

    # createNetworkObject()

if __name__ == "__main__":
    script_run_time = datetime.now().strftime("%d-%B-%Y-%I-%M-%p")
    main()