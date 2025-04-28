import random
from . import REAL_MODE

if REAL_MODE:
    import smbus2

    DEVICE = 0x23
    ONE_TIME_HIGH_RES_MODE_1 = 0x20
    bus = smbus2.SMBus(1)

def read_light():
    if REAL_MODE:
        try:
            data = bus.read_i2c_block_data(DEVICE, ONE_TIME_HIGH_RES_MODE_1)
            result = (data[1] + (256 * data[0])) / 1.2
            return round(result, 2)
        except Exception:
            return None
    return random.randint(100, 1000)
