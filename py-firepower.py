import requests
import urllib3
import base64
import sys
import json
from getpass import getpass

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def getTokenAndDomain(base_url:str):

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

def getDevices(token:str, domain_uuid:str, base_url:str):

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
    #print(formatted_response["items"])
    #print(json.dumps(formatted_response, indent=4))

def getAccessPolicies(token:str, domain_uuid:str, base_url:str):

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

def getAccessPoliciesContent(token:str, domain_uuid:str, base_url:str, policies:list):

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


def main():

    ip_address = input("Please input the FMC IP address: ")
    base_url = "https://" + ip_address

    token, domain_uuid = getTokenAndDomain(base_url)
    devices = getDevices(token, domain_uuid, base_url)
    policies = getAccessPolicies(token, domain_uuid, base_url)
    policy_contents = getAccessPoliciesContent(token, domain_uuid, base_url, policies)
    
    printAccessPolicyContents(policy_contents)

if __name__ == "__main__":
    main()