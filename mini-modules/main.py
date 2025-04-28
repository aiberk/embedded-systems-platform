from core.mqtt_client import MQTTDeviceClient
from devices.fan_device import handle_message as fan_handler
from devices.button_device import handle_message as button_handler, setup as setup_button, handle_button_press
from config.fan_config import config as fan_config
from config.button_config import config as button_config

fan_client = MQTTDeviceClient(fan_config, fan_handler)
button_client = MQTTDeviceClient(button_config, button_handler)

def main():
    fan_client.start()
    button_client.start()
    setup_button(lambda: handle_button_press(button_client.publish, button_config))

    import time
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
