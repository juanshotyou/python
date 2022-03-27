import json
import os
import requests
from datetime import datetime
from netaddr import IPAddress
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

SCRIPT_RUN_TIME = datetime.now().strftime("%d-%B-%Y-%I-%M-%p")
print(f"\nScript started at {SCRIPT_RUN_TIME}\n")

FMC_IP = "172.16.2.101"
FMC_USER = "apiuser"
FMC_PASS = "apipass"

###NOTE - the tool is designed for Eric Wright's requirements (no ipv6 objects, limited subset of object groups)
### This is not a universal migration tool.

# Check current working directory and make sure it's set as the working folder

path = os.getcwd()
print("\nInitial path was:", path)

os.chdir(os.path.dirname(os.path.abspath(__file__)))

path = os.getcwd()
print("\nNew path is:", path)

###OBJECTS###

# Get the objects filename and read the data

filename = input("\nPlease input the name of the file storing the network objects.\nMake sure to include the file extension: ")

with open(filename) as f:
    sonicwall_objects = json.load(f)

# Loop through the objects list and create Firepower equivalent

index = 0
successes = 0
failures = 0

ipv4_host_object = {}
ipv4_network_object = {}
ipv4_range_object = {}
ipv4_host_object_list = []
ipv4_network_object_list = []
ipv4_range_object_list = []
fqdn_object = {}
fqdn_objects_list = []

for item in sonicwall_objects["address_objects"]:
    if "ipv4" in item:
        if "host" in item["ipv4"] and item["ipv4"]["host"] != {}:
            ipv4_host_object["type"] = "Host"
            ipv4_host_object["value"] = item["ipv4"]["host"]["ip"]
            ipv4_host_object["name"] = item["ipv4"]["name"]
            ipv4_host_object["description"] = "Added via the FMC API with index " + str(index)
            ipv4_host_object_list.append(ipv4_host_object)
            ipv4_host_object = {}
            successes+=1
        elif "network" in item["ipv4"] and item["ipv4"]["network"] != {}:
            ipv4_network_object["type"] = "Network"
            ipv4_network_object["value"] = item["ipv4"]["network"]["subnet"] + "/" + str(IPAddress(item["ipv4"]["network"]["mask"]))
            ipv4_network_object["name"] = item["ipv4"]["name"]
            ipv4_network_object["description"] = "Added via the FMC API with index " + str(index)
            ipv4_network_object_list.append(ipv4_network_object)
            ipv4_network_object = {}
            successes+=1
        elif "range" in item["ipv4"]:
            ipv4_range_object["type"] = "Range"
            ipv4_range_object["value"] = item["ipv4"]["range"]["begin"] + "-" + item["ipv4"]["range"]["end"]
            ipv4_range_object["name"] = item["ipv4"]["name"]
            ipv4_range_object["description"] = "Added via the FMC API with index " + str(index)
            ipv4_range_object_list.append(ipv4_range_object)
            ipv4_range_object = {}
            successes+=1
        else:
            print(f"\nItem at index {index} does not meet criteria so it has been ignored.")
            print("Offending item: \n", item["ipv4"])
            failures+=1
    if "mac" in item:
        print(f"\nItem at index {index} does not meet criteria so it has been ignored.")
        print("Offending item: \n", item["mac"])
        failures+=1
    if "fqdn" in item:
        fqdn_object["type"] = "FQDN"
        fqdn_object["name"] = item["fqdn"]["name"]
        fqdn_object["value"] = item["fqdn"]["domain"]
        fqdn_object["description"] = "Added via the FMC API with index " + str(index)
        fqdn_object["dnsResolution"] = "IPV4_ONLY"
        fqdn_objects_list.append(fqdn_object)
        fqdn_object = {}
        successes+=1
    if "ipv6" in item:
        print(f"\nItem at index {index} does not meet criteria so it has been ignored.")
        print("Offending item: \n", item["ipv6"])
        failures+=1
    index+=1
        
print(f"\nScript has processed {index} items with {successes} successfull and {failures} failed translations ")

# Remove spaces and illegal characters from the 4 Firepower object files (replace " " and ":" with "-")
#   -item["name"]

ftd_objects = [ ipv4_host_object_list, fqdn_objects_list, ipv4_network_object_list, ipv4_range_object_list]

for item in ftd_objects:
    for subitem in item:
        subitem["name"] = subitem["name"].replace(" ","-")
        subitem["name"] = subitem["name"].replace(":","-")

