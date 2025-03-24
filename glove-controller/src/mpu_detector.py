#!/usr/bin/env python3
"""
Simplified Motion Detector for MPU9250
- Stable visualization approach
- Detection of lift, drop, and stationary states
- English UI with Chinese comments
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
import time
from collections import deque
import matplotlib.pyplot as plt
import numpy as np
import threading

class MotionDetector(Node):
    def __init__(self):
        super().__init__('motion_detector')
        
        # Motion detection parameters (动作检测参数)
        self.LIFT_THRESHOLD = 1.2     # Lift threshold: >1.2g (抬起阈值)
        self.DROP_THRESHOLD = 0.8     # Drop threshold: <0.8g (降下阈值)
        self.MOTION_DURATION = 0.3    # Motion duration threshold in seconds (动作持续时间阈值)
        self.COOLDOWN_TIME = 0.5      # Cooldown time between detections (两次检测之间的冷却时间)
        
        # Buffer for storing data for detection (用于检测的数据缓冲区)
        self.window_size = 10
        self.accel_z_buffer = deque(maxlen=self.window_size)
        
        # Buffer for visualization (用于可视化的数据缓冲区)
        self.data_length = 200
        self.time_buffer = deque(maxlen=self.data_length)
        self.accel_x_buffer = deque(maxlen=self.data_length)
        self.accel_y_buffer = deque(maxlen=self.data_length)
        self.accel_z_buffer_vis = deque(maxlen=self.data_length)
        
        # Motion detection state (动作检测状态)
        self.last_detection_time = time.time()
        self.motion_start_time = 0
        self.is_lifting = False
        self.is_dropping = False
        self.is_stationary = True
        self.motion_in_progress = False
        
        # Current motion state for display (当前动作状态，用于显示)
        self.current_state = "STATIONARY"  # Can be "UP", "DOWN", or "STATIONARY"
        
        # Create subscriber (创建订阅者)
        self.subscription = self.create_subscription(
            String,
            'imu/all_data',
            self.data_callback,
            10)
        
        # Create publisher for detection results (创建发布者用于发布检测结果)
        self.motion_pub = self.create_publisher(
            String,
            'motion/detection',
            10)
        
        # Create mutex for thread synchronization (创建互斥锁用于线程同步)
        self.data_lock = threading.Lock()
        
        # Create event loop timer for updating data processing (创建事件循环定时器用于更新数据处理)
        self.timer = self.create_timer(0.05, self.timer_callback)
        
        self.get_logger().info('Motion detector initialized')
    
    def data_callback(self, msg):
        """Process received IMU data (处理接收到的IMU数据)"""
        try:
            data = json.loads(msg.data)
            
            # Get acceleration data (获取加速度数据)
            accel_x = data['accel']['x']
            accel_y = data['accel']['y']
            accel_z = data['accel']['z']
            timestamp = data['timestamp']
            
            # Update data buffers (更新数据缓冲区)
            with self.data_lock:
                self.accel_z_buffer.append(accel_z)
                
                # Update visualization data (更新可视化数据)
                self.time_buffer.append(timestamp)
                self.accel_x_buffer.append(accel_x)
                self.accel_y_buffer.append(accel_y)
                self.accel_z_buffer_vis.append(accel_z)
        
        except Exception as e:
            self.get_logger().error(f'Processing data failed: {e}')
    
    def timer_callback(self):
        """Periodically process and detect motions (定期处理和检测动作)"""
        # Detect motion (检测动作)
        motion = self.detect_motion()
        if motion:
            # Publish detection result (发布检测结果)
            result_msg = String()
            result_msg.data = motion
            self.motion_pub.publish(result_msg)
            self.get_logger().info(f'Detected motion: {motion}')
            
            # Update current state for display (更新当前状态用于显示)
            if motion == "LIFT_START" or motion == "LIFT_COMPLETE":
                self.current_state = "UP"
            elif motion == "DROP_START" or motion == "DROP_COMPLETE":
                self.current_state = "DOWN"
            elif motion == "STATIONARY":
                self.current_state = "STATIONARY"
        
        # Check for stationary state explicitly (明确检查静止状态)
        if not self.is_lifting and not self.is_dropping and not self.motion_in_progress:
            if len(self.accel_z_buffer) >= self.window_size:
                avg_accel_z = sum(self.accel_z_buffer) / len(self.accel_z_buffer)
                if self.DROP_THRESHOLD < avg_accel_z < self.LIFT_THRESHOLD:
                    if not self.is_stationary:
                        self.is_stationary = True
                        self.current_state = "STATIONARY"
                        self.motion_pub.publish(String(data="STATIONARY"))
                        self.get_logger().info("Motion state: STATIONARY")
    
    def detect_motion(self):
        """Detect lift and drop motions (检测抬起和降下动作)"""
        current_time = time.time()
        
        # If not enough data points or in cooldown period, don't detect (如果数据点不足或在冷却期内，则不检测)
        if len(self.accel_z_buffer) < self.window_size or \
           current_time - self.last_detection_time < self.COOLDOWN_TIME:
            return None
        
        # Use average to smooth noise (使用平均值来平滑噪声)
        avg_accel_z = sum(self.accel_z_buffer) / len(self.accel_z_buffer)
        
        # Motion detection logic (动作检测逻辑)
        if not self.motion_in_progress:
            # Detect motion start (检测动作开始)
            if avg_accel_z > self.LIFT_THRESHOLD and not self.is_lifting:
                self.is_lifting = True
                self.is_stationary = False
                self.motion_start_time = current_time
                self.motion_in_progress = True
                self.get_logger().info("Lift motion started")
                return "LIFT_START"
            elif avg_accel_z < self.DROP_THRESHOLD and not self.is_dropping:
                self.is_dropping = True
                self.is_stationary = False
                self.motion_start_time = current_time
                self.motion_in_progress = True
                self.get_logger().info("Drop motion started")
                return "DROP_START"
        else:
            # Detect if motion is complete - when acceleration returns to normal range
            # (检测动作是否完成 - 当加速度恢复到正常范围时)
            if self.DROP_THRESHOLD < avg_accel_z < self.LIFT_THRESHOLD:
                motion_duration = current_time - self.motion_start_time
                if motion_duration > self.MOTION_DURATION:
                    if self.is_lifting:
                        self.get_logger().info(f"Complete lift motion detected! Duration: {motion_duration:.2f}s")
                        self.is_lifting = False
                        self.last_detection_time = current_time
                        self.motion_in_progress = False
                        return "LIFT_COMPLETE"
                    elif self.is_dropping:
                        self.get_logger().info(f"Complete drop motion detected! Duration: {motion_duration:.2f}s")
                        self.is_dropping = False
                        self.last_detection_time = current_time
                        self.motion_in_progress = False
                        return "DROP_COMPLETE"
        
        return None
    
    def get_visualization_data(self):
        """Get copy of visualization data (获取可视化数据的副本)"""
        with self.data_lock:
            if not self.time_buffer:
                return None
            
            # Calculate relative times (first data point as 0) (计算相对时间，以第一个数据点为0)
            times = list(self.time_buffer)
            relative_times = [(t - times[0]) for t in times]
            
            return {
                'times': relative_times,
                'accel_x': list(self.accel_x_buffer),
                'accel_y': list(self.accel_y_buffer),
                'accel_z': list(self.accel_z_buffer_vis),
                'state': self.current_state
            }

def update_plot(detector, fig, ax, lines, motion_text, status_text):
    """Update plot with latest data (使用最新数据更新图表)"""
    data = detector.get_visualization_data()
    if data is None:
        return
    
    # Update line data (更新线条数据)
    lines[0].set_data(data['times'], data['accel_x'])
    lines[1].set_data(data['times'], data['accel_y'])
    lines[2].set_data(data['times'], data['accel_z'])
    
    # Update x-axis range (更新x轴范围)
    if data['times']:
        ax.set_xlim(max(0, data['times'][-1] - 5), data['times'][-1] + 0.5)
    
    # Update status text (更新状态文本)
    status = "Motion status: "
    if detector.is_lifting:
        status += "Lifting"
    elif detector.is_dropping:
        status += "Dropping"
    else:
        status += "Stationary"
    status_text.set_text(status)
    
    # Update motion state display (更新动作状态显示)
    motion_text.set_text(data['state'])
    
    # Change text color based on state (根据状态更改文本颜色)
    if data['state'] == "UP":
        motion_text.set_color('red')
    elif data['state'] == "DOWN":
        motion_text.set_color('blue')
    else:  # STATIONARY
        motion_text.set_color('green')
    
    # Draw plot (绘制图表)
    fig.canvas.draw_idle()
    plt.pause(0.01)

def main(args=None):
    rclpy.init(args=args)
    
    # Create the detector node
    detector = MotionDetector()
    
    # Setup thread for ROS2 processing
    ros_thread = threading.Thread(target=lambda: rclpy.spin(detector))
    ros_thread.daemon = True
    ros_thread.start()
    
    # Setup plot in the main thread
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_title('MPU9250 Acceleration Data and Motion Detection')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Acceleration (g)')
    ax.grid(True)
    
    # Create line objects (创建线条对象)
    line_x, = ax.plot([], [], 'r-', label='X-axis')
    line_y, = ax.plot([], [], 'g-', label='Y-axis')
    line_z, = ax.plot([], [], 'b-', label='Z-axis')
    lines = [line_x, line_y, line_z]
    
    # Add threshold lines (添加阈值线)
    ax.axhline(y=detector.LIFT_THRESHOLD, color='m', linestyle='--', label='Lift Threshold')
    ax.axhline(y=detector.DROP_THRESHOLD, color='c', linestyle='--', label='Drop Threshold')
    
    # Add legend (添加图例)
    ax.legend()
    
    # Set y-axis range (设置y轴范围)
    ax.set_ylim(-2, 2)
    
    # Initialize text annotation (初始化文本注释)
    status_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, 
                        bbox=dict(facecolor='white', alpha=0.5))
    
    # Add motion state display (添加动作状态显示)
    motion_text = ax.text(0.5, 0.5, 'STATIONARY', 
                        transform=ax.transAxes,
                        fontsize=20, ha='center', va='center',
                        bbox=dict(facecolor='white', alpha=0.7))
    
    try:
        plt.show(block=False)
        
        while plt.fignum_exists(fig.number):
            update_plot(detector, fig, ax, lines, motion_text, status_text)
            plt.pause(0.05)  # Small pause to allow GUI to update
            
    except KeyboardInterrupt:
        print("User interrupted, shutting down...")
    except Exception as e:
        print(f"Error in visualization: {e}")
    finally:
        plt.close(fig)
        detector.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()