import random
from . import REAL_MODE

if REAL_MODE:
    import Adafruit_DHT
    DHT_SENSOR = Adafruit_DHT.DHT22
    DHT_PIN = 4

def read_humidity():
    if REAL_MODE:
        humidity, _ = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
        return round(humidity, 2) if humidity else None
    return round(random.uniform(30.0, 80.0), 2)
