import time
import json
import random
import socket
import os
import paho.mqtt.client as mqtt
import camera_controller

# Configuration parameters
device_id = "ksyhwGSfpMJ2kqt5dB4ydH"
mqtt_mdns_name = "platform.local" # "192.168.0.104" # "platform-mmqtt.local"  # Attempt to resolve MQTT broker hostname via mDNS
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


def publish_data(client):
    generatedNumber = random.randint(0, 999)
    payload = {
        "device_id": device_id,
        "timestamp": int(time.time() * 1000),  # Millisecond timestamp
        "data": {
            "generatedNumber": generatedNumber,
            "testBool": True
        }
    }
    payload_str = json.dumps(payload)
    result = client.publish(mqtt_data_topic, payload_str)
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print("Data published:", payload_str)
    else:
        print("Data publish failed, error code:", result.rc)

def publish_emotion(client, emotion):
    payload = {
        "device_id": device_id,
        "timestamp": int(time.time() * 1000),  # Millisecond timestamp
        "data": {
            "emotion": emotion,
            "testBool": True
        }
    }
    payload_str = json.dumps(payload)
    result = client.publish(mqtt_data_topic, payload_str)
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print("Data published:", payload_str)
    else:
        print("Data publish failed, error code:", result.rc)


def main():
    emotion = camera_controller.detect_emotions('the_guys.jpg')[0]
    global updateInterval

    load_preferences()

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
    published = False
    try:
        while True:
            if not published:
                publish_emotion(client, emotion)
                published = True
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting program...")
    finally:
        client.loop_stop()
        client.disconnect()

    

if __name__ == "__main__":
    main()
