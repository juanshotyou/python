import requests
import json

URL = "https://postman-echo.com/get"
QUERRY = {"test" : "123"}
HEADERS = {}

response = requests.request("GET", URL, headers = HEADERS, params = QUERRY)
json_response = json.loads(response.text)

print(json.dumps(json_response, indent = 4))