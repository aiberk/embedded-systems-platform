#!/usr/bin/env python3
import time
import json
import random
import socket
import os
import threading
import paho.mqtt.client as mqtt

# -------------------------------
# New: Import ROS related modules for subscribing to ROS topics in MQTT scripts
import rclpy
from rclpy.node import Node
from std_msgs.msg import String as ROSString
# -------------------------------

# Configuration parameters
device_id = "zmpTGC3eGcrhixv8U7TRUJ"
mqtt_mdns_name = "192.168.0.18"  # "platform-mmqtt.local"  # Attempt to resolve MQTT broker hostname via mDNS
mqtt_data_topic = f"sensors/{device_id}/data"
mqtt_config_topic = f"devices/{device_id}/config"

# Default data publish interval (in milliseconds)
updateInterval = 6000

# File to store configuration (simulating Preferences)
PREFS_FILE = "esp32-data.json"


def load_preferences():
    global updateInterval
    if os.path.exists(PREFS_FILE):
        try:
            with open(PREFS_FILE, "r") as f:
                prefs = json.load(f)
                updateInterval = prefs.get("updateInterval", 6000)
                print("Configuration loaded successfully, updateInterval =", updateInterval)
        except Exception as e:
            print("Error loading configuration, using default value. Error:", e)
    else:
        print("Configuration file not found, using default updateInterval =", updateInterval)


def save_preferences():
    try:
        with open(PREFS_FILE, "w") as f:
            json.dump({"updateInterval": updateInterval}, f)
        print("Configuration saved successfully, updateInterval =", updateInterval)
    except Exception as e:
        print("Error saving configuration:", e)


def resolve_mqtt_broker():
    """
    Resolve MQTT broker IP by parsing mDNS hostname.
    If resolution fails, returns fallback IP (adjust as needed).
    """
    try:
        broker_ip = socket.gethostbyname(mqtt_mdns_name)
        print("MQTT broker IP resolved via mDNS:", broker_ip)
        return broker_ip
    except Exception as e:
        fallback_ip = "192.168.1.100"  # Please adjust the fallback IP as needed
        print("mDNS resolution failed, using fallback IP:", fallback_ip)
        return fallback_ip


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT connected successfully")
        client.subscribe(mqtt_data_topic)
        client.subscribe(mqtt_config_topic)
        print("Subscribed to topics:", mqtt_data_topic, "and", mqtt_config_topic)
    else:
        print("MQTT connection failed, error code:", rc)


def on_message(client, userdata, msg):
    global updateInterval
    try:
        topic = msg.topic
        payload = msg.payload.decode()
        print(f"Received message on topic {topic}: {payload}")
        # If it's a configuration update message
        if topic == mqtt_config_topic:
            config = json.loads(payload)
            # Check if JSON data contains data.updateInterval field
            if "data" in config and "updateInterval" in config["data"]:
                newInterval = int(config["data"]["updateInterval"])
                if newInterval >= 1000:
                    updateInterval = newInterval
                    save_preferences()
                    print("Updated data publish interval to:", updateInterval)
    except Exception as e:
        print("Error processing message:", e)


# -------------------------------
# New: Define a ROS subscription node to receive ROS messages published by the GUI
class GuiSubscriber(Node):
    def __init__(self):
        super().__init__('gui_subscriber')
        self.subscription = self.create_subscription(
            ROSString,
            'GUI',
            self.gui_callback,
            10
        )
        self.latest_gui_data = None  # store newest GUI data

    def gui_callback(self, msg: ROSString):
        try:
            data = json.loads(msg.data)  # Parsing JSON data posted by GUI
            self.latest_gui_data = data
            self.get_logger().info(f"Received GUI data: {data}")
        except Exception as e:
            self.get_logger().error("Error parsing GUI message: " + str(e))
# -------------------------------

# Modification: The original publish_data function adds the GUI data part.
# Here we extract the contents of the GUI data separately and display them independently as gui-click, gui-motion, gui-channel
def publish_data(client, gui_data):
    generatedNumber = random.randint(0, 999)
    # If there is GUI data, extract each field separately; otherwise use "error"
    if gui_data is not None:
        gui_click = gui_data.get("click", "error")
        gui_motion = gui_data.get("motion", "error")
        gui_channel = gui_data.get("channel", "error")
    else:
        gui_click = "error"
        gui_motion = "error"
        gui_channel = "error"
        
    # Construct a published message, including both random numbers and GUI data (displayed separately)
    payload = {
        "device_id": device_id,
        "timestamp": int(time.time() * 1000),  # Millisecond timestamp
        "data": {
            "generatedNumber": generatedNumber,
            "testBool": True,
            "gui-click": gui_click,       # NEW: GUI click status, "pressed", "not_pressed"
            "gui-motion": gui_motion,     # NEW: GUI motion status, "lifting", "dropping", "stationary"
            "gui-channel": gui_channel    # NEW: GUI channel status: "1", "2", "3"
        }
    }
    payload_str = json.dumps(payload)
    result = client.publish(mqtt_data_topic, payload_str)
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print("Data published:", payload_str)
    else:
        print("Data publish failed, error code:", result.rc)


def main():
    global updateInterval

    load_preferences()

    # -------------------------------
    # New: Initialize ROS and create a GUI subscription node to receive messages from the GUI on ROS
    rclpy.init()
    gui_subscriber = GuiSubscriber()
    ros_thread = threading.Thread(target=rclpy.spin, args=(gui_subscriber,), daemon=True)
    ros_thread.start()
    # -------------------------------

    # Resolve MQTT broker IP (if local system supports mDNS resolution, it will be used)
    broker_ip = resolve_mqtt_broker()

    # Create MQTT client and set callback functions
    client = mqtt.Client(client_id=f"{device_id}_client")
    client.on_connect = on_connect
    client.on_message = on_message

    # Attempt to connect to MQTT broker
    while True:
        try:
            print("Attempting to connect to MQTT broker...")
            client.connect(broker_ip, port=1883, keepalive=60)
            break
        except Exception as e:
            print("MQTT connection error:", e)
            time.sleep(2)

    # Start background thread for MQTT network loop
    client.loop_start()

    last_publish_time = time.time() * 1000  # 毫秒计时器
    try:
        while True:
            current_time = time.time() * 1000
            if current_time - last_publish_time >= updateInterval:
                last_publish_time = current_time
                # Modification: In each release cycle, take the latest GUI data and publish it together with the random number data
                publish_data(client, gui_subscriber.latest_gui_data)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting program...")
    finally:
        client.loop_stop()
        client.disconnect()
        # shutdown ROS node
        rclpy.shutdown()


if __name__ == "__main__":
    main()
