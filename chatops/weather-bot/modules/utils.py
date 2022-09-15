import logging
import subprocess
import requests
from time import sleep

# Initialize logger
logger = logging.getLogger(__name__)


def startNgrok() -> bool:
    logging.debug("Starting Ngrok...")
    number_of_tries = 5
    ngrok_console = "http://127.0.0.1:4040/api/tunnels"
    p = subprocess.Popen(["sh","start_ngrok.sh"], stdout=subprocess.DEVNULL)
    sleep(5)
    while number_of_tries:
        number_of_tries -= 1
        try:
            tunnels = requests.get(ngrok_console).json()["tunnels"]
            return True
        except Exception as e:
            logger.error(f"Could not start NGROK!\n{e}")
    return False


def getNgrokURLs() -> list:
    urls = []
    ngrok_console = "http://127.0.0.1:4040/api/tunnels"
    try:
        tunnels = requests.request(
            method="GET",
            url=ngrok_console
        ).json()["tunnels"]
        for tunnel in tunnels:
            urls.append(tunnel["public_url"])
        logger.debug(f"Found the following URLs:\n{urls}\n")
    except Exception as e:
        logger.warning("Connection refused! Is Ngrok running?")
        logger.debug(f"Error text:{e}")

    return urls
