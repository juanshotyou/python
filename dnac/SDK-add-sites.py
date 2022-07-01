import os
import json
import urllib3
from dnacentersdk import DNACenterAPI
from dotenv import load_dotenv

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def inventoryAudit(dnac):
    print("haha")
    try:
        devices = dnac.devices.get_device_list()
        for device in devices.response:
            print(f"{device.hostname} has been up for {device.upTime}")
    except ApiError as e:
        print("Error encountered! See below for more info:\n",e)

def main():
    # Create a DNACenterAPI connection object which we will use for the other tasks
    dnac = DNACenterAPI()
    inventoryAudit(dnac)

if __name__ == "__main__":
    main()