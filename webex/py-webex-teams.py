from datetime import datetime
import requests
import json
from getpass import getpass


def createTeam(token: str, name: str):
    URL = "https://webexapis.com/v1/teams"
    PAYLOAD = {
        "name": "DevNet Team created with Python"
    }
    HEADERS = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
    }

    RESPONSE = requests.request("POST", URL, data=json.dumps(PAYLOAD), headers=HEADERS)
    
    #The lines below are testing code - no need to run them
    
    #formatted_response = json.loads(RESPONSE.text)
    #print(json.dumps(formatted_response, indent=4))

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
    token = getpass("Please input the Webex Teams token:\n")
    message = input("Please input the message you would like to send:\n")
    sendBotMessage(message, token)
    create_team = input("Would you like to create a new team? [Y/N]\n")
    if create_team == "Y":
        team_name = input("Please input the name of the team:\n")
        createTeam(token, name)
    else:
        print("Oke.\n")

if __name__ == "__main__":
    start_time = datetime.now()
    main()
    end_time = datetime.now()
    print(f'\nScript complete, total runtime {end_time - start_time}')