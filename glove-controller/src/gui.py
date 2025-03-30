#!/usr/bin/env python3
"""
click_gui.py
ROS2 订阅者 + GUI 示例：
订阅 "click" 和 "motion/detection" 话题，并同时显示两个状态。
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import tkinter as tk
import threading

class ClickListener(Node):
    def __init__(self):
        super().__init__('click_listener')
        
        # 订阅 "click" 话题
        self.subscription_click = self.create_subscription(
            String,
            'click',
            self.click_callback,
            10
        )
        
        # 订阅 "motion/detection" 话题
        self.subscription_motion = self.create_subscription(
            String,
            'motion/detection',
            self.motion_callback,
            10
        )
        
        self.click_state = "FALSE"      # 默认按压状态
        self.motion_state = "STATIONARY" # 默认运动状态

    def click_callback(self, msg: String):
        self.click_state = msg.data
        self.get_logger().info(f"收到按压状态: {self.click_state}")

    def motion_callback(self, msg: String):
        self.motion_state = msg.data
        self.get_logger().info(f"收到运动状态: {self.motion_state}")

def ros_spin(node):
    rclpy.spin(node)

def main():
    # 初始化 ROS2 节点
    rclpy.init()
    click_listener = ClickListener()
    
    # 单独线程运行 ROS2 spin，避免阻塞 GUI 主循环
    ros_thread = threading.Thread(target=ros_spin, args=(click_listener,), daemon=True)
    ros_thread.start()
    
    # 创建 Tkinter GUI 窗口
    root = tk.Tk()
    root.title("Click & Motion State Detector")
    
    # 创建两个 Label 显示点击状态和运动状态
    label_click = tk.Label(root, text="Not Pressed", font=("Arial", 32), width=20, height=3, bg="green")
    label_click.pack(padx=20, pady=10)

    label_motion = tk.Label(root, text="STATIONARY", font=("Arial", 32), width=20, height=3, bg="yellow")
    label_motion.pack(padx=20, pady=10)
    
    def update_labels():
        # 更新按压状态
        if click_listener.click_state == "TRUE":
            label_click.config(text="Pressed", bg="red")
        else:
            label_click.config(text="Not Pressed", bg="green")

        # 更新运动状态
        if click_listener.motion_state in ["LIFT_START", "LIFT_COMPLETE"]:
            label_motion.config(text="LIFTING", bg="red")
        elif click_listener.motion_state in ["DROP_START", "DROP_COMPLETE"]:
            label_motion.config(text="DROPPING", bg="blue")
        elif click_listener.motion_state == "STATIONARY":
            label_motion.config(text="STATIONARY", bg="yellow")
        else:
            label_motion.config(text="UNKNOWN", bg="grey")

        # 每隔 100 毫秒更新一次
        root.after(100, update_labels)
    
    update_labels()  # 启动定时器
    root.mainloop()
    
    # GUI 关闭后清理 ROS2 节点
    click_listener.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()















# #!/usr/bin/env python3
# """
# click_gui.py
# ROS2 订阅者 + GUI 示例：
# 订阅 "click" 话题，根据接收到的点击状态显示对应的动画状态。
# """

# import rclpy
# from rclpy.node import Node
# from std_msgs.msg import String
# import tkinter as tk
# import threading

# class ClickListener(Node):
#     def __init__(self):
#         super().__init__('click_listener')
#         # 订阅 "click" 话题
#         self.subscription = self.create_subscription(
#             String,
#             'click',
#             self.listener_callback,
#             10
#         )
#         self.subscription  # 防止未使用变量警告
#         self.click_state = "FALSE"  # 默认状态

#     def listener_callback(self, msg: String):
#         self.click_state = msg.data
#         self.get_logger().info(f"收到点击状态: {self.click_state}")

# def ros_spin(node):
#     rclpy.spin(node)

# def main():
#     # 初始化 ROS2 节点
#     rclpy.init()
#     click_listener = ClickListener()
    
#     # 单独线程运行 ROS2 spin，避免阻塞 GUI 主循环
#     ros_thread = threading.Thread(target=ros_spin, args=(click_listener,), daemon=True)
#     ros_thread.start()
    
#     # 创建 Tkinter GUI 窗口
#     root = tk.Tk()
#     root.title("Click State Detector")
    
#     # 创建一个 Label 显示点击状态
#     label = tk.Label(root, text="Not Pressed", font=("Arial", 32), width=20, height=5, bg="green")
#     label.pack(padx=20, pady=20)
    
#     def update_label():
#         # 根据 click_listener.click_state 更新 Label 的显示和背景颜色
#         if click_listener.click_state == "TRUE":
#             label.config(text="Pressed", bg="red")
#         else:
#             label.config(text="Not Pressed", bg="green")
#         # 每隔 100 毫秒更新一次
#         root.after(100, update_label)
    
#     update_label()  # 启动定时器
#     root.mainloop()
    
#     # GUI 关闭后清理 ROS2 节点
#     click_listener.destroy_node()
#     rclpy.shutdown()

# if __name__ == '__main__':
#     main()
