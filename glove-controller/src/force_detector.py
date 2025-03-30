#!/usr/bin/env python3
"""
force_detector.py
ROS2 订阅者示例：
监听 "force_sensor" 话题，接收来自 FSR402 的传感器数据，
并根据力值判断发布“click”话题状态：
    - 当力值大于 20000 时，发布 "TRUE"
    - 当力值小于等于 20000 时，发布 "FALSE"
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32, String

class ForceDetector(Node):
    def __init__(self):
        super().__init__('force_detector')
        # 创建订阅者，订阅 'force_sensor' 话题，消息类型为 Int32
        self.subscription = self.create_subscription(
            Int32,
            'force_sensor',
            self.listener_callback,
            10
        )
        self.subscription  # 防止未使用变量警告

        # 创建发布者，发布 'click' 话题，消息类型为 String
        self.click_pub = self.create_publisher(String, 'click', 10)
        
        # 设定力的阈值为 20000
        self.force_threshold = 20000
        self.get_logger().info(f"Force Detector 已启动，阈值设定为 {self.force_threshold}")

    def listener_callback(self, msg: Int32):
        force_value = msg.data
        self.get_logger().info(f"Force Sensor Data: {force_value}")
        
        # 根据力值判断按压状态
        if force_value > self.force_threshold:
            click_state = "TRUE"
        else:
            click_state = "FALSE"
            
        # 发布按压状态到 click 话题
        click_msg = String()
        click_msg.data = click_state
        self.click_pub.publish(click_msg)
        self.get_logger().debug(f"发布 click 状态: {click_state}")

def main(args=None):
    rclpy.init(args=args)
    node = ForceDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Force Detector 退出")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
