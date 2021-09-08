from datetime import datetime
import os
import requests
import json

URL = "https://n313.meraki.com/api/v1/organizations"
API_KEY = "00f91d2d07f2e7fc7733f459086f3140b5fd41d9"
ENCODING = "application/json"
HEADERS = { "X-Cisco-Meraki-API-Key" : API_KEY , "Accept" : ENCODING }

def print_time_and_cwd():
    runtime = datetime.now()
    runtime_str = runtime.strftime("%d-%b-%Y-%H:%M:%S.%f")
    print(f"This script was run at {runtime_str} from " + os.getcwd() + ".\n")

def get_list_of_organizations():
    response = requests.request("GET", URL, headers = HEADERS)
    json_response = json.loads(response.text)
    return(json_response)

def print_list_of_organizations(organizations):
    for item in organizations:
        print("ID: " + item["id"] + "\n" + "NAME: " + item["name"] + "\n" + "URL: " + item["url"] + "\n") 

def print_networks_from_organization():
    org_id = input("\nPlease input the ID of the organziation you want to querry for networks: ")
    NETWORKS_URL = URL + "/" + org_id + "/networks"
    response = requests.request("GET", NETWORKS_URL, headers = HEADERS)
    json_response = json.loads(response.text)
    print("\n")
    for item in json_response:
        print(item["name"] + " " + item["id"])
    return(org_id)

def print_devices_from_network(org_id):
    network_id = input("\nPlease input the ID of the network you want to print devices for: ")
    DEVICES_URL = URL + "/" + org_id + "/networks/" + network_id + "/devices" 
    response = requests.request("GET", DEVICES_URL, headers = HEADERS)
    json_response = json.loads(response.text)
    print("\n")
    for item in json_response:
        print(item["model"] + " - " + item["serial"] + " - " + item["mac"] + " - " + item["url"])

def main():
    print("Hello from the main function!")
    print_time_and_cwd()
    organizations = get_list_of_organizations()
    print_list_of_organizations(organizations)
    org_id = print_networks_from_organization()
    print_devices_from_network(org_id)

if __name__ == "__main__":
    main()