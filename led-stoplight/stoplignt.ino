#include <WiFi.h>
#include <ESPmDNS.h>
#include <PubSubClient.h>
#include <Preferences.h>
#include <ArduinoJson.h>

const char* ssid = "platform-wan";
const char* password = "platform-wan";

const char* device_id = "me9iefnXM6UBKwxtENd4pD";
String mqtt_config_topic = String("devices/") + device_id + "/config";

const int redPin = 21;
const int yellowPin = 22;
const int greenPin = 23;

WiFiClient espClient;
PubSubClient client(espClient);
Preferences preferences;
volatile int updateInterval = 6000;

void setLights(String pattern) {
  if (pattern.length() != 3) {
    return;
  }
  digitalWrite(redPin, (pattern.charAt(0) == '1') ? HIGH : LOW);
  digitalWrite(yellowPin, (pattern.charAt(1) == '1') ? HIGH : LOW);
  digitalWrite(greenPin, (pattern.charAt(2) == '1') ? HIGH : LOW);
}

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
      if (data.containsKey("lightPattern")) {
        String pattern = data["lightPattern"].as<String>();
        setLights(pattern);
      }
      if (data.containsKey("updateInterval")) {
        int newInterval = data["updateInterval"];
        if (newInterval >= 1000) {
          updateInterval = newInterval;
          preferences.begin("esp32-data", false);
          preferences.putInt("updateInterval", updateInterval);
          preferences.end();
        }
      }
    }
  }
}

void setup_wifi() {
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
  MDNS.begin("esp32");
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
      client.subscribe(mqtt_config_topic.c_str());
    } else {
      delay(2000);
    }
  }
}

void setup() {
  pinMode(redPin, OUTPUT);
  pinMode(yellowPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  setup_wifi();
  client.setCallback(callback);
  reconnect_mqtt();
  preferences.begin("esp32-data", false);
  updateInterval = preferences.getInt("updateInterval", 6000);
  preferences.end();
}

void loop() {
  if (!client.connected()) {
    reconnect_mqtt();
  }
  client.loop();
}
