#import network
import wireless
import time
import json
import random
import socket
#from umqtt.simple import MQTTClient
import paho.mqtt.client as mqtt

import os

SSID = "platform-wan"
PASSWORD = "platform-wan"
device_id = "MfQBgQwTjsWqJYC8jsNDwN"
mqtt_mdns_name = "platform-mmqtt.local"
mqtt_data_topic = "sensors/{}/data".format(device_id)
mqtt_config_topic = "devices/{}/config".format(device_id)

updateInterval = 6000
PREFS_FILE = "esp32-data.json"


def file_exists(filename):
    try:
        uos.stat(filename)
        return True
    except OSError:
        return False


def load_preferences():
    global updateInterval
    if file_exists(PREFS_FILE):
        try:
            with open(PREFS_FILE, "r") as f:
                prefs = json.load(f)
                updateInterval = prefs.get("updateInterval", 6000)
                print(
                    "Configuration loaded successfully, updateInterval =",
                    updateInterval,
                )
        except Exception as e:
            print("Error loading configuration, using default value. Error:", e)
    else:
        print(
            "Configuration file not found, using default updateInterval =",
            updateInterval,
        )


def save_preferences():
    try:
        with open(PREFS_FILE, "w") as f:
            json.dump({"updateInterval": updateInterval}, f)
        print("Configuration saved successfully, updateInterval =", updateInterval)
    except Exception as e:
        print("Error saving configuration:", e)


def connect_wifi():
    w= wireless.Wireless()
    w.connect(ssid=SSID, password= PASSWORD)
    


def resolve_broker(hostname):
    """
    Resolve the MQTT broker IP using the given hostname.
    This uses socket.getaddrinfo to perform a DNS lookup.
    """
    try:
        addr_info = socket.getaddrinfo(hostname, 1883)
        # Get the first returned IP address
        ip = addr_info[0][4][0]
        print("MQTT broker IP resolved via DNS/mDNS:", ip)
        return ip
    except Exception as e:
        fallback_ip = "192.168.0.18"
        print(
            "Failed to resolve MQTT broker hostname, using fallback IP:",
            fallback_ip,
            "Error:",
            e,
        )
        return fallback_ip


def sub_cb(topic, msg):
    global updateInterval
    try:
        topic_str = topic.decode() if isinstance(topic, bytes) else topic
        msg_str = msg.decode() if isinstance(msg, bytes) else msg
        print("Received message on topic:", topic_str)
        print("Message:", msg_str)
        if topic_str == mqtt_config_topic:
            config = json.loads(msg_str)
            if "data" in config:
                data_obj = config["data"]
                for key in data_obj:
                    if key.lower() == "updateinterval":
                        newInterval = int(data_obj[key])
                        if newInterval >= 1000:
                            updateInterval = newInterval
                            save_preferences()
                            print("Updated data publish interval to:", updateInterval)
                        else:
                            print("Ignoring updateInterval < 1000 ms")
                        break
    except Exception as e:
        print("Error processing message:", e)


def publish_data(client):
    generatedNumber = random.randint(0, 999)
    payload = {
        "device_id": device_id,
        "timestamp": int(time.time() * 1000),
        "data": {"generatedNumber": generatedNumber, "testBool": True},
    }
    payload_str = json.dumps(payload)
    ret = client.publish(mqtt_data_topic, payload_str)
    if ret == 0:
        print("Data published:", payload_str)
    else:
        print("Data publish failed, error code:", ret)


def main():
    global updateInterval
    load_preferences()
    wlan = connect_wifi()
    broker_ip = resolve_broker(mqtt_mdns_name)
    client = MQTTClient(client_id=device_id + "_client", server=broker_ip, keepalive=60)
    client.set_callback(sub_cb)
    while True:
        try:
            print("Attempting to connect to MQTT broker at", broker_ip)
            client.connect()
            break
        except Exception as e:
            print("MQTT connection error:", e)
            time.sleep(2)

    client.subscribe(mqtt_data_topic)
    client.subscribe(mqtt_config_topic)
    print("Subscribed to topics:", mqtt_data_topic, "and", mqtt_config_topic)

    last_publish_time = time.ticks_ms()

    try:
        while True:
            client.check_msg()
            current_time = time.ticks_ms()
            if time.ticks_diff(current_time, last_publish_time) >= updateInterval:
                last_publish_time = current_time
                publish_data(client)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting program...")
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
