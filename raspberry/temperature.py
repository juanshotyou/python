import Adafruit_DHT
from time import sleep

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

while True:
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    print(f"Current temperature {temperature:.2f} °C\nCurrent humidity {humidity:.2f} %\n")
    sleep(1)
