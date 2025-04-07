#!/usr/bin/env python3
"""
ROS2 Subscriber + GUI Example:
Subscribe to "click" and "motion/detection" topics, and display both states simultaneously.
Additional: Add a channel switch button to the GUI, and publish the current GUI state to the "GUI" topic when the state is updated
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import tkinter as tk
import threading
import json

class ClickListener(Node):
    def __init__(self):
        super().__init__('click_listener')
        
        # subscribe "click" topic
        self.subscription_click = self.create_subscription(
            String,
            'click',
            self.click_callback,
            10
        )
        
        # subscribe "motion/detection" topic
        self.subscription_motion = self.create_subscription(
            String,
            'motion/detection',
            self.motion_callback,
            10
        )
        
        self.click_state = "FALSE"      # DEFAULT PRESS STATUS
        self.motion_state = "STATIONARY" # DEFAULT MOTION STATUS

        self.channel = 1  # DEFAULT CHANNEL 1

        # Create a publisher to publish GUI status messages for use by MQTT
        self.publisher_gui = self.create_publisher(String, 'GUI', 10)
        
    def click_callback(self, msg: String):
        self.click_state = msg.data
        self.get_logger().info(f"RECEIVE CLICK STATE: {self.click_state}")

    def motion_callback(self, msg: String):
        self.motion_state = msg.data
        self.get_logger().info(f"RECEIVE MOTION STATE: {self.motion_state}")

def ros_spin(node):
    rclpy.spin(node)

def main():
    # initialize ROS2 node
    rclpy.init()
    click_listener = ClickListener()
    
    # Run ROS2 spin in a separate thread to avoid blocking the GUI main loop
    # (单独线程运行 ROS2 spin，避免阻塞 GUI 主循环)
    ros_thread = threading.Thread(target=ros_spin, args=(click_listener,), daemon=True)
    ros_thread.start()
    
    # create Tkinter GUI window
    root = tk.Tk()
    root.title("Click & Motion State Detector")
    
    # create Label, show click status 
    label_click = tk.Label(root, text="Not Pressed", font=("Arial", 32), width=20, height=3, bg="green")
    label_click.pack(padx=20, pady=10)

    # create Label, show motion status 
    label_motion = tk.Label(root, text="STATIONARY", font=("Arial", 32), width=20, height=3, bg="yellow")
    label_motion.pack(padx=20, pady=10)
    
    # add channel switch module: 1, 2, 3
    def switch_channel():
        # 按顺序切换：1 -> 2 -> 3 -> 1
        if click_listener.channel == 1:
            click_listener.channel = 2
        elif click_listener.channel == 2:
            click_listener.channel = 3
        else:
            click_listener.channel = 1
        btn_channel.config(text=f"Channel: {click_listener.channel}")
        click_listener.get_logger().info(f"Channel switched to: {click_listener.channel}")

    btn_channel = tk.Button(root, text=f"Channel: {click_listener.channel}", font=("Arial", 24), command=switch_channel)
    btn_channel.pack(padx=20, pady=10)
    
    def update_labels():
        # update press status
        if click_listener.click_state == "TRUE":
            label_click.config(text="Pressed", bg="red")
            publish_click = "pressed"
        else:
            label_click.config(text="Not Pressed", bg="green")
            publish_click = "not_pressed"

        # update motion status
        if click_listener.motion_state in ["LIFT_START", "LIFT_COMPLETE"]:
            label_motion.config(text="LIFTING", bg="red")
            publish_motion = "lifting"
        elif click_listener.motion_state in ["DROP_START", "DROP_COMPLETE"]:
            label_motion.config(text="DROPPING", bg="blue")
            publish_motion = "dropping"
        elif click_listener.motion_state == "STATIONARY":
            label_motion.config(text="STATIONARY", bg="yellow")
            publish_motion = "stationary"
        else:
            label_motion.config(text="UNKNOWN", bg="grey")
            publish_motion = "error"

        # 获取当前频道信息8
        publish_channel = str(click_listener.channel)
        
        # 构造要发布的消息
        payload = {
            "click": publish_click,
            "motion": publish_motion,
            "channel": publish_channel
        }
        msg = String()
        msg.data = json.dumps(payload)
        click_listener.publisher_gui.publish(msg)
        
        # 每隔 100 毫秒更新一次
        root.after(100, update_labels)
    
    update_labels()  # 启动定时器
    root.mainloop()
    
    # GUI 关闭后清理 ROS2 节点
    click_listener.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
