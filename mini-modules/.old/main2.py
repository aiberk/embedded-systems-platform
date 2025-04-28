import time
import json
import random
import logging
import signal
import sys
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

from temperature.fan_control import setup_fan, control_fan
from temperature.led_control import setup_led, control_led

from sensors.temperature import read_temperature
from sensors.humidity import read_humidity
from sensors.light import read_light
from sensors.pressure import read_pressure

device_id = "RaspiDevice"
TEMP_THRESHOLD = 28.0
UPDATE_INTERVAL = 6
fireFunctionA = True
fireFunctionB = True
running = True

MQTT_SERVER = "127.0.0.1"
MQTT_PORT = 1883
MQTT_DATA_TOPIC = "sensors/raspi/data"
MQTT_CONFIG_TOPIC = "devices/raspi/config"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def signal_handler(sig, frame):
    global running
    logging.info("Termination signal received. Shutting down...")
    running = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT Broker!")
        client.subscribe(MQTT_CONFIG_TOPIC)
    else:
        logging.error("Failed to connect to MQTT Broker, return code %d", rc)

def on_message(client, userdata, msg):
    try:
        message = msg.payload.decode("utf-8")
        logging.info("Received message on %s: %s", msg.topic, message)
        if msg.topic == MQTT_CONFIG_TOPIC:
            config = json.loads(message)
            update_configuration(config)
    except Exception as e:
        logging.error("Error processing MQTT message: %s", e)

def update_configuration(config):
    global TEMP_THRESHOLD, UPDATE_INTERVAL, fireFunctionA, fireFunctionB
    try:
        if "temp_threshold" in config:
            TEMP_THRESHOLD = float(config["temp_threshold"])
        if "update_interval" in config:
            UPDATE_INTERVAL = int(config["update_interval"])
        if "fireFunctionA" in config:
            fireFunctionA = bool(config["fireFunctionA"])
        if "fireFunctionB" in config:
            fireFunctionB = bool(config["fireFunctionB"])
        logging.info("Configuration updated.")
    except Exception as e:
        logging.error("Error updating configuration: %s", e)

def connect_mqtt(client):
    while not client.is_connected() and running:
        try:
            client_id = f"{device_id}_{random.randint(0, 1000)}"
            client.connect(MQTT_SERVER, MQTT_PORT, 60)
            logging.info("Attempting MQTT connection with client id: %s", client_id)
            break
        except Exception as e:
            logging.error("MQTT connection failed: %s. Retrying in 2 seconds...", e)
            time.sleep(2)

def publish_data(client, readings):
    payload = {
        "device_id": device_id,
        "data": readings,
        "timestamp": int(time.time() * 1000),
    }
    try:
        result = client.publish(MQTT_DATA_TOPIC, json.dumps(payload))
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logging.info("Published data: %s", json.dumps(payload))
        else:
            logging.error("Failed to publish MQTT message, result code: %s", result.rc)
    except Exception as e:
        logging.error("Error publishing MQTT message: %s", e)

def device_logic():
    try:
        temperature = read_temperature()
        humidity = read_humidity()
        light = read_light()
        pressure = read_pressure()

        if temperature is not None:
            if temperature >= TEMP_THRESHOLD and fireFunctionA:
                control_fan(True)
            else:
                control_fan(False)
            if temperature >= TEMP_THRESHOLD and fireFunctionB:
                control_led(True)
            else:
                control_led(False)

        readings = {
            "temperature": temperature,
            "humidity": humidity,
            "light": light,
            "pressure": pressure,
        }

        logging.info(f"Sensor Readings: {readings}")
        return readings
    except Exception as e:
        logging.error("Error in device logic: %s", e)
        return {}

def main():
    global running
    setup_fan()
    setup_led()

    client = mqtt.Client(
        client_id=f"{device_id}_{random.randint(0, 1000)}",
        clean_session=True,
        callback_api_version=mqtt.CallbackAPIVersion(1),
    )
    client.on_connect = on_connect
    client.on_message = on_message
    connect_mqtt(client)
    client.loop_start()

    last_publish_time = time.time()

    try:
        while running:
            readings = device_logic()
            current_time = time.time()
            if (current_time - last_publish_time) >= UPDATE_INTERVAL:
                publish_data(client, readings)
                last_publish_time = current_time
            time.sleep(1)
    except Exception as e:
        logging.error("Error in main loop: %s", e)
    finally:
        client.loop_stop()
        client.disconnect()
        GPIO.cleanup()
        logging.info("Program terminated gracefully.")

if __name__ == "__main__":
    main()
