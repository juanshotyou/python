import os
from ncclient import manager
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
    
    def getCapabilities(self) -> list:
        return self._manager.server_capabilities


if __name__ == "__main__":
    csr = IOSXE(ip_address=ip_address, username=username, password=password)
    capabilities = csr.getCapabilities()
    for c in capabilities:
        print(c)