from core.mqtt_client import MQTTDeviceClient
from devices.fan_device import handle_message as fan_handler
from devices.button_device import handle_message as button_handler, setup as setup_button, handle_button_press
from devices.lcd_device import handle_message as lcd_handler, setup as setup_lcd
from devices.buzzer_device import handle_message as buzzer_handler, setup as setup_buzzer
from config.fan_config import config as fan_config
from config.button_config import config as button_config
from config.lcd_config import config as lcd_config
from config.buzzer_config import config as buzzer_config

fan_client = MQTTDeviceClient(fan_config, fan_handler)
button_client = MQTTDeviceClient(button_config, button_handler)
lcd_client = MQTTDeviceClient(lcd_config, lcd_handler)
buzzer_client = MQTTDeviceClient(buzzer_config, buzzer_handler)

def main():
    fan_client.start()
    button_client.start()
    lcd_client.start()
    buzzer_client.start()
    setup_button(lambda: handle_button_press(button_client.publish, button_config))
    setup_lcd()
    setup_buzzer()

    import time
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
