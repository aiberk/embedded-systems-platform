import json
import socket
import time
import paho.mqtt.client as mqtt
from config import *
from hardware import control_fan

client = None

def resolve_broker():
    try:
        ip = socket.gethostbyname(mqtt_mdns_name)
        print("Broker resolved via mDNS:", ip)
        return ip
    except:
        fallback_ip = "192.168.1.100"
        print("Using fallback broker IP:", fallback_ip)
        return fallback_ip

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe(mqtt_data_topic)
        client.subscribe(mqtt_config_topic)
        client.subscribe(mqtt_fan_topic)
    else:
        print("MQTT connection failed with code:", rc)

def on_message(client, userdata, msg):
    global ping
    try:
        payload = json.loads(msg.payload.decode())
        print(f"Message on {msg.topic}: {payload}")
        if msg.topic == mqtt_config_topic:
            data = payload.get("data", {})
            newping = data.get("ping", "true")
            ping = newping
            save_preferences(ping)
            print("Ping updated:", ping)

            publish_data({
                "device_id": device_id,
                "timestamp": int(time.time() * 1000),
                "data": {
                    "ping": False,
                },
            })
        elif msg.topic == mqtt_fan_topic:
            if msg.payload:
                try:
                    fan_state = json.loads(msg.payload.decode())
                    if isinstance(fan_state, dict) and "fan" in fan_state:
                        control_fan(fan_state["fan"])
                        print(f"Fan {'ON' if fan_state['fan'] else 'OFF'}")
                except Exception as e:
                    print("Failed to decode fan message: ", e)
    except Exception as e:
        print("Error in on_message:", e)

def publish_data(payload):
    payload_str = json.dumps(payload)
    result = client.publish(mqtt_data_topic, payload_str)
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print("Published:", payload_str)
    else:
        print("Failed to publish, code:", result.rc)

def setup_client():
    global client
    broker = resolve_broker()
    client = mqtt.Client(client_id=f"{device_id}_client")
    client.on_connect = on_connect
    client.on_message = on_message

    while True:
        try:
            client.connect(broker, 1883, 60)
            break
        except Exception as e:
            print("Connection retrying:", e)
            time.sleep(2)

    client.loop_start()
