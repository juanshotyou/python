import requests
import urllib3
import base64
import sys
import json
from getpass import getpass

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
    response = requests.request("POST", url, headers=headers, verify=False)

    if response.status_code == 204:
        print("\nAuthorization successfull!\n")
        return response.headers["X-auth-access-token"], response.headers["DOMAIN_UUID"]
    else:
        print("\nAuthentication failed! Terminating script!\n")
        sys.exit()

def getDevices():

    devices = []

    url = base_url + "/api/fmc_config/v1/domain/" + domain_uuid + "/devices/devicerecords"
    headers = {
        "Content-Type" : "application/json",
        "X-auth-access-token" : token
    }
    response = requests.request("GET", url, headers=headers, verify=False)

    if response.status_code == 200:
        print("\nDevice list retrieved successfully!\n")
    else:
        print("\nError while retrieving device list! Terminating script!\n")
        sys.exit()

    formatted_response = json.loads(response.text)

    for item in formatted_response["items"]:
        devices.append(item)

    return devices

def getAccessPolicies():

    policies = []

    url = base_url + "/api/fmc_config/v1/domain/" + domain_uuid + "/policy/accesspolicies"
    headers = {
        "Content-Type" : "application/json",
        "X-auth-access-token" : token
    }
    response = requests.request("GET", url, headers=headers, verify=False)

    if response.status_code == 200:
        print("\nPolicies list retrieved successfully!\n")
    else:
        print("\nError while retrieving policies list! Terminating script!\n")
        sys.exit()

    formatted_response = json.loads(response.text)

    for item in formatted_response["items"]:
        policies.append(item["id"])

    return policies

def getAccessPoliciesContents(policies:list):

    policy_contents = []

    for policy_id in policies:
        url = base_url + "/api/fmc_config/v1/domain/" + domain_uuid + "/policy/accesspolicies/" + policy_id + "/accessrules?expanded=true"
        headers = {
            "Content-Type" : "application/json",
            "X-auth-access-token" : token
        }
        response = requests.request("GET", url, headers=headers, verify=False)

        if response.status_code == 200:
            print(f"\nAccess rule for policy {policy_id} retrieved successfully!\n")
        else:
            print("\nError while retrieving policies contents! Terminating script!\n")
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
                print(json.dumps(item[i], indent=4))

def createNetworkObject():

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

    print("Your object is\n\n", json.dumps(network_object, indent=4), "\n")

    deploy_object = input("Input 1 if you would like to deploy this object or anything else to discard it: ")
    if deploy_object == "1":
        try:
            url = base_url + "/api/fmc_config/v1/domain/" + domain_uuid + "/object/networks"
            headers = {
                "Content-Type" : "application/json",
                "X-auth-access-token" : token
            }
            response = requests.request("POST", url, headers=headers, data=json.dumps(network_object), verify=False)
            print(f"The request returned status code {response.status_code}.")
            if response.status_code == 201 or response.status_code == 202:
                print("Object successfully deployed!")
            else:
                response.raise_for_status()
            print(json.loads(response.text))
        except requests.exceptions.HTTPError as err:
            print("Reason Code: " + str(err))
        finally:
            if response:
                response.close()

def getNetworkObjects():

    url = base_url + "/api/fmc_config/v1/domain/" + domain_uuid + "/object/networks"
    headers = {
        "Content-Type" : "application/json",
        "X-auth-access-token" : token
    }
    response = requests.request("GET", url, headers=headers, verify=False)

    formatted_response = json.loads(response.text)

    print("Currently configured objects in FMC:\n")
    for item in formatted_response["items"]:
        print(json.dumps(item, indent=4))

    return formatted_response

def main():

    global base_url, token, domain_uuid

    ip_address = input("Please input the FMC IP address: ")
    base_url = "https://" + ip_address
    token, domain_uuid = getTokenAndDomain()
    devices = getDevices()
    policies = getAccessPolicies()
    policy_contents = getAccessPoliciesContents(policies)
    
    printAccessPolicyContents(policy_contents)

    createNetworkObject()
    network_objects = getNetworkObjects()

if __name__ == "__main__":
    main()