device_id = "G4VtMWbGUnpB2K2sR5bpf9"
mqtt_mdns_name = "platform.local"
mqtt_fan_data_topic = f"devices/{device_id}/data"
mqtt_fan_config_topic = f"sensors/{device_id}/config"

config = {
    "device_id": device_id,
    "mqtt_mdns_name": mqtt_mdns_name,
    "subscriptions": [mqtt_fan_data_topic],
    "data_topic": mqtt_fan_config_topic
}
