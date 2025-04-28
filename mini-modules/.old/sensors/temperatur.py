import random
from . import REAL_MODE

if REAL_MODE:
    import Adafruit_DHT
    DHT_SENSOR = Adafruit_DHT.DHT22
    DHT_PIN = 4  # BCM Pin 4

def read_temperature():
    if REAL_MODE:
        _, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
        return round(temperature, 2) if temperature else None
    return round(random.uniform(20.0, 35.0), 2)
