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

# ----- Configuration -----
MQTT_SERVER = "192.168.1.100"      # Replace with your MQTT broker address
MQTT_PORT = 1883
MQTT_DATA_TOPIC = "sensors/raspi/data"
MQTT_CONFIG_TOPIC = "devices/raspi/config"

# Operational parameters
TEMP_THRESHOLD = 28.0            # Temperature threshold in Celsius
UPDATE_INTERVAL = 6              # Update interval in seconds

# Device configuration (simulate persistent storage values)
device_id = "RaspiDevice"
fireFunctionA = True             # Flag to control the fan
fireFunctionB = True             # Flag to control the LED

# Global flag for graceful shutdown
running = True

# ----- Logging Configuration -----
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# ----- Signal Handler for Graceful Shutdown -----
def signal_handler(sig, frame):
    global running
    logging.info("Termination signal received. Shutting down...")
    running = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ----- MQTT Callback Functions -----
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
        # Process configuration updates if message received on config topic
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
            logging.info("Updated TEMP_THRESHOLD: %f", TEMP_THRESHOLD)
        if "update_interval" in config:
            UPDATE_INTERVAL = int(config["update_interval"])
            logging.info("Updated UPDATE_INTERVAL: %d", UPDATE_INTERVAL)
        if "fireFunctionA" in config:
            fireFunctionA = bool(config["fireFunctionA"])
            logging.info("Updated fireFunctionA: %s", fireFunctionA)
        if "fireFunctionB" in config:
            fireFunctionB = bool(config["fireFunctionB"])
            logging.info("Updated fireFunctionB: %s", fireFunctionB)
    except Exception as e:
        logging.error("Error updating configuration: %s", e)

def connect_mqtt(client):
    while not client.is_connected():
        try:
            client_id = f"{device_id}_{random.randint(0, 1000)}"
            client.connect(MQTT_SERVER, MQTT_PORT, 60)
            logging.info("Attempting MQTT connection with client id: %s", client_id)
            break
        except Exception as e:
            logging.error("MQTT connection failed: %s. Retrying in 2 seconds...", e)
            time.sleep(2)

# ----- Sensor Reading Function -----
def read_temperature():
    """
    Read the temperature from a sensor.
    This function currently simulates a temperature reading.
    Replace with actual sensor code.
    """
    return random.uniform(20.0, 35.0)

# ----- MQTT Data Publishing Function -----
def publish_data(client, temperature):
    payload = {
        "device_id": device_id,
        "temperature": round(temperature, 2),
        "timestamp": int(time.time() * 1000)
    }
    try:
        result = client.publish(MQTT_DATA_TOPIC, json.dumps(payload))
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logging.info("Published data: %s", json.dumps(payload))
        else:
            logging.error("Failed to publish MQTT message, result code: %s", result.rc)
    except Exception as e:
        logging.error("Error publishing MQTT message: %s", e)

# ----- Device Logic Function -----
def device_logic():
    try:
        temperature = read_temperature()
        logging.info("Current Temperature: %.2f°C", temperature)
        # Control the fan based on temperature threshold
        if temperature >= TEMP_THRESHOLD and fireFunctionA:
            control_fan(True)
        else:
            control_fan(False)
        # Control the LED based on temperature threshold
        if temperature >= TEMP_THRESHOLD and fireFunctionB:
            control_led(True)
        else:
            control_led(False)
        return temperature
    except Exception as e:
        logging.error("Error in device logic: %s", e)
        return None

# ----- Main Execution -----
def main():
    global running
    # Setup GPIO for fan and LED
    setup_fan()
    setup_led()

    # Initialize MQTT client
    client = mqtt.Client(f"{device_id}_{random.randint(0, 1000)}")
    client.on_connect = on_connect
    client.on_message = on_message
    connect_mqtt(client)
    client.loop_start()

    last_publish_time = time.time()

    try:
        while running:
            temperature = device_logic()
            current_time = time.time()
            if (current_time - last_publish_time) >= UPDATE_INTERVAL:
                if temperature is not None:
                    publish_data(client, temperature)
                last_publish_time = current_time
            time.sleep(1)
    except Exception as e:
        logging.error("Error in main loop: %s", e)
    finally:
        client.loop_stop()
        client.disconnect()
        GPIO.cleanup()
        logging.info("Program terminated gracefully.")

if __name__ == '__main__':
    main()
