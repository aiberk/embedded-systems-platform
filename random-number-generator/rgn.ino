#include <WiFi.h>
#include <ESPmDNS.h>
#include <Preferences.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

const char* ssid = "platform-wan";
const char* password = "platform-wan";
const char* device_id = "zhbwscBXHUF9QnZKzFdRDd";
const char* mqtt_mdns_name = "platform-mmqtt.local";

String mqtt_data_topic = String("sensors/") + device_id + "/data";
String mqtt_config_topic = String("devices/") + device_id + "/config";
WiFiClient espClient;
PubSubClient client(espClient);
Preferences preferences;

volatile int updateInterval = 6000;
int generatedNumber = 0;

void callback(char* topic, byte* payload, unsigned int length) {
  payload[length] = '\0';
  String message = String((char*)payload);

  if (String(topic) == mqtt_config_topic) {
    StaticJsonDocument<256> doc;
    DeserializationError error = deserializeJson(doc, message);
    if (error) {
      return;
    }

    if (doc.containsKey("data")) {
      JsonObject data = doc["data"].as<JsonObject>();
      if (data.containsKey("updateInterval")) {
        int newInterval = data["updateInterval"];
        if (newInterval >= 1000) {
          updateInterval = newInterval;
        }
      }
    }

    preferences.begin("esp32-data", false);
    preferences.putInt("updateInterval", updateInterval);
    preferences.end();
  }
}

void setup_wifi() {
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }

  if (!MDNS.begin("esp32")) {
    return;
  }
}

void reconnect_mqtt() {
  int n = MDNS.queryService("_mqtt", "_tcp");
  if (n == 0) {
    delay(2000);
    return;
  }

  String serviceHostname = MDNS.hostname(0);

  IPAddress mqttIP = MDNS.queryHost(serviceHostname.c_str(), 3000);
  if (mqttIP == INADDR_NONE || mqttIP == IPAddress(0, 0, 0, 0)) {
    delay(2000);
    return;
  }

  client.setServer(mqttIP, 1883);
  while (!client.connected()) {
    String clientId = String(device_id) + "_client";
    if (client.connect(clientId.c_str())) {
      client.subscribe(mqtt_data_topic.c_str());
      client.subscribe(mqtt_config_topic.c_str());
    } else {
      delay(2000);
    }
  }
}

void publishDataToMQTT() {
  generatedNumber = random(0, 1000);
  StaticJsonDocument<256> doc;
  doc["device_id"] = device_id;
  doc["timestamp"] = millis();
  JsonObject data = doc.createNestedObject("data");
  data["generatedNumber"] = generatedNumber;
  data["testBool"] = true;

  String payload;
  serializeJson(doc, payload);
  client.publish(mqtt_data_topic.c_str(), payload.c_str());
}

void setup() {
  Serial.begin(115200);
  setup_wifi();

  client.setCallback(callback);

  reconnect_mqtt();

  preferences.begin("esp32-data", false);
  updateInterval = preferences.getInt("updateInterval", 6000);
  preferences.end();
}

unsigned long lastPublishTime = 0;

void loop() {
  if (!client.connected()) {
    reconnect_mqtt();
  }
  client.loop();

  unsigned long currentMillis = millis();
  if (currentMillis - lastPublishTime >= updateInterval) {
    lastPublishTime = currentMillis;
    publishDataToMQTT();
  }
}
