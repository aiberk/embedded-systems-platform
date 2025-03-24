"""
MPU9250:
SDA → GP0 (Pin 1)
SCL → GP1 (Pin 2)
GND → Pin 36
VCC → Pin 38
"""

"""
example use (公制单位 m/s^2)
"""
import utime
from machine import I2C, Pin
from mpu9250 import MPU9250

# 1. INITIALIZE I2C
#    scl=Pin(1)  --> GP1
#    sda=Pin(0)  --> GP0
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)

# 2. INITIALIZE MPU9250
sensor = MPU9250(i2c)

# 3. READ MPU9250 ID
print("MPU9250 id: " + hex(sensor.whoami))

# 4. Loop to read sensor data
while True:
    print("Acceleration (m/s^2):", sensor.acceleration)
    print("Gyro (rad/s):", sensor.gyro)
    print("Magnetic (uT):", sensor.magnetic)
    print("Temperature (C):", sensor.temperature)
    print("----")
    utime.sleep(1)
