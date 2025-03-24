"""
如果希望加速度以 g、角速度以 °/s 输出，可以像下面这样设置：
"""

import utime
from machine import I2C, Pin
from mpu9250 import MPU9250
from mpu6500 import MPU6500, SF_G, SF_DEG_S

i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)

# 使用mpu6500子类，指定量程转换系数
mpu6500 = MPU6500(i2c, accel_sf=SF_G, gyro_sf=SF_DEG_S)

# 将mpu6500对象传给MPU9250的构造函数
sensor = MPU9250(i2c, mpu6500=mpu6500)

print("MPU9250 id: " + hex(sensor.whoami))

while True:
    print("Acceleration (g):", sensor.acceleration)
    print("Gyro (deg/s):", sensor.gyro)
    print("Magnetic (uT):", sensor.magnetic)
    print("Temperature (C):", sensor.temperature)
    print("----")
    utime.sleep(1)
