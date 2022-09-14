import json
import logging
import logging.config
from modules import utils, webex_module, weather_module
from flask import Flask, request

# Initialize logger
logging.config.fileConfig("logger.conf")
logger = logging.getLogger(__name__)
logging.getLogger("modules.webex_module").disabled = False
logging.getLogger("modules.weather_module").disabled = False
logging.getLogger("modules.utils").disabled = False

# Instantiate Webex handler, Flask gateway and define routes
webex = webex_module.Messenger()
gateway = Flask(__name__)
weather = weather_module.OpenWeather()

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
            # Filter out messages from self
            if webex.bot_id == data.get("data").get("personId"):
                logger.debug(f"Message from self received:\n{printable_data}")
                return ("Message from self ignored.", 200)
            else:
                # Read message contents
                logger.debug(f"Notification received:\n{printable_data}")
                room_id = data["data"]["roomId"]
                message_id = data["data"]["id"]
                msg_contents = webex.getMessage(message_id=message_id)
                # Extract all information from message
                msg = {}
                if "text" in msg_contents:
                    msg["text"] = msg_contents["text"]
                if "files" in msg_contents:
                    msg["files"] = msg_contents["files"]
                if "attachments" in msg_contents:
                    msg["attachments"] = msg_contents["attachments"]
                # Check message contents and reply
                if msg["text"].lower() in ["hello", "help"]:
                    logger.debug(f'Help command received: {msg["text"]}')
                    text = "Welcome to the Weather Bot!\n\n" +\
                        "You can ask the bot for weather info for any city" +\
                        " by sending it the name of the city. Only single" +\
                        " word locations are currently supported.\n" +\
                        "Type \"help\" or \"hello\" to see this message again"
                    webex.sendMessageToRoom(room_id=room_id, text=text)
                    return (data, 200)
                elif len(msg["text"].split()) > 1:
                    logger.debug(f'Invalid command received: {msg["text"]}')
                    text = "Could not process request! Too many words...aghhh"
                    webex.sendMessageToRoom(room_id=room_id, text=text)
                    return (data, 400)
                else:
                    logger.debug(f'Looking up weather info for {msg["text"]}')
                    geolocation = weather.getGeolocationData(msg["text"])
                    weather_info = weather.getCurrentWeather(geolocation)
                    text = json.dumps(weather_info, indent=4)
                    webex.sendMessageToRoom(room_id=room_id, text=text)
                    return (data, 200)
        else:
            return ("Wrong data format", 400)


def main():
    webhook_urls = webex.getWebhooks()
    ngrok_urls = utils.getNgrokURLs()
    if not ngrok_urls:
        utils.startNgrok()
        ngrok_urls = utils.getNgrokURLs()
    target_url = list(set(ngrok_urls) & set(webhook_urls))
    if target_url:
        logger.info(f"Target webhook: {target_url[0]}")
    else:
        webex.registerWebhook(url=ngrok_urls[0], name="NGROK test webhook")
    gateway.run(host="0.0.0.0", port=5005, debug=True)


if __name__ == "__main__":
    main()
