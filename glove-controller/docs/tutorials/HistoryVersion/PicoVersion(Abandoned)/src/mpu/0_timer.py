"""
下面的示例展示如何使用 Timer 来周期性地读取传感器数据。请注意，如果在软重启后出现 OSError: 26 或 i2c driver install error，可能需要进行一次硬重启（按下板上的 RUN/RESET 按钮或者断电重上电）。
"""
import micropython
from machine import I2C, Pin, Timer
from mpu9250 import MPU9250

# 为紧急异常分配缓冲
micropython.alloc_emergency_exception_buf(100)

i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
sensor = MPU9250(i2c)

def read_sensor(timer):
    print("Acceleration:", sensor.acceleration)
    print("Gyro:", sensor.gyro)
    print("Magnetic:", sensor.magnetic)
    print("Temperature:", sensor.temperature)
    print("----")

print("MPU9250 id: " + hex(sensor.whoami))

timer_0 = Timer(0)
# 每1000ms调用一次read_sensor回调
timer_0.init(period=1000, mode=Timer.PERIODIC, callback=read_sensor)