###GROUPS###

# Loop through the object groups list and convert name to Firepower formatting

fishy_items = 0 #Used for empty groups counting
ipv4_items = 0 
ipv6_items = 0

filename = input("\nPlease input the name of the file storing the network group objects.\nMake sure to include the file extension: ")

with open(filename) as f:
    sonicwall_groups = json.load(f)

for item in sonicwall_groups["address_groups"]:
    if "ipv4" in item:
        item["ipv4"]["name"] = item["ipv4"]["name"].replace(" ","-")
        item["ipv4"]["name"] = item["ipv4"]["name"].replace(":","-")
        if "address_object" in item["ipv4"] and "address_group" not in item["ipv4"]:
            for subitem in item["ipv4"]["address_object"]["ipv4"]:
                subitem["name"] = subitem["name"].replace(" ","-")
                subitem["name"] = subitem["name"].replace(":","-")
            ipv4_items+=1
        elif "address_group" in item["ipv4"] and "address_object" not in item["ipv4"]:
            for subitem in item["ipv4"]["address_group"]["ipv4"]:
                subitem["name"] = subitem["name"].replace(" ","-")
                subitem["name"] = subitem["name"].replace(":","-")
            ipv4_items+=1
        elif "address_group" in item["ipv4"] and "address_object" in item["ipv4"]:
            for subitem in item["ipv4"]["address_object"]["ipv4"]:
                subitem["name"] = subitem["name"].replace(" ","-")
                subitem["name"] = subitem["name"].replace(":","-")
            for subitem in item["ipv4"]["address_group"]["ipv4"]:
                subitem["name"] = subitem["name"].replace(" ","-")
                subitem["name"] = subitem["name"].replace(":","-")
            ipv4_items+=1
        else:
            fishy_items+=1
    elif "ipv6" in item:
        item["ipv6"]["name"] = item["ipv6"]["name"].replace(" ","-")
        item["ipv6"]["name"] = item["ipv6"]["name"].replace(":","-")
        if "address_object" in item["ipv6"]:
            if "ipv4" in item["ipv6"]["address_object"]:
                for subitem in item["ipv6"]["address_object"]["ipv4"]:
                    subitem["name"] = subitem["name"].replace(" ","-")
                    subitem["name"] = subitem["name"].replace(":","-")
            if "fqdn" in item["ipv6"]["address_object"]:
                for subitem in item["ipv6"]["address_object"]["fqdn"]:
                    subitem["name"] = subitem["name"].replace(" ","-")
                    subitem["name"] = subitem["name"].replace(":","-")
            ipv6_items+=1
        elif "address_group" in item["ipv6"]:
            if "ipv4" in item["ipv6"]["address_group"]:
                for subitem in item["ipv6"]["address_group"]["ipv6"]:
                    subitem["name"] = subitem["name"].replace(" ","-")
                    subitem["name"] = subitem["name"].replace(":","-")
            if "fqdn" in item["ipv6"]["address_group"]:
                for subitem in item["ipv6"]["address_group"]["fqdn"]:
                    subitem["name"] = subitem["name"].replace(" ","-")
                    subitem["name"] = subitem["name"].replace(":","-")
            ipv6_items+=1
        else:
            fishy_items+=1
    else:
        print("Something fishy found!")
        break

print(f"\n{ipv4_items} IPv4 groups and {ipv6_items} IPv6 groups were formatted for Firepower.")
print(f"\n{fishy_items} items were ignored due to non-compliance.")

#3 Load all objects into FMC to generate UUIDs and download them back

auth_url = "https://" + FMC_IP + "/api/fmc_platform/v1/auth/generatetoken"

response = requests.request("POST", auth_url, auth=(FMC_USER,FMC_PASS), verify=False)
print(f"\nAuthentication result: {response.status_code}.")

domain = response.headers["DOMAIN_UUID"]
base_url = "https://" + FMC_IP + f"/api/fmc_config/v1/domain/{domain}/object/"
headers = {
    "X-auth-access-token": response.headers["X-auth-access-token"],
    'Content-Type': 'application/json'
}

