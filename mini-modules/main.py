from config import *
from mqtt_client import setup_client, publish_data
from hardware import setup_devices
from signal import pause
import time

def on_button_press():
    print("Button was pressed")
    payload = {
        "device_id": device_id,
        "timestamp": int(time.time() * 1000),
        "data": {
            "ping": False,
            "isClicked": True
        }
    }
    publish_data(payload)

def main():
    load_preferences()
    setup_client()
    setup_devices(on_button_press)
    print("Ready. Waiting for button press...")
    pause()  # Keeps the program running for GPIO callbacks

if __name__ == "__main__":
    main()
