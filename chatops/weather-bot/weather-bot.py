from importlib.metadata import files
import json
import logging
import logging.config
from jinja_templates import templates
from modules import utils, webex_module, weather_module
from flask import Flask, request
from requests_toolbelt.multipart.encoder import MultipartEncoder

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


@gateway.route("/weather", methods=["GET", "POST"])
def index() -> tuple:
    if request.method == "GET":
        logger.info("GET request received.")
        return (f"Request received via {request.host}", 200)
    elif request.method == "POST":
        logger.info("POST request received.")
        if "application/json" in request.headers.get("Content-Type"):
            data = request.get_json()
            printable_data = json.dumps(data, indent=2)
            logger.debug(f"Notification contents:\n{printable_data}")
            # Filter out messages from self
            if webex.bot_id == data.get("data").get("personId"):
                return ("Message from self ignored.", 200)
            else:
                # Read message contents
                room_id = data["data"]["roomId"]
                data_id = data["data"]["id"]
                user_id = data["data"]["personId"]
                time = data["data"]["created"]
                if "personEmail" in data["data"]:
                    user_email = data["data"]["personEmail"]
                if data["resource"] == "messages" and data["event"] == "created":
                    msg_contents = webex.getMessage(message_id=data_id)
                    # Check message text contents and reply
                    if "text" in msg_contents:
                        if msg_contents["text"].lower() in ["hello", "help"]:
                            logger.debug(f'Help command received: {msg_contents["text"]}')
                            attachments = json.loads(templates.J2_HELLO.render())
                            logger.debug(f"Attachment: \n\n\n {attachments} \n\n\n")
                            text = attachments["content"]["body"][0]["text"] + "\n" +\
                                attachments["content"]["body"][1]["columns"][1]["items"][0]["text"]
                            webex.sendMessageToRoom(
                                room_id=room_id, text=text, attachments=attachments)
                            return ("OK", 200)
                        elif msg_contents["text"].lower() in "start":
                            logger.debug(f'Start command received:{msg_contents["text"]}')
                            attachments = json.loads(templates.J2_START.render())
                            text = attachments["content"]["body"][1]["text"]
                            webex.sendMessageToRoom(
                                room_id=room_id, text=text, attachments=attachments)
                            return ("OK", 200)
                        elif msg_contents["text"].lower() in "pint":
                            logger.info("Coming right up!")
                            text = "Enjoy!"
                            m = MultipartEncoder(
                                {
                                    "roomId": room_id,
                                    "text": text,
                                    "files": ("pint.png", open("images/pint.png", "rb"), "image/png")
                                }
                            )
                            webex.sendMessageToRoom(room_id=room_id, files=m, special=True)
                            return ("OK", 200)
                        else:
                            logger.debug(f'Looking up weather info for {msg_contents["text"]}')
                            geolocation = weather.getGeolocationData(msg_contents["text"])
                            if len(geolocation) != 0:
                                weather_info = weather.getCurrentWeather(geolocation)
                                text = json.dumps(weather_info, indent=2)
                                attachments = json.loads(templates.J2_WEATHER.render(weather_info))
                                webex.sendMessageToRoom(room_id=room_id, text=text, attachments=attachments)
                                return (data, 200)
                            else:
                                text = f'Could not find {msg_contents["text"]}'
                                attachments = json.loads(templates.J2_INVALID.render(msg_contents))
                                webex.sendMessageToRoom(room_id=room_id, text=text, attachments=attachments)
                                return (data, 400)
                elif data["resource"] == "attachmentActions" and data["event"] == "created":
                    action_contents = webex.getAttachmentActionData(
                        action_id=data_id)
                    if "inputs" in action_contents:
                        logger.debug(f'Action notification received:{action_contents["inputs"]}')
                        location = action_contents["inputs"]["location"]
                        logger.debug(f'Looking up weather info for {location}')
                        geolocation = weather.getGeolocationData(location)
                        weather_info = weather.getCurrentWeather(geolocation)
                        text = json.dumps(weather_info, indent=2)
                        attachments = json.loads(templates.J2_WEATHER.render(weather_info))
                        webex.sendMessageToRoom(
                            room_id=room_id, text=text, attachments=attachments
                        )
                    return (data, 200)
        else:
            return ("Wrong data format. Please use JSON.", 400)


def main():
    webhook_urls = webex.getWebhooks()
    ngrok_urls = utils.getNgrokURLs()
    if not ngrok_urls:
        logger.debug("No active Ngrok sessions found! Starting Ngrok...")
        utils.startNgrok()
        ngrok_urls = utils.getNgrokURLs()
    target_url = list(set(ngrok_urls) & set(webhook_urls))
    if target_url:
        logger.info(f"Target webhook: {target_url[0]}")
    else:
        url = ngrok_urls[0] + "/weather"
        webex.deleteNgrokWebhooks()
        webex.registerWebhook(
            url=url, name="NGROK general wh", resource="all")
        webex.registerWebhook(
            url=url, name="NGROK action wh", resource="attachmentActions")
    gateway.run(host="0.0.0.0", port=5005, debug=True)


if __name__ == "__main__":
    main()