for item in ftd_objects:
    payload = json.dumps(item)
    if item[0]["type"] == "Host":
        url = base_url + "hosts?bulk=true"
        print("Attempting to load host objects...")
        response = requests.request("POST", url, headers = headers, data = payload, verify = False)
        if response.status_code <= 210:
            print("Success!")
        else:
            print("An error has been encountered!\n", response.content)
    elif item[0]["type"] == "FQDN":
        url = base_url + "fqdns?bulk=true"
        print("Attempting to load FQDN objects...")
        response = requests.request("POST", url, headers = headers, data = payload, verify = False)
        if response.status_code <= 210:
            print("Success!")
        else:
            print("An error has been encountered!\n", response.content)
    elif item[0]["type"] == "Network":
        url = base_url + "networks?bulk=true"
        print("Attempting to load network objects...")
        response = requests.request("POST", url, headers = headers, data = payload, verify = False)
        if response.status_code <= 210:
            print("Success!")
        else:
            print("An error has been encountered!\n", response.content)
    elif item[0]["type"] == "Range":
        url = base_url + "ranges?bulk=true"
        print("Attempting to load range objects...")
        response = requests.request("POST", url, headers = headers, data = payload, verify = False)
        if response.status_code <= 210:
            print("Success!")
        else:
            print("An error has been encountered!\n", response.content)
    else:
        print("\nWhat is this fishines!?!?")

for item in ftd_objects:
    if item[0]["type"] == "Host":
        url = base_url + "hosts?limit=1000"
        print("Attempting to download host objects...")
        response = requests.request("GET", url, headers = headers, verify = False)
        if response.status_code <= 210:
            print("Success!")
            hosts_with_uuid = json.loads(response.content)
        else:
            print("An error has been encountered!\n", response.content)
    elif item[0]["type"] == "FQDN":
        url = base_url + "fqdns?limit=1000"
        print("Attempting to download FQDN objects...")
        response = requests.request("GET", url, headers = headers, verify = False)
        if response.status_code <= 210:
            print("Success!")
            fqdns_with_uuid = json.loads(response.content)
        else:
            print("An error has been encountered!\n", response.content)
    elif item[0]["type"] == "Network":
        url = base_url + "networks?limit=1000"
        print("Attempting to download network objects...")
        response = requests.request("GET", url, headers = headers, verify = False)
        if response.status_code <= 210:
            print("Success!")
            networks_with_uuid = json.loads(response.content)
        else:
            print("An error has been encountered!\n", response.content)
    elif item[0]["type"] == "Range":
        url = base_url + "ranges?limit=1000"
        print("Attempting to download range objects...")
        response = requests.request("GET", url, headers = headers, verify = False)
        if response.status_code <= 210:
            print("Success!")
            ranges_with_uuid = json.loads(response.content)
        else:
            print("An error has been encountered!\n", response.content)
    else:
        print("\nWhat is this fishines!?!?")

#4 Combine all Firepower objects into single list (with "name", "type" and "id")

ftd_objects_with_uuid = hosts_with_uuid["items"] + fqdns_with_uuid["items"] + networks_with_uuid["items"] + ranges_with_uuid["items"]

#5 Loop through Sonicwall object groups and match:
#   -subitem["name"] of item["ipv4"]["address_object"]["ipv4"] with names from Firepower object list
#   -create Firepower object groups (made only by objects) and add to list

ftd_group = {}
ftd_group_element = {}
ftd_groups = []
ftd_group_element_list = []
empty_groups = 0
fishy_items = 0

