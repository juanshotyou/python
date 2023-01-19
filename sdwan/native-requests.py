import requests
import json
import os
import urllib3
from dotenv import load_dotenv

# Disable insecure HTTPS warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables and declare API url
load_dotenv()
api_url = "https://sandbox-sdwan-2.cisco.com"
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")

class SDWAN:
    def __init__(self, username: str, password: str, api_url: str) -> None:
        self._auth = {
            "j_username": username,
            "j_password": password
        }
        self._api_url = api_url
        self._session_token = requests.post(
            url=self._api_url + "/j_security_check",
            data=self._auth,
            verify=False
        ).headers["set-cookie"].split(";")[0]
        self._xsrf_token = requests.get(
            url=self._api_url + "/dataservice/client/token",
            headers={
                "Cookie": self._session_token
            },
            verify=False
        ).text
        self._headers = {
            "Cookie": self._session_token,
            "X-XSRF-TOKEN": self._xsrf_token
        }

    def _makeRequest(self, method: str, endpoint: str, payload: dict = {}) -> dict:
        url = self._api_url + endpoint
        result = {}
        try:
            if payload:
                data = json.dumps(payload)
                response = requests.request(
                    method=method,
                    url=url,
                    headers=self._headers,
                    data=data,
                    verify=False
                )
            else:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=self._headers,
                    verify=False
                )
        except requests.exceptions.Timeout as e:
            print(f"Operation timed out:\n{e}")
            raise SystemError(e)
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error:\n{e}")
            raise SystemError(e)
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error:\n{e}")
            raise SystemError(e)

        if response.status_code >= 400 or response.status_code < 200:
            print(
                f"Operation failed: {response.status_code} \n{response.text}"
            )
        elif response.status_code >= 200 and response.status_code < 300:
            print("Operation successful!")

        # Return data if needed
        if response.content:
            result = response.json()

        return result


if __name__ == "__main__":
    # Instantiate vManage connection object
    vmanage = SDWAN(username=username, password=password, api_url=api_url)

    # Get device inventory and print info
    print("\nAttempting to get device inventory...")
    inventory = vmanage._makeRequest(method="GET", endpoint="/dataservice/device")
    print(f"Found the following devices controlled by {vmanage._api_url}:")
    for device in inventory["data"]:
        print(f'Device {device["host-name"]} with IP {device["system-ip"]} and serial {device["board-serial"]}')
        print(f'Model is {device["device-model"]} and software version is {device["version"]}')

    # Get user list
    print("\nAttempting to get users list...")
    users = vmanage._makeRequest(method="GET", endpoint="/dataservice/admin/user")
    for user in users["data"]:
        print(f'Found user \"{user["userName"]}\".')

    # Get device configuration history
    print("\nAttempting to get device configuration history...")
    device_config_history = vmanage._makeRequest(method="GET", endpoint="/dataservice/device/history")
    for device in device_config_history["data"]:
        print(f"Device {device['local_system_ip']} is in {device['state']} state.")
