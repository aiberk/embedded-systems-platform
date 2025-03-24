"""
pc_receiver.py

此脚本在电脑端运行，用于接收来自Pico的实时传感器数据。
使用方法:
1. 将Pico通过USB连接到电脑
2. 在Pico上运行collect_uart.py
3. 在电脑上运行此脚本接收数据
"""

import serial
import time
import csv
import os
from datetime import datetime

# 配置串口
PORT = "COM3"  # Windows上通常是COMx，Linux上是/dev/ttyACMx，MacOS上是/dev/cu.usbmodemxxxx
BAUD_RATE = 115200

def receive_data():
    try:
        # 创建输出文件名，包含时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"motion_data_{timestamp}.csv"
        
        print(f"尝试连接到 {PORT} 以接收数据...")
        
        # 打开串口连接
        with serial.Serial(PORT, BAUD_RATE, timeout=1) as ser:
            print(f"成功连接到 {PORT}！")
            print(f"数据将保存到 {filename}")
            
            # 打开CSV文件用于写入
            with open(filename, 'w', newline='') as csvfile:
                # 等待并读取表头
                header = ser.readline().decode('utf-8').strip()
                csvfile.write(header + '\n')
                print("接收到表头: " + header)
                
                print("开始接收数据...")
                print("按 Ctrl+C 停止")
                
                try:
                    while True:
                        # 读取一行数据
                        line = ser.readline().decode('utf-8').strip()
                        
                        if line:
                            # 写入CSV文件
                            csvfile.write(line + '\n')
                            csvfile.flush()  # 立即写入磁盘
                            print(f"接收到数据: {line}")
                except KeyboardInterrupt:
                    print("\n数据接收已停止")
                    
            print(f"数据已保存到 {filename}")
            
    except serial.SerialException as e:
        print(f"串口错误: {e}")
        print("请检查:")
        print("1. Pico是否已连接到电脑")
        print("2. 端口名是否正确 (当前设置为 {PORT})")
        print("3. 是否已在Pico上运行数据收集脚本")
        
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    # 列出可用的串口供参考
    try:
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        if ports:
            print("可用串口:")
            for p in ports:
                print(f" - {p}")
            print(f"当前设置使用: {PORT}")
            
            # 允许用户选择端口
            user_port = input(f"使用默认端口 {PORT} 吗? 输入新端口名或按回车继续: ")
            if user_port:
                PORT = user_port
                
        else:
            print("未检测到串行端口。请确保Pico已连接。")
    except:
        pass
        
    # 开始接收数据
    receive_data()