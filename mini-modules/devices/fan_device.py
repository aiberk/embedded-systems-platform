from hardware.gpio import fan

def control_fan(state):
    if state == "true":
        fan.on()
        print("Fan ON")
    else:
        fan.off()
        print("Fan OFF")

def handle_message(topic, payload, mqtt_client):
    try:
        data = payload.get("data", {})
        if "fan" in data:
            control_fan(data["fan"])
    except Exception as e:
        print(f"[FAN] Error reading payload: {e}")
