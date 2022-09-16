import requests
import os
import logging
from dotenv import load_dotenv

# Initialize logger
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class OpenWeather():
    def __init__(self):
        self.base_url = "https://api.openweathermap.org"
        self.api_token = os.environ["WEATHER_API_TOKEN"]

    def _makeRequest(self, method: str, endpoint: str):
        url = self.base_url + endpoint
        try:
            logger.debug(f"Executing {method} - {url}")
            response = requests.request(
                method=method, url=url, verify=True
            )
            logger.debug(f"Response received:\n{response.json()}\n")
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
            logger.debug("Operation successful!")

        return response.json()

    def getGeolocationData(self, location: str) -> dict:
        logger.info(f"Retrieving geolocation data for {location}...")
        endpoint = "/geo/1.0/direct?q=" + location + "&appid=" + self.api_token
        response = self._makeRequest(method="GET", endpoint=endpoint)
        if response:
            match = response[0]
            return match
        else:
            logger.warning(f"Could not find geolocation data for {location}!")
            return {}

    def getCurrentWeather(self, geo_data: dict) -> dict:
        if geo_data:
            logger.info(f'Retrieving weather info for {geo_data["name"]}')
            endpoint = "/data/2.5/weather?lat=" + str(geo_data["lat"]) +\
                "&lon=" + str(geo_data["lon"]) +\
                "&appid=" + self.api_token
            response = self._makeRequest(method="GET", endpoint=endpoint)
            if response:
                weather_data = {}
                weather_data["location"] = geo_data["name"]
                weather_data["w_main"] = response["weather"][0]["main"]
                weather_data["w_desc"] = response["weather"][0]["description"].capitalize()
                weather_data["tmp"] = round(response["main"]["temp"] - 273, 2)
                weather_data["tmp_feel"] = round(response["main"]["feels_like"] - 273, 2)
                weather_data["tmp_min"] = round(response["main"]["temp_min"] - 273, 2)
                weather_data["temp_max"] = round(response["main"]["temp_max"] - 273, 2)
                weather_data["pressure"] = response["main"]["pressure"] / 1000
                weather_data["humidity"] = response["main"]["humidity"]
                return weather_data
        else:
            logger.warning("Geolocation data missing!")
            return {}
