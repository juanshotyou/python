import json
import os
import requests
from getpass import getpass
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

###Deletes all unused items from the FMC

#Check current working directory and make sure it's set as the working folder

path = os.getcwd()
print("\nInitial path was:", path)

os.chdir(os.path.dirname(os.path.abspath(__file__)))

path = os.getcwd()
print("\nNew path is:", path)

#Authenticate the session with the FMC

FMC_IP = input("Please input the IP address of the FMC: ")
FMC_USER = input("Please input the FMC username: ")
FMC_PASS = getpass("Please input the FMC password: ")

auth_url = "https://" + FMC_IP + "/api/fmc_platform/v1/auth/generatetoken"

response = requests.request("POST", auth_url, auth=(FMC_USER,FMC_PASS), verify=False)
print(f"Authentication result: {response.status_code}.")

domain = response.headers["DOMAIN_UUID"]
base_url = "https://" + FMC_IP + f"/api/fmc_config/v1/domain/{domain}/object/"
headers = {
    "X-auth-access-token": response.headers["X-auth-access-token"],
    'Content-Type': 'application/json'
}

#Download network groups, networks, hosts, FQDNs, URLs, ports

base_url = "https://" + FMC_IP
network_groups_url = base_url + f"/api/fmc_config/v1/domain/{domain}/object/networkgroups"
networks_url = base_url + f"/api/fmc_config/v1/domain/{domain}/object/networks"
hosts_url = base_url + f"/api/fmc_config/v1/domain/{domain}/object/hosts"
fqdns_url = base_url + f"/api/fmc_config/v1/domain/{domain}/object/fqdns"
urls_url = base_url + f"/api/fmc_config/v1/domain/{domain}/object/urls"
ports_url = base_url + f"/api/fmc_config/v1/domain/{domain}/object/portobjectgroups"
ranges_url = base_url + f"/api/fmc_config/v1/domain/{domain}/object/ranges"

all_objects_urls = [network_groups_url, networks_url, hosts_url, fqdns_url, urls_url, ports_url, ranges_url]

for item in all_objects_urls:
    url = item + "?limit=1000"
    response = requests.request("GET", url, headers = headers, verify = False)
    data = json.loads(response.content)
    if "items" in data:
        for subitem in data["items"]:
            object_to_delete = item + "/" + subitem["id"]
            response = requests.request("DELETE", object_to_delete, headers = headers, verify = False)
            print("Attempting to delete object:", subitem["name"], "\nResult:", response.status_code)
            if response.status_code >399 and response.status_code <500:
                reason = json.loads(response.content)
                reason_description = reason["error"]["messages"][0]["description"]
                print(f"Operation failed! Reason: {reason_description}","\n")