for item in sonicwall_groups["address_groups"]:
    if "ipv4" in item:
        if "address_object" in item["ipv4"] and "address_group" not in item["ipv4"]:
            ftd_group["name"] = item["ipv4"]["name"]
            for subitem in item["ipv4"]["address_object"]["ipv4"]:
                for subsubitem in ftd_objects_with_uuid:
                    if subitem["name"] == subsubitem["name"]:
                        ftd_group_element["type"] = subsubitem["type"]
                        ftd_group_element["id"] = subsubitem["id"]
                        ftd_group_element_list.append(ftd_group_element)
                        ftd_group_element = {}
            if ftd_group_element_list:
                ftd_group["objects"] = ftd_group_element_list
                ftd_group_element_list = []
                ftd_groups.append(ftd_group)
                ftd_group = {}
            else:
                empty_groups+=1
    if "ipv6" in item:
        if "address_object" in item["ipv6"] and "address_group" not in item["ipv6"]:
            ftd_group["name"] = item["ipv6"]["name"]
            if "ipv4" in item["ipv6"]["address_object"] and "fqdn" in item["ipv6"]["address_object"]:
                for subitem in item["ipv6"]["address_object"]["ipv4"]:
                    for subsubitem in ftd_objects_with_uuid:
                        if subitem["name"] == subsubitem["name"]:
                            ftd_group_element["type"] = subsubitem["type"]
                            ftd_group_element["id"] = subsubitem["id"]
                            ftd_group_element_list.append(ftd_group_element)
                            ftd_group_element = {}
                for subitem in item["ipv6"]["address_object"]["fqdn"]:
                    for subsubitem in ftd_objects_with_uuid:
                        if subitem["name"] == subsubitem["name"]:
                            ftd_group_element["type"] = subsubitem["type"]
                            ftd_group_element["id"] = subsubitem["id"]
                            ftd_group_element_list.append(ftd_group_element)
                            ftd_group_element = {}
                if ftd_group_element_list:
                    ftd_group["objects"] = ftd_group_element_list
                    ftd_group_element_list = []
                    ftd_groups.append(ftd_group)
                    ftd_group = {}
                else:
                    empty_groups+=1
            elif "ipv4" in item["ipv6"]["address_object"] and "fqdn" not in item["ipv6"]["address_object"]:
                for subitem in item["ipv6"]["address_object"]["ipv4"]:
                    for subsubitem in ftd_objects_with_uuid:
                        if subitem["name"] == subsubitem["name"]:
                            ftd_group_element["type"] = subsubitem["type"]
                            ftd_group_element["id"] = subsubitem["id"]
                            ftd_group_element_list.append(ftd_group_element)
                            ftd_group_element = {}
                if ftd_group_element_list:
                    ftd_group["objects"] = ftd_group_element_list
                    ftd_group_element_list = []
                    ftd_groups.append(ftd_group)
                    ftd_group = {}
                else:
                    empty_groups+=1
            elif "ipv4" not in item["ipv6"]["address_object"] and "fqdn" in item["ipv6"]["address_object"]:
                for subitem in item["ipv6"]["address_object"]["fqdn"]:
                    for subsubitem in ftd_objects_with_uuid:
                        if subitem["name"] == subsubitem["name"]:
                            ftd_group_element["type"] = subsubitem["type"]
                            ftd_group_element["id"] = subsubitem["id"]
                            ftd_group_element_list.append(ftd_group_element)
                            ftd_group_element = {}
                if ftd_group_element_list:
                    ftd_group["objects"] = ftd_group_element_list
                    ftd_group_element_list = []
                    ftd_groups.append(ftd_group)
                    ftd_group = {}
                else:
                    empty_groups+=1
            else:
                fishy_items+=1


print(f"{empty_groups} object groups have been ignored due to being empty.")
print(f"\n{fishy_items} items were ignored due to non-compliance.")

#6 Load all object groups into FMC to generate UUIDs and download them back

url = base_url + "networkgroups?bulk=true"
payload = json.dumps(ftd_groups)

print("Attempting to load network group objects...")
response = requests.request("POST", url, headers = headers, data = payload, verify = False)
if response.status_code <= 210:
    print("Success!")
else:
    print("An error has been encountered!\n", response.content)

url = base_url + "networkgroups?limit=1000"

print("Attempting to download network group objects...")
response = requests.request("GET", url, headers = headers, verify = False)
if response.status_code <= 210:
    print("Success!")
    groups_with_uuid = json.loads(response.content)
else:
    print("An error has been encountered!\n", response.content)

ftd_objects_with_uuid+=groups_with_uuid["items"]

#7 Loop again through Sonicwall object groups and match:
#   -subitem["name"] of item["ipv4"]["address_group"]["ipv4"] with names from list of Firepower object groups 
#   -create Firepower object groups (made only by groups) and add to list


ftd_groups = []

