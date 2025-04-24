import json
import os

PREFS_FILE = "esp32-data.json"
device_id = "jLDT3JpuGeC6Ard52HYkHN"
mqtt_mdns_name = "platform.local"

mqtt_data_topic = f"sensors/{device_id}/data"
mqtt_config_topic = f"devices/{device_id}/config"

default_ping = 6000
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

def save_preferences():
    try:
        with open(PREFS_FILE, "w") as f:
            json.dump({"ping": ping}, f)
        print("Config saved, ping =", ping)
    except Exception as e:
        print("Failed to save config:", e)
