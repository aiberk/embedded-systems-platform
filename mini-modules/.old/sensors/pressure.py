import random
from . import REAL_MODE

if REAL_MODE:
    import board
    import busio
    import adafruit_bmp280

    i2c = busio.I2C(board.SCL, board.SDA)
    bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)

def read_pressure():
    if REAL_MODE:
        try:
            return round(bmp280.pressure, 2)
        except Exception:
            return None
    return round(random.uniform(980, 1025), 2)
