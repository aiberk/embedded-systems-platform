from grove.display.jhd1802 import JHD1802

lcd = JHD1802()

def setup():
    lcd.clear()
    lcd.setCursor(0, 0)
    lcd.write("LCD Ready...")
    lcd.setCursor(1, 0)
    lcd.write("Waiting...")

def handle_message(topic, payload, mqtt_client):
    """
    Handle incoming MQTT messages and display the emotion value.

    Expected payload format:
    {
        "device_id": "...",
        "timestamp": 1690000000,
        "data": {
            "emotion": "happy"
        }
    }
    """
    try:
        print(f"[LCD] Received payload: {payload}")
        emotion = payload.get("data", {}).get("emotion", "No emotion")

        lcd.clear()
        lcd.setCursor(0, 0)
        lcd.write("Emotion:")
        lcd.setCursor(1, 0)
        lcd.write(emotion[:16])
        print(f"[LCD] Displayed emotion: {emotion}")

    except Exception as e:
        print(f"[LCD] Error displaying emotion: {e}")
