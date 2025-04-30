device_id = "C2Zj4UFsw2reqamFw9ZhFN"
mqtt_mdns_name = "platform.local"
mqtt_lcd_data_topic = f"sensors/{device_id}/data"
mqtt_lcd_config_topic = f"devices/{device_id}/config"

config = {
    "device_id": device_id,
    "mqtt_mdns_name": mqtt_mdns_name,
    "subscriptions": [mqtt_lcd_config_topic, mqtt_lcd_data_topic],
    "data_topic": mqtt_lcd_data_topic
}