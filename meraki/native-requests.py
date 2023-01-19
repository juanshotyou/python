import requests
import json
import os
import urllib3
from dotenv import load_dotenv

# Disable insecure HTTPS warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables and declare API url
load_dotenv()
token = os.environ.get("MERAKI_API_KEY")
api_url = "https://api.meraki.com/api/v1"

class NoRebuildAuthSession(requests.Session):
    def rebuild_auth(self, prepared_request, response) -> None:
        """ Needed to prevent the stripping of the Authorization header when
            the request is redirected. See Meraki API docs for info.
        """
        return

class Meraki:
    def __init__(self, token: str, api_url: str) -> None:
        self._header = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Cisco-Meraki-API-Key": token
        }
        self._session = NoRebuildAuthSession()
        self._api_url = api_url

    def _makeRequest(self, method: str, endpoint: str, payload: dict = {}) -> dict:
        url = self._api_url + endpoint
        result = {}
        try:
            if payload:
                data = json.dumps(payload)
                response = self._session.request(
                    method=method,
                    url=url,
                    headers=self._header,
                    data=data
                )
            else:
                response = self._session.request(
                    method=method,
                    url=url,
                    headers=self._header
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
    # Initialize dashboard object
    dashboard = Meraki(token=token, api_url=api_url)
    # Get all orgs that the user has access to
    print("Attempting to download orgs list...")
    orgs = dashboard._makeRequest(method="GET", endpoint="/organizations")
    # If org is "VMO2 - NCA DEVNET", get and print all devices associated to it
    id = [org["id"] for org in orgs if org["name"] == "VMO2 - NCA DEVNET"]
    print("Attempting to retrieve device info for VMO2 - NCA DEVNET...")
    devices = dashboard._makeRequest(method="GET", endpoint=f"/organizations/{id[0]}/devices")
    print(f"Found the following for organization {id[0]}:")
    for device in devices:
        print(
            f"Device {device['name']} is a {device['model']} and has SN {device['serial']}. "
            f"It was last configured at {device['configurationUpdatedAt']}."
        )
    # Create a new network under the "VMO2 - NCA DEVNET" org
    print("Attempting to create a new network...")
    new_network = "VR_learning_net"
    payload = {
        "name": new_network,
        "tags": [
            "ENAUTO",
            "DevNet",
            "Training"
        ],
        "productTypes": ['appliance', 'switch', 'camera']
    }
    dashboard._makeRequest(method="POST", endpoint=f"/organizations/{id[0]}/networks", payload=payload)
    # Get new network ID and update its notes
    networks = dashboard._makeRequest(method="GET", endpoint=f"/organizations/{id[0]}/networks")
    network_id = [network["id"] for network in networks if network["name"] == "VR_learning_net"]
    print(f"Network {new_network} has ID {network_id[0]}")
    payload = {
        "notes": "Added some notes to this network via API."
    }
    dashboard._makeRequest(method="PUT", endpoint=f"/networks/{network_id[0]}", payload=payload)
    # Check that there are no webhooks currently registered
    webhooks = dashboard._makeRequest(method="GET", endpoint=f"/networks/{network_id[0]}/webhooks/httpServers")
    if not webhooks:
        print(f"No webhooks found for network {network_id[0]}")
    # Register a new webhook
    print("Attempting to register a new webhook...")
    payload = {
        "name": "VR_TEST_WEBHOOK",
        "sharedSecret": "SHHHHHHHH",
        "url": "https://nca-dev.techsupport.co.uk/receiver"
    }
    dashboard._makeRequest(method="POST", endpoint=f"/networks/{network_id[0]}/webhooks/httpServers", payload=payload)
    # Check that new webhook can now be seen
    webhooks = dashboard._makeRequest(method="GET", endpoint=f"/networks/{network_id[0]}/webhooks/httpServers")
    if webhooks:
        print("The following webhooks have been found:")
        for webhook in webhooks:
            print(json.dumps(webhook, indent=2))
    # Get ID of new webhook and delete it from the network
    webhook_id = [webhook["id"] for webhook in webhooks if webhook["name"] == "VR_TEST_WEBHOOK"]
    print(f"Attempting to delete webhook {webhook_id[0]} from network {network_id[0]}...")
    dashboard._makeRequest(method="DELETE", endpoint=f"/networks/{network_id[0]}/webhooks/httpServers/{webhook_id[0]}")
    # Remove the new network
    print(f"Attempting to delete network {network_id[0]}...")
    dashboard._makeRequest(method="DELETE", endpoint=f"/networks/{network_id[0]}")
