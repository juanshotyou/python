import os
import json
import urllib3
import time
import sys
import math
import pandas as pd
from dnacentersdk import DNACenterAPI
from dotenv import load_dotenv
from jinja_templates.site_templates import *

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def inventoryAudit(dnac):

    print("Testing connection to DNAC by auditing device inventory...\n")
    try:
        devices = dnac.devices.get_device_list()
        for device in devices.response:
            print(f"{device.hostname} has been up for {device.upTime}")
    except ApiError as e:
        print("Error encountered! See below for more info:\n",e)

def addSiteToHierarchy(dnac, sites_to_add):

    for site in sites_to_add:
        # Start by assuming that fields are missing until we check against the data frame
        area_check = False
        building_check = False
        floor_check = False
        
        # Check the presence of each field within the frame
        if isinstance(site["Site"], str):
            area_payload = json.loads(J2_TMP_AREA.render(site))
            area_check = True
        if isinstance(site["Building"], str):
            building_payload = json.loads(J2_TMP_BUILDING.render(site))
            building_check = True
        if isinstance(site["Floor"], str):
            floor_payload = json.loads(J2_TMP_FLOOR.render(site))
            floor_check = True
        
        print(area_check, building_check, floor_check)

        # Load area to DNAC
        if area_check:
            try:
                print(f"\nLoading area - {site['Site']}.")
                response = dnac.sites.create_site(payload=area_payload)
                taskId = response["executionId"]
                if taskId:
                    status = checkTaskExecutionStandard(dnac, taskId)
                    while status["status"] == "IN_PROGRESS":
                        print(f"Loading site {site['Site']} is still in progress. Sleeping for 1s...")
                        time.sleep(1)
                        status = checkTaskExecutionStandard(dnac, taskId)
                    if status["status"] == "FAILURE":
                        error_msg = json.loads(status["bapiError"])
                        print(f"Loading site {site['Site']} failed due to the following reason:\n    - {error_msg['result']['result']}")
                    elif status["status"] == "SUCCESS":
                        print(f"Site {site['Site']} successfully added!")
                    else:
                        print("Unexpected result encountered! Terminating program!")
                        sys.exit()
                else:
                    print("Task ID could not be retrieved! Terminating program!")
                    sys.exit()
            except ApiError as e:
                print("Error encountered! See below for more info:\n",e)
            except TypeError as e:
                print("Type error encountered! See below for more info:\n",e)

        # Load building to DNAC
        if building_check:
            try:
                print(f"\nLoading building - {site['Building']} within {site['Site']}.")
                response = dnac.sites.create_site(payload=building_payload)
                taskId = response["executionId"]
                if taskId:
                    status = checkTaskExecutionStandard(dnac, taskId)
                    while status["status"] == "IN_PROGRESS":
                        print(f"Loading building {site['Building']} to {site['Site']}-{site['Address']} is still in progress. Sleeping for 1s...")
                        time.sleep(1)
                        status = checkTaskExecutionStandard(dnac, taskId)
                    if status["status"] == "FAILURE":
                        error_msg = json.loads(status["bapiError"])
                        print(f"Loading building {site['Building']} to {site['Site']} failed due to the following reason:\n    - {error_msg['result']['result']}")
                    elif status["status"] == "SUCCESS":
                        print(f"Building {site['Building']} successfully added to {site['Site']}!")
                    else:
                        print("Unexpected result encountered! Terminating program!")
                        sys.exit()
                else:
                    print("Task ID could not be retrieved! Terminating program!")
                    sys.exit()
            except ApiError as e:
                print("Error encountered! See below for more info:\n",e)
            except TypeError as e:
                print("Type error encountered! See below for more info:\n",e)

        # Load floor to DNAC
        if floor_check:
            try:
                print(f"\nLoading floor - {site['Floor']} within {site['Building']} in {site['Site']}.")
                response = dnac.sites.create_site(payload=floor_payload)
                taskId = response["executionId"]
                if taskId:
                    status = checkTaskExecutionStandard(dnac, taskId)
                    while status["status"] == "IN_PROGRESS":
                        print(f"Loading floor {site['Floor']} to building {site['Building']} in {site['Site']} is still in progress. Sleeping for 1s...")
                        time.sleep(1)
                        status = checkTaskExecutionStandard(dnac, taskId)
                    if status["status"] == "FAILURE":
                        error_msg = json.loads(status["bapiError"])
                        print(f"Loading floor {site['Floor']} to building {site['Building']} in {site['Site']} failed due to the following reason:\n    - {error_msg['result']['result']}")
                    elif status["status"] == "SUCCESS":
                        print(f"Floor {site['Floor']} successfully added to building {site['Building']} in {site['Site']}")
                    else:
                        print("Unexpected result encountered! Terminating program!")
                        sys.exit()
                else:
                    print("Task ID could not be retrieved! Terminating program!")
                    sys.exit()
            except TypeError as e:
                print("Type error encountered! See below for more info:\n",e)

