import os
from ncclient import manager
from lxml import etree
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")
ip_address = os.environ.get("IP_ADDRESS")


class IOSXE:
    def __init__(self, ip_address: str, username: str, password: str) -> None:
        self._manager = manager.connect(
            host=ip_address,
            username=username,
            password=password
        )
        self._ip = ip_address

    def __del__(self) -> None:
        print("Terminating connection...")
        self._manager.close_session()

    def getCapabilities(self) -> list:
        return self._manager.server_capabilities

    def getConfig(self) -> dict:
        response = self._manager.get_config(source="running")
        xml_data = etree.tostring(
            element_or_tree=response.data_ele,
            pretty_print=True
        ).decode()
        return xml_data


if __name__ == "__main__":
    csr = IOSXE(ip_address=ip_address, username=username, password=password)
    config = csr.getConfig()
    print(config)
    del csr
