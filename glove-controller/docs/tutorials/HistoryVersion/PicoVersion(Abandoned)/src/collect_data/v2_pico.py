"""
collect_uart.py

本脚本从MPU9250收集传感器数据并通过串口实时发送到电脑。
硬件连接 (参考文档):
  SDA → GP0 (Pin 1)
  SCL → GP1 (Pin 2)
  GND → Pin 36
  VCC → Pin 38

采集流程:
1. 收集两个动作的数据: 抬起手臂和放下手臂。
2. 对于每个动作，系统会提示您输入'y'开始数据收集（约2秒）。
3. 数据收集在指定时间后自动停止，并转到下一个动作，直到所有周期完成。
4. 收集的数据通过USB串口实时发送到电脑。
"""

import utime
from machine import I2C, Pin, UART
import sys
from mpu9250 import MPU9250

# ---------------------------
# 1. 初始化I2C、MPU9250传感器和UART
# ---------------------------
# 注意: sda=GP0, scl=GP1
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
sensor = MPU9250(i2c)
print("MPU9250 id: " + hex(sensor.whoami))

# 初始化UART (默认通过USB发送)
# 使用系统默认的USB串口，这样数据会通过USB发送到电脑
uart = UART(0, baudrate=115200)

# ---------------------------
# 2. 数据采集设置
# ---------------------------
# 定义两个动作: 抬起手臂然后放下手臂
actions = [("raise", "RaiseArm"), ("lower", "LowerArm")]

# 设置每个动作的采集时长（秒）和采样间隔（秒）
trial_duration = 1      # 每个动作采集2秒
sampling_interval = 0.1 # 采样间隔100毫秒

# 提示用户输入每个动作的循环次数
try:
    num_cycles = int(input("Each action's cycle time (eg, 3): "))
except Exception as e:
    print("invalid input, initial as 1")
    num_cycles = 1

# 发送CSV表头到电脑
header = "action,time,acc_x,acc_y,acc_z,gyro_x,gyro_y,gyro_z,mag_x,mag_y,mag_z,temp\n"
uart.write(header)

# ---------------------------
# 3. 数据采集循环并实时发送到电脑
# ---------------------------
for cycle in range(num_cycles):
    print("======== 循环 {}/{} ========".format(cycle+1, num_cycles))
    # 按顺序循环每个动作
    for label, prompt in actions:
        print("Action: {}".format(prompt))
        # 等待用户输入'y'开始采集
        while True:
            start_cmd = input("input 'y' to start data collection: ").strip().lower()
            if start_cmd == 'y':
                break
            else:
                print("输入无效。请输入'y'开始。")
        
        print("开始采集'{}' {}秒的数据...".format(prompt, trial_duration))
        start_time = utime.ticks_ms()
        elapsed = 0
        
        while elapsed < trial_duration * 1000:
            current_time = utime.ticks_ms()
            elapsed = utime.ticks_diff(current_time, start_time)
            
            # 读取传感器数据
            acc = sensor.acceleration   # (x, y, z) 单位 m/s^2
            gyro = sensor.gyro          # (x, y, z) 单位 rad/s
            mag = sensor.magnetic       # (x, y, z) 单位 uT
            temp = sensor.temperature   # 温度，单位 摄氏度

            # 格式化一个样本为CSV行 (时间单位为毫秒)
            csv_line = "{},{},{},{},{},{},{},{},{},{},{}\n".format(
                label, elapsed,
                acc[0], acc[1], acc[2],
                gyro[0], gyro[1], gyro[2],
                mag[0], mag[1], mag[2],
                temp
            )
            
            # 通过串口发送到电脑
            uart.write(csv_line)
            utime.sleep(sampling_interval)
            
        print("Action'{}'data collect complete..\n".format(prompt))
        utime.sleep(1)  # 动作之间短暂停顿

print("all cycle done.")
print("sent to pc.")