for item in sonicwall_groups["address_groups"]:
    if "ipv4" in item:
        if "address_group" in item["ipv4"] and "address_object" not in item["ipv4"]:
            ftd_group["name"] = item["ipv4"]["name"]
            for subitem in item["ipv4"]["address_group"]["ipv4"]:
                for subsubitem in ftd_objects_with_uuid:
                    if subitem["name"] == subsubitem["name"]:
                        ftd_group_element["type"] = subsubitem["type"]
                        ftd_group_element["id"] = subsubitem["id"]
                        ftd_group_element_list.append(ftd_group_element)
                        ftd_group_element = {}
            if ftd_group_element_list:
                ftd_group["objects"] = ftd_group_element_list
                ftd_group_element_list = []
                ftd_groups.append(ftd_group)
                ftd_group = {}
            else:
                empty_groups+=1
        elif "address_group" in item["ipv4"] and "address_object" in item["ipv4"]:
            ftd_group["name"] = item["ipv4"]["name"]
            for subitem in item["ipv4"]["address_group"]["ipv4"]:
                for subsubitem in ftd_objects_with_uuid:
                    if subitem["name"] == subsubitem["name"]:
                        ftd_group_element["type"] = subsubitem["type"]
                        ftd_group_element["id"] = subsubitem["id"]
                        ftd_group_element_list.append(ftd_group_element)
                        ftd_group_element = {}
            for subitem in item["ipv4"]["address_object"]["ipv4"]:
                for subsubitem in ftd_objects_with_uuid:
                    if subitem["name"] == subsubitem["name"]:
                        ftd_group_element["type"] = subsubitem["type"]
                        ftd_group_element["id"] = subsubitem["id"]
                        ftd_group_element_list.append(ftd_group_element)
                        ftd_group_element = {}
            if ftd_group_element_list:
                ftd_group["objects"] = ftd_group_element_list
                ftd_group_element_list = []
                ftd_groups.append(ftd_group)
                ftd_group = {}
            else:
                empty_groups+=1
    elif "ipv6" in item:
        if "address_object" in item["ipv6"] and "address_group" in item["ipv6"]:
            ftd_group["name"] = item["ipv6"]["name"]
            if "ipv4" in item["ipv6"]["address_object"] and "fqdn" in item["ipv6"]["address_object"] and "fqdn" not in item["ipv6"]["address_group"]:
                for subitem in item["ipv6"]["address_object"]["ipv4"]:
                    for subsubitem in ftd_objects_with_uuid:
                        if subitem["name"] == subsubitem["name"]:
                            ftd_group_element["type"] = subsubitem["type"]
                            ftd_group_element["id"] = subsubitem["id"]
                            ftd_group_element_list.append(ftd_group_element)
                            ftd_group_element = {}
                for subitem in item["ipv6"]["address_object"]["fqdn"]:
                    for subsubitem in ftd_objects_with_uuid:
                        if subitem["name"] == subsubitem["name"]:
                            ftd_group_element["type"] = subsubitem["type"]
                            ftd_group_element["id"] = subsubitem["id"]
                            ftd_group_element_list.append(ftd_group_element)
                            ftd_group_element = {}
                if ftd_group_element_list:
                    ftd_group["objects"] = ftd_group_element_list
                    ftd_group_element_list = []
                    ftd_groups.append(ftd_group)
                    ftd_group = {}
            elif "fqdn" in item["ipv6"]["address_object"] and "ipv4" not in item["ipv6"]["address_object"] and "ipv4" in item["ipv6"]["address_group"]:
                for subitem in item["ipv6"]["address_object"]["fqdn"]:
                    for subsubitem in ftd_objects_with_uuid:
                        if subitem["name"] == subsubitem["name"]:
                            ftd_group_element["type"] = subsubitem["type"]
                            ftd_group_element["id"] = subsubitem["id"]
                            ftd_group_element_list.append(ftd_group_element)
                            ftd_group_element = {}
                for subitem in item["ipv6"]["address_group"]["ipv4"]:
                    for subsubitem in ftd_objects_with_uuid:
                        if subitem["name"] == subsubitem["name"]:
                            ftd_group_element["type"] = subsubitem["type"]
                            ftd_group_element["id"] = subsubitem["id"]
                            ftd_group_element_list.append(ftd_group_element)
                            ftd_group_element = {}
                if ftd_group_element_list:
                    ftd_group["objects"] = ftd_group_element_list
                    ftd_group_element_list = []
                    ftd_groups.append(ftd_group)
                    ftd_group = {}
            else:
                break

#6 Load last object groups into FMC 

url = base_url + "networkgroups?bulk=true"
payload = json.dumps(ftd_groups)

print("Attempting to load network group objects...")
response = requests.request("POST", url, headers = headers, data = payload, verify = False)
if response.status_code <= 210:
    print("Success!")
else:
    print("An error has been encountered!\n", response.content)
              
SCRIPT_END_TIME = datetime.now().strftime("%d-%B-%Y-%I-%M-%p")
print(f"\nScript ended at {SCRIPT_END_TIME}")