def deleteSiteFromHierarchy(dnac, sites_to_add, site_hierarchy):

    for i in site_hierarchy["response"]:
        for k in i["additionalInfo"]:
            if k["nameSpace"] == "Location" and k["attributes"]["type"] == "floor":
                for j in sites_to_add:
                    if j["Floor"] == i["name"]:
                        try:
                            result = dnac.sites.delete_site(site_id=i["id"])
                            print(f"Floor {i['name']} successfully deleted!")
                        except ApiError as e:
                            print("Error encountered! See below for more info:\n",e)
  
    for i1 in site_hierarchy["response"]:
        for k1 in i1["additionalInfo"]:
            if k1["nameSpace"] == "Location" and k1["attributes"]["type"] == "building":
                for j1 in sites_to_add:
                    if j1["Building"] == i1["name"]:
                        try:
                            result = dnac.sites.delete_site(site_id=i1["id"])
                            print(f"Building {i1['name']} successfully deleted!")
                        except ApiError as e:
                            print("Error encountered! See below for more info:\n",e)

    for i2 in site_hierarchy["response"]:
        for k2 in i2["additionalInfo"]:
            if k2["nameSpace"] == "Location" and k2["attributes"]["type"] == "area":
                for j2 in sites_to_add:
                    if j2["Site"] == i2["name"]:
                        try:
                            result = dnac.sites.delete_site(site_id=i2["id"])
                            print(f"Area {i2['name']} successfully deleted!")
                        except ApiError as e:
                            print("Error encountered! See below for more info:\n",e)


def getSiteHierarchy(dnac):

    try:
        site_hierarchy = dnac.sites.get_site()
        return site_hierarchy
    except ApiError as e:
        print("Error encountered! See below for more info:\n",e)

def checkTaskExecutionStandard(dnac, taskId):

    try:
        task_status = dnac.task.get_business_api_execution_details(execution_id = taskId)
        return task_status
    except ApiError as e:
        print("Error encountered! See below for more info:\n",e)

def readDataCaptureFile():

    data_path = os.getcwd() + "/data_sources/" + "LSDD-Form-SDA-optimized-full.xlsx"
    net_hierarchy_pd = pd.read_excel(data_path, sheet_name="NetHie", header=3, usecols="B:E")
    net_hierarchy_list = []

    for i in range(len(net_hierarchy_pd.index)):
        net_hierarchy_list.append(net_hierarchy_pd.iloc[i].to_dict())

    return net_hierarchy_list


def main():

    # Create a DNACenterAPI connection object which we will use for the other tasks
    dnac = DNACenterAPI()
    # inventoryAudit(dnac)
    # Retrieve sites, buildings and floors from data capture file
    sites_to_add = readDataCaptureFile()
    site_hierarchy = getSiteHierarchy(dnac)
    # print(json.dumps(site_hierarchy["response"], indent = 4))
    # Add data to DNAC
    # addSiteToHierarchy(dnac, sites_to_add)
    deleteSiteFromHierarchy(dnac, sites_to_add, site_hierarchy)

if __name__ == "__main__":
    main()