from hardware.gpio import fan

def control_fan(state):
    if state:
        fan.on()
        print("Fan ON")
    else:
        fan.off()
        print("Fan OFF")

def handle_message(topic, payload, mqtt_client):
    if "fan" in payload:
        control_fan(payload["fan"])
        mqtt_client.publish(mqtt_client.config["data_topic"], {
            "device_id": mqtt_client.config["device_id"],
            "timestamp": int(__import__('time').time() * 1000),
            "data": {"fan": payload["fan"]}
        })
