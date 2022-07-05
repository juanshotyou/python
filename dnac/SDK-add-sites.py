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

def addSiteToHierarchy(dnac, list_of_sites):

    for site in list_of_sites:
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

        # Load building to DNAC
        if building_check:
            try:
                print(f"\nLoading building - {site['Building']} within {site['Site']}.")
                response = dnac.sites.create_site(payload=building_payload)
                taskId = response["executionId"]
                if taskId:
                    status = checkTaskExecutionStandard(dnac, taskId)
                    while status["status"] == "IN_PROGRESS":
                        print(f"Loading building {site['Building']} to {site['Site']} is still in progress. Sleeping for 1s...")
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
    net_hierarchy_pd = pd.read_excel(data_path, sheet_name="NetHie", header=3, usecols="B:D")
    net_hierarchy_list = []

    for i in range(len(net_hierarchy_pd.index)):
        net_hierarchy_list.append(net_hierarchy_pd.iloc[i].to_dict())

    return net_hierarchy_list


def main():

    # Create a DNACenterAPI connection object which we will use for the other tasks
    dnac = DNACenterAPI()
    # inventoryAudit(dnac)
    # Retrieve sites, buildings and floors from data capture file
    list_of_sites = readDataCaptureFile()
    # Add data to DNAC
    addSiteToHierarchy(dnac, list_of_sites)

if __name__ == "__main__":
    main()