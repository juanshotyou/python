import json
import requests
import logging
import logging.config
from webex_module import Messenger
from flask import Flask, request

# Initialize logger
logging.config.fileConfig("logger.conf")
logger = logging.getLogger(__name__)
logging.getLogger("webex_module").disabled = False

# Instantiate Webex handler, Flask gateway and define routes
webex = Messenger()
gateway = Flask(__name__)


@gateway.route("/", methods=["GET", "POST"])
def index() -> tuple:
    if request.method == "GET":
        logger.info("GET request received.")
        return (f"Request received via {request.host}", 200)
    elif request.method == "POST":
        logger.info("POST request received.")
        if "application/json" in request.headers.get("Content-Type"):
            data = request.get_json()
            printable_data = json.dumps(data, indent=4)
            if webex.bot_id == data.get("data").get("personId"):
                logger.debug(f"Message from self received:\n{printable_data}")
                return ("Message from self ignored.", 200)
            else:
                logger.debug(f"Message received:\n{printable_data}")
                room_id = data["data"]["roomId"]
                message_id = data["data"]["id"]
                msg_contents = webex.getMessage(message_id=message_id)["text"]
                reply = f'You sent me this - "{msg_contents}"'
                webex.sendMessageToRoom(room_id=room_id, message=reply)
                return (data, 200)
        else:
            return ("Wrong data format", 400)


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
    except ConnectionRefusedError as e:
        logger.warning("Connection refused! Is Ngrok running?")
        logger.debug(f"Error text:{e}")

    return urls


def main():
    webhook_urls = webex.getWebhooks()
    ngrok_urls = getNgrokURLs()
    target_url = list(set(ngrok_urls) & set(webhook_urls))
    if target_url:
        logger.info(f"Target webhook: {target_url[0]}")
    else:
        webex.registerWebhook(url=ngrok_urls[0], name="NGROK test webhook")
    gateway.run(host="0.0.0.0", port=5005, debug=True)


if __name__ == "__main__":
    main()
