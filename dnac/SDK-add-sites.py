import os
import json
import urllib3
import time
import sys
import math
import pandas as pd
from dnacentersdk import DNACenterAPI
from dotenv import load_dotenv
from prettytable import PrettyTable
from jinja_templates.site_templates import *

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def inventoryAudit(dnac):

    print("Testing connection to DNAC by auditing device inventory...\n")
    try:
        devices = dnac.devices.get_device_list()
        for device in devices.response:
            print(f"{device.hostname} has been up for {device.upTime}")
    except TypeError as e:
        print("Type error encountered! See below for more info:\n",e)

def addSiteToHierarchy(dnac, sites_to_add):

    already_added = []

    for site in sites_to_add:
        # Start by assuming that fields are missing until we check against the data frame
        area_check = False
        building_check = False
        floor_check = False
        
        # Check the presence of each field within the frame
        if isinstance(site["Area"], str):
            area_payload = json.loads(J2_TMP_AREA.render(site))
            area_check = True
        if isinstance(site["Building"], str):
            building_payload = json.loads(J2_TMP_BUILDING.render(site))
            building_check = True
        if isinstance(site["Floor"], str):
            floor_payload = json.loads(J2_TMP_FLOOR.render(site))
            floor_check = True

        # Load area to DNAC
        if area_check and site["Area"] not in already_added:
            already_added.append(site["Area"])
            try:
                print(f"Loading area - {site['Area']}.")
                response = dnac.sites.create_site(payload=area_payload)
                taskId = response["executionId"]
                if taskId:
                    checkTaskExecutionStatus(dnac, taskId)
                else:
                    print("Task ID could not be retrieved! Terminating program!")
                    sys.exit()
            except TypeError as e:
                print("Type error encountered! See below for more info:\n",e)

        # Load building to DNAC
        if building_check and site["Building"] not in already_added:
            already_added.append(site["Building"])
            try:
                print(f"Loading building - {site['Building']} within {site['Area']}.")
                response = dnac.sites.create_site(payload=building_payload)
                taskId = response["executionId"]
                if taskId:
                    checkTaskExecutionStatus(dnac, taskId)
                else:
                    print("Task ID could not be retrieved! Terminating program!")
                    sys.exit()
            except TypeError as e:
                print("Type error encountered! See below for more info:\n",e)

        # Load floor to DNAC
        if floor_check:
            try:
                print(f"Loading floor - {site['Floor']} within {site['Building']} in {site['Area']}.")
                response = dnac.sites.create_site(payload=floor_payload)
                taskId = response["executionId"]
                if taskId:
                    checkTaskExecutionStatus(dnac, taskId)
                else:
                    print("Task ID could not be retrieved! Terminating program!")
                    sys.exit()
            except TypeError as e:
                print("Type error encountered! See below for more info:\n",e)

def deleteSiteFromHierarchy(dnac, sites_to_add, site_hierarchy):

    already_deleted = []

    for element in ["floor", "building", "area"]:
        for i in site_hierarchy["response"]:
            for k in i["additionalInfo"]:
                if k["nameSpace"] == "Location" and k["attributes"]["type"] == element:
                    for j in sites_to_add:
                        if j[element.title()] == i["name"] and j[element.title()] not in already_deleted:
                            already_deleted.append(j[element.title()])
                            try:
                                print(f"Deleting {element} {i['name']}...")
                                result = dnac.sites.delete_site(site_id=i["id"])
                                taskId = result["executionId"]
                                if taskId:
                                    checkTaskExecutionStatus(dnac, taskId)
                                else:
                                    print("Task ID could not be retrieved! Terminating program!")
                                    sys.exit()
                            except TypeError as e:
                                print("Error encountered! See below for more info:\n",e)


def getSiteHierarchy(dnac):

    try:
        site_hierarchy = dnac.sites.get_site()
        return site_hierarchy
    except ApiError as e:
        print("Error encountered! See below for more info:\n",e)

def checkTaskExecutionStatus(dnac, taskId):

    try:
        task_status = dnac.task.get_business_api_execution_details(execution_id = taskId)
        while task_status["status"] == "IN_PROGRESS":
            time.sleep(1)
            task_status = dnac.task.get_business_api_execution_details(execution_id = taskId)
        if task_status["status"] == "FAILURE":
            error_msg = json.loads(task_status["bapiError"])
            print(f"Task failed due to the following reason:\n    - {error_msg}")
        elif task_status["status"] == "SUCCESS":
            print(f"Task successfully completed!")
        else:
            print("Unexpected result encountered! Terminating program!")
            sys.exit()
    except TypeError as e:
        print("Type error encountered! See below for more info:\n",e)

def getDeviceCredentials(dnac):

    try:
        device_credentials = dnac.network_settings.get_device_credential_details()
        
    except TypeError as e:
        print("Type error encountered! See below for more info:\n",e)

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
    # Check that the connection is correctly set up by requesting the device inventory list
    # inventoryAudit(dnac)
    # Retrieve sites, buildings and floors from data capture file
    sites_to_add = readDataCaptureFile()
    site_hierarchy = getSiteHierarchy(dnac)

    # Function that adds data from the data source to DNAC
    addSiteToHierarchy(dnac, sites_to_add)
    # Function that removes data from the data source from DNAC
    # deleteSiteFromHierarchy(dnac, sites_to_add, site_hierarchy)
    getDeviceCredentials(dnac)

if __name__ == "__main__":
    main()