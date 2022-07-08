import requests
import os
import json
import base64
import urllib3
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# This section contains the essential variables for the script. DNAC details are read from the '.env' file present in the folder.
# The 'RETENTION' variable specifies the number of backups to be kept - edit it as needed

DNAC_URL = os.environ.get("DNA_CENTER_BASE_URL")
DNAC_USER = os.environ.get("DNA_CENTER_USERNAME")
DNAC_PASS = os.environ.get("DNA_CENTER_PASSWORD")
WEBEX_TOKEN = os.environ.get("WEBEX_TOKEN")
RETENTION_POLICY = 1

def getAuthenticationToken():
    url = DNAC_URL + "/dna/system/api/v1/auth/token"
    auth2encode = DNAC_USER + ":" + DNAC_PASS
    auth = base64.b64encode(auth2encode.encode('UTF-8')).decode('ASCII')
    headers = {
            "Accept": "application/json",
            "Authorization": "Basic " + auth,
            "Content-Type": "application/json"
        }

    try:
        response = requests.post(url, headers=headers, verify = False)
    except requests.exceptions.Timeout as e:
        print("Operation timed out!")
        raise SystemError(e)
    except requests.exceptions.ConnectionError as e:
        print("Connection error - please check network connectivity!")
        raise SystemExit(e)
    except requests.exceptions.HTTPError as e:
        print("HTTP error encountered!")
        raise SystemExit(e)
    
    if response.status_code >=200 and response.status_code<=299:
        print("Authentication successfull!")
    else:
        print("Authentication failed! See message below for more info!\n", response.content)
        sys.exit()
    token = json.loads(response.content)

    return token["Token"]

def getBackupsList(token):
    url = DNAC_URL + "/api/system/v1/maglev/backup"
    headers = {
            "x-auth-token": token,
            "Content-Type": "application/json"
        }

    try:
        response = requests.get(url, headers=headers, verify = False)
    except requests.exceptions.Timeout as e:
        print("Operation timed out!")
        raise SystemError(e)
    except requests.exceptions.ConnectionError as e:
        print("Connection error - please check network connectivity!")
        raise SystemExit(e)
    except requests.exceptions.HTTPError as e:
        print("HTTP error encountered!")
        raise SystemExit(e)
    
    if response.status_code >=200 and response.status_code<=299:
        print("\nBackups list successfully retrieved!")
        backups_list = json.loads(response.content)
        index = 1
        print(f"There are currently {len(backups_list['response'])} backups available for this DNAC node:")
        for item in sorted(backups_list['response'], key=lambda d: d['start_timestamp'], reverse=True):
            backup_start_time = datetime.fromtimestamp(item['start_timestamp']).replace(microsecond=0)
            backup_end_time = datetime.fromtimestamp(item['end_timestamp']).replace(microsecond=0)
            print(f"{index} - Name: {item['description']} -> Size: {item['backup_size'] / 1000000} MB -> Start time: {backup_start_time} -> End time: {backup_end_time}-> Completion status: {item['status']}")
            index+=1

        return sorted(backups_list['response'], key=lambda d: d['start_timestamp'])

def getBackupsHistory(token):
    # Unused function

    url = DNAC_URL + "/api/system/v1/maglev/backup/history"
    headers = {
            "x-auth-token": token,
            "Content-Type": "application/json"
        }

    try:
        response = requests.get(url, headers=headers, verify = False)
    except requests.exceptions.Timeout as e:
        print("Operation timed out!")
        raise SystemError(e)
    except requests.exceptions.ConnectionError as e:
        print("Connection error - please check network connectivity!")
        raise SystemExit(e)
    except requests.exceptions.HTTPError as e:
        print("HTTP error encountered!")
        raise SystemExit(e)
    
    if response.status_code >=200 and response.status_code<=299:
        print("Backups history successfully retrieved!")
        backups_history = json.loads(response.content)
        print(json.dumps(backups_history['response'], indent = 2))
    else:
        print("An issue has been ecountered!\n", response.content)

def deleteOldestBackup(token, backups_list):
    # Select the oldest backup ID to delete (1st element in the backups list) and use it in the API call to delete it

    id_of_item_to_delete = backups_list[0]["backup_id"]

    print(f"\nAttempting to delete backup {backups_list[0]['description']}")

    url = DNAC_URL + "/api/system/v1/maglev/backup/" + id_of_item_to_delete
    headers = {
            "x-auth-token": token,
            "Content-Type": "application/json"
        }
    
    try:
        response = requests.delete(url, headers=headers, verify = False)
    except requests.exceptions.Timeout as e:
        print("Operation timed out!")
        raise SystemError(e)
    except requests.exceptions.ConnectionError as e:
        print("Connection error - please check network connectivity!")
        raise SystemExit(e)
    except requests.exceptions.HTTPError as e:
        print("HTTP error encountered!")
        raise SystemExit(e)

    if response.status_code >=200 and response.status_code<=299:
        print(f"Backup {backups_list[0]['description']} has been successfully deleted!")
    else:
        print("An issue has been ecountered!\n", response.content)

def applyBackupPolicy(token):
    # Get list of backups currently present on DNAC
    print(f"\nCurrent backup policy: keep newest {RETENTION_POLICY} backup(s).")
    
    backups_list = getBackupsList(token)
    index = 0 

    while len(backups_list) > RETENTION_POLICY:
        index+=1
        deleteOldestBackup(token, backups_list)
        backups_list = getBackupsList(token)

    print(f"\nPolicy has been applied! {index} old backup(s) have been purged.")
    sendWebexMessage(f"Policy has been applied! {index} old backup(s) have been purged.")

def sendWebexMessage(message: str):
    webex_url = "https://webexapis.com/v1/messages"
    payload = {
        "text": message,
        "toPersonEmail": "vlad.raducanu@virginmedia.co.uk"
    }
    headers = {
        "Authorization": "Bearer " + WEBEX_TOKEN,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(webex_url, data=json.dumps(payload), headers=headers, verify = False)
    except requests.exceptions.Timeout as e:
        print("Operation timed out!")
        raise SystemError(e)
    except requests.exceptions.ConnectionError as e:
        print("Connection error - please check network connectivity!")
        raise SystemExit(e)
    except requests.exceptions.HTTPError as e:
        print("HTTP error encountered!")
        raise SystemExit(e)

    if response.status_code >=200 and response.status_code<=299:
        formatted_response = json.loads(response.text)
        print(json.dumps(formatted_response, indent=4))
    else:
        print("An issue has been ecountered!\n", response.content)
    

def main():
    token = getAuthenticationToken()
    # backups_list = getBackupsList(token)
    # deleteOldestBackup(token, backups_list)
    # backups_list = getBackupsList(token)
    applyBackupPolicy(token)
    

if __name__ == "__main__":
    main()