device_id = "NVwiLtkYt8EDjWESoBohM3"
mqtt_mdns_name = "platform.local"
mqtt_buzzor_data_topic = f"sensors/{device_id}/data"
mqtt_buzzor_config_topic = f"devices/{device_id}/config"

config = {
    "device_id": device_id,
    "mqtt_mdns_name": mqtt_mdns_name,
    "subscriptions": [mqtt_buzzor_config_topic, mqtt_buzzor_data_topic],
    "data_topic": mqtt_buzzor_data_topic
}
