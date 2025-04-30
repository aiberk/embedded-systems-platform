import json
import paho.mqtt.client as mqtt
from core.broker import resolve_broker

class MQTTDeviceClient:
    def __init__(self, config, message_handler):
        self.config = config
        self.message_handler = message_handler
        self.client = mqtt.Client(client_id=f"{config['device_id']}_client")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            client.subscribe(self.config["data_topic"])
            print(f"[{self.config['device_id']}] Connected to broker")
            for topic in self.config["subscriptions"]:
                client.subscribe(topic)
                print(f"Subscribed to {topic}")
        else:
            print("MQTT connect failed:", rc)

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            self.message_handler(msg.topic, payload, self)
        except Exception as e:
            print("Error in on_message:", e)

    def publish(self, topic, payload):
        result = self.client.publish(topic, json.dumps(payload))
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            print("Failed to publish:", result.rc)

    def start(self):
        broker_ip = resolve_broker(self.config["mqtt_mdns_name"])
        self.client.connect(broker_ip, 1883, 60)
        self.client.loop_start()
