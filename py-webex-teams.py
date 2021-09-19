from datetime import datetime
import requests
import json


def createTeam(token: str):
    URL = "https://webexapis.com/v1/teams"
    PAYLOAD = {
        "name": "DevNet Team created with Python"
    }
    HEADERS = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
    }

    RESPONSE = requests.request("POST", URL, data=json.dumps(PAYLOAD), headers=HEADERS)
    formatted_response = json.loads(RESPONSE.text)
    print(json.dumps(formatted_response, indent=4))

def sendBotMessage(message: str, token: str):
    URL = "https://webexapis.com/v1/messages"
    PAYLOAD = {
        "text": message,
        "toPersonEmail": "vlad.raducanu@virginmedia.co.uk"
    }
    HEADERS = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
    }

    RESPONSE = requests.request("POST", URL, data=json.dumps(PAYLOAD), headers=HEADERS)
    formatted_response = json.loads(RESPONSE.text)
    print(json.dumps(formatted_response, indent=4))

def main():
    token = input("Please input the Webex Teams token:\n")
    message = input("Please input the message you would like to send:\n")
    sendBotMessage(message, token)

if __name__ == "__main__":
    start_time = datetime.now()
    main()
    end_time = datetime.now()
    print(f'\nScript complete, total runtime {end_time - start_time}')