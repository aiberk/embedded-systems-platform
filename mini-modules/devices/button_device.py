from time import time
from hardware.gpio import button

def setup(callback):
    button.when_pressed = lambda: callback()

def handle_button_press(publish, config):
    print("Button was pressed")
    payload = {
        "device_id": config['device_id'],
        "timestamp": int(time() * 1000),
        "data": {
            "ping": False,
            "isClicked": True
        }
    }
    publish(config["data_topic"], payload)

def handle_message(topic, payload, mqtt_client):
    # No incoming messages handled by button
    pass
