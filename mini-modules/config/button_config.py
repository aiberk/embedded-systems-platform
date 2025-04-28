device_id = "jLDT3JpuGeC6Ard52HYkHN"
mqtt_mdns_name = "platform.local"
mqtt_button_data_topic = f"sensors/{device_id}/data"
mqtt_button_config_topic = f"devices/{device_id}/config"

config = {
    "device_id": device_id,
    "mqtt_mdns_name": mqtt_mdns_name,
    "subscriptions": [mqtt_button_config_topic],
    "data_topic": mqtt_button_data_topic
}
