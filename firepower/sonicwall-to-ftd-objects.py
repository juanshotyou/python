import json
import os
from netaddr import IPAddress
from datetime import datetime

SCRIPT_RUN_TIME = datetime.now().strftime("%d-%B-%Y-%I-%M-%p")
print(f"\nScript started at {SCRIPT_RUN_TIME}\n")

#Check current working directory and make sure it's set as the working folder

path = os.getcwd()
print("\nInitial path was:", path)

os.chdir(os.path.dirname(os.path.abspath(__file__)))

path = os.getcwd()
print("\nNew path is:", path)

#Get the objects filename and read the data

filename = input("\nPlease input the name of the file storing the network objects.\nMake sure to include the file extension: ")

with open(filename) as f:
    sonicwall_objects = json.load(f)

#Loop through the data and create Firepower equivalent

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
        if "host" in object["ipv4"] and object["ipv4"]["host"] != {}:
            ipv4_host_object["type"] = "Host"
            ipv4_host_object["value"] = object["ipv4"]["host"]["ip"]
            ipv4_host_object["name"] = object["ipv4"]["name"]
            ipv4_host_object["description"] = "Added via the FMC API with index " + str(index)
            ipv4_host_object_list.append(ipv4_host_object)
            ipv4_host_object = {}
            successes+=1
        elif "network" in object["ipv4"] and object["ipv4"]["network"] != {}:
            ipv4_network_object["type"] = "Network"
            ipv4_network_object["value"] = object["ipv4"]["network"]["subnet"] + "/" + str(IPAddress(object["ipv4"]["network"]["mask"]))
            ipv4_network_object["name"] = object["ipv4"]["name"]
            ipv4_network_object["description"] = "Added via the FMC API with index " + str(index)
            ipv4_network_object_list.append(ipv4_network_object)
            ipv4_network_object = {}
            successes+=1
        elif "range" in object["ipv4"]:
            ipv4_range_object["type"] = "Range"
            ipv4_range_object["value"] = object["ipv4"]["range"]["begin"] + "-" + object["ipv4"]["range"]["end"]
            ipv4_range_object["name"] = object["ipv4"]["name"]
            ipv4_range_object["description"] = "Added via the FMC API with index " + str(index)
            ipv4_range_object_list.append(ipv4_range_object)
            ipv4_range_object = {}
            successes+=1
        else:
            print(f"\nItem at index {index} does not meet criteria so it has been ignored.")
            print("Offending item: \n", object["ipv4"])
            failures+=1
    if "mac" in item:
        print(f"\nItem at index {index} does not meet criteria so it has been ignored.")
        print("Offending item: \n", object["mac"])
        failures+=1
    if "fqdn" in item:
        fqdn_object["type"] = "FQDN"
        fqdn_object["name"] = object["fqdn"]["name"]
        fqdn_object["value"] = object["fqdn"]["domain"]
        fqdn_object["description"] = "Added via the FMC API with index " + str(index)
        fqdn_object["dnsResolution"] = "IPV4_ONLY"
        fqdn_objects_list.append(fqdn_object)
        fqdn_object = {}
        successes+=1
    if "ipv6" in item:
        print(f"\nItem at index {index} does not meet criteria so it has been ignored.")
        print("Offending item: \n", object["ipv6"])
        failures+=1
    index+=1
        
print(f"\nScript has processed {index} items with {successes} successfull and {failures} failed translations ")

#Save each object sets to its own file

with open("sonicwall-to-ftd-host-objects-" + SCRIPT_RUN_TIME + ".txt", "a+") as f:
    json.dump(ipv4_host_object_list, f, indent = 2)
with open("sonicwall-to-ftd-network-objects-" + SCRIPT_RUN_TIME + ".txt", "a+") as f:
    json.dump(ipv4_network_object_list, f, indent = 2)
with open("sonicwall-to-ftd-range-objects-" + SCRIPT_RUN_TIME + ".txt", "a+") as f:
    json.dump(ipv4_range_object_list, f, indent = 2)
with open("sonicwall-to-ftd-fqdn-objects-" + SCRIPT_RUN_TIME + ".txt", "a+") as f:
    json.dump(fqdn_objects_list, f, indent = 2)

SCRIPT_END_TIME = datetime.now().strftime("%d-%B-%Y-%I-%M-%p")
print(f"\nScript ended at {SCRIPT_END_TIME}")