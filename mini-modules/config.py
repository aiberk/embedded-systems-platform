import json
import os

PREFS_FILE = "esp32-data.json"
device_id = "jLDT3JpuGeC6Ard52HYkHN"
fan_device_id = "G4VtMWbGUnpB2K2sR5bpf9"
mqtt_mdns_name = "platform.local"

mqtt_data_topic = f"sensors/{device_id}/data"
mqtt_config_topic = f"devices/{device_id}/config"
mqtt_fan_topic = f"devices/{fan_device_id}/fan"

default_ping = "false"
ping = default_ping

def load_preferences():
    global ping
    if os.path.exists(PREFS_FILE):
        try:
            with open(PREFS_FILE, "r") as f:
                prefs = json.load(f)
                ping = prefs.get("ping", default_ping)
                print("Config loaded, ping =", ping)
        except Exception as e:
            print("Failed to load config:", e)

def save_preferences(ping):
    try:
        with open(PREFS_FILE, "w") as f:
            json.dump({"ping": ping}, f)
        print("Config saved, ping =", ping)
    except Exception as e:
        print("Failed to save config:", e)
