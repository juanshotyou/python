import os
import json
from string import printable
import requests
import logging
from dotenv import load_dotenv

# Initialize logger
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Define Messenger class (handles interaction with Webex Teams API)


class Messenger:
    def __init__(self):
        self.base_url = os.environ["WEBEX_BASE_URL"]
        self.api_key = os.environ["WEBEX_BOT_ACCESS_TOKEN"]
        self.bot_id = os.environ["WEBEX_BOT_ID"]
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _makeRequest(
        self,
        method: str,
        endpoint: str,
        payload: dict = {}
    ) -> dict:
        url = self.base_url + endpoint
        data = {}
        try:
            logger.debug(f"Executing {method} - {url} \n {payload}")
            if payload:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    data=json.dumps(payload),
                    verify=True,
                )
            else:
                response = requests.request(
                    method=method, url=url, headers=self.headers, verify=True
                )
        except requests.exceptions.Timeout as e:
            logger.error(f"Operation timed out:\n{e}")
            logger.info("Please check connectivity and try again!")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error:\n{e}")
            logger.info("Please check connectivity and try again!")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error:\n{e}")
            logger.info("Please check HTTPS/TLS settings and try again!")

        # Determine outcome of low level request
        if response.status_code >= 400 or response.status_code < 200:
            logger.error(
                f"Operation failed: {response.status_code}\n"
                f"{response.text}"
            )
        elif response.status_code >= 200 or response.status_code < 300:
            logger.info("Operation successful!")

        # Return data if needed
        if response.content:
            data = json.loads(response.content)

        return data

    def getWebhooks(self) -> list:
        logger.info("Retrieving webhooks from Webex API...")
        endpoint = "/webhooks"
        webhook_urls = []
        webhooks = self._makeRequest(method="GET", endpoint=endpoint)
        for webhook in webhooks["items"]:
            webhook_urls.append(webhook["targetUrl"])
            logger.debug(
                f'Found {webhook["name"]}:\n{json.dumps(webhook, indent=2)}\n')
        return webhook_urls

    def registerWebhook(
        self, url: str, name: str, resource: str = "all", event: str = "all"
    ) -> None:
        logger.info(f"Registering webhook {name} with target {url}...")
        endpoint = "/webhooks"
        data = {
            "name": name,
            "resource": resource,
            "event": event,
            "targetUrl": url
        }
        self._makeRequest(method="POST", endpoint=endpoint, payload=data)

    def deleteWebhook(self, webhook_id: str) -> None:
        logger.info(f"Deleting webhook {webhook_id}")
        endpoint = "/webhooks/" + webhook_id
        self._makeRequest(method="DELETE", endpoint=endpoint)

    def deleteNgrokWebhooks(self) -> None:
        logger.info(f"Deleting all Ngrok webhooks...")
        endpoint = "/webhooks"
        webhooks = self._makeRequest(method="GET", endpoint=endpoint)
        logger.debug(f"Webhooks found:\n{webhooks}\n")
        if webhooks["items"]:
            for webhook in webhooks["items"]:
                logger.debug(f"{webhook}")
                if "ngrok" in webhook["name"].lower():
                    logger.info(f'Deleting webhook {webhook["name"]}')
                    self.deleteWebhook(webhook_id=webhook["id"])

    def getBotID(self) -> str:
        logger.info("Retrieving BOT ID...")
        endpoint = "/people/me"
        response = self._makeRequest(method="GET", endpoint=endpoint)
        bot_id = response["id"]
        return bot_id

    def getMessage(self, message_id: str) -> dict:
        logger.info(f"Retrieving message {message_id}")
        endpoint = "/messages/" + message_id
        response = self._makeRequest(method="GET", endpoint=endpoint)
        logger.debug(f"Message retrieved:\n{json.dumps(response, indent=2)}\n")
        return response

    def getAttachmentActionData(self, action_id: str) -> dict:
        logger.info(f"Retrieving attachment action {action_id}")
        endpoint = "/attachment/actions/"+ action_id
        response = self._makeRequest(method="GET", endpoint=endpoint)
        logger.debug(f"Attachment action retrieved:\n{json.dumps(response, indent=2)}\n")
        return response

    def getPersonInfo(self, person_id: str) -> dict:
        logger.debug(f"Retrieving information for ID {person_id}")
        endpoint = "/people/" + person_id
        response = self._makeRequest(method="GET", endpoint=endpoint)
        return response

    def sendMessageToRoom(
        self,
        room_id: str,
        text: str = None,
        files: str = None,
        attachments: dict = None
    ) -> None:
        logger.info(f"Sending message to room {room_id}")
        endpoint = "/messages"
        data = {
            "roomId": room_id,
            "text": text
        }
        if attachments:
            data["attachments"] = [attachments]  # For Adaptive cards
        if files:
            data["files"] = files  # Must be URL to file
        logger.debug(f"Message contents: \n{json.dumps(data, indent=2)}\n")
        self._makeRequest(method="POST", endpoint=endpoint, payload=data)

    def sendMessageToPersonEmail(self, email: str, message: str) -> None:
        logger.info(f"Sending message to {email}")
        endpoint = "/messages"
        data = {"toPersonEmail": email, "text": message}
        self._makeRequest(method="POST", endpoint=endpoint, payload=data)

    def sendMessageToPersonID(self, user_id: str, message: str) -> None:
        logger.infor(f"Sending message to {user_id}")
        endpoint = "/messages"
        data = {"toPersonId": user_id, "text": message}
        self._makeRequest(method="POST", endpoint=endpoint, payload=data)

    def downloadFiles(self, files: list) -> None:
        for file in files:
            filename = file.split("/")[-1]
            with open(file=filename, mode="wb") as file_content:
                content = requests.get(
                    url=file, headers=self.headers, stream=True).content
                file_content.write(content)
