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
  Serial.print("📩 Received message on topic: ");
  Serial.println(topic);
  payload[length] = '\0';
  String message = String((char*)payload);
  Serial.print("📜 Message content: ");
  Serial.println(message);

  if (String(topic) == mqtt_config_topic) {
    Serial.println("🟡 Processing configuration update...");
    StaticJsonDocument<256> doc;
    DeserializationError error = deserializeJson(doc, message);
    if (error) {
      Serial.println("❌ JSON parsing failed!");
      return;
    }

    Serial.println("✅ JSON parsed successfully!");
    if (doc.containsKey("data")) {
      JsonObject data = doc["data"].as<JsonObject>();
      if (data.containsKey("updateInterval")) {
        int newInterval = data["updateInterval"];
        if (newInterval >= 1000) {
          updateInterval = newInterval;
          Serial.print("🔄 Updated updateInterval (from data): ");
          Serial.println(updateInterval);
        } else {
          Serial.println("❌ Ignoring updateInterval < 1000ms (too fast!)");
        }
      } 
    } else {
      Serial.println("❌ No 'data' field found in configuration update.");
    }

    preferences.begin("esp32-data", false);
    preferences.putInt("updateInterval", updateInterval);
    preferences.end();
    Serial.println("💾 Saved configuration to NVS!");
    Serial.println("✅ Configuration updated from MQTT!");
  }
}


void setup_wifi() {
  Serial.print("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
  }
  Serial.println("\n✅ WiFi connected!");
  Serial.print("📶 ESP32 IP Address: ");
  Serial.println(WiFi.localIP());

  if (!MDNS.begin("esp32")) {
    Serial.println("❌ Error setting up MDNS responder!");
  } else {
    Serial.println("✅ MDNS responder started");
  }
}


void reconnect_mqtt() {
  int n = MDNS.queryService("_mqtt", "_tcp");
  if (n == 0) {
    Serial.println("❌ No mDNS services found for _mqtt._tcp");
    delay(2000);
    return;
  }
  
  String serviceHostname = MDNS.hostname(0);
  Serial.print("Service hostname from mDNS: ");
  Serial.println(serviceHostname);
  
  IPAddress mqttIP = MDNS.queryHost(serviceHostname.c_str(), 3000);
  if (mqttIP == INADDR_NONE || mqttIP == IPAddress(0, 0, 0, 0)) {
    Serial.println("❌ Failed to resolve MQTT Broker IP using queryHost");
    delay(2000);
    return;
  }
  
  Serial.print("Resolved MQTT Broker IP: ");
  Serial.println(mqttIP);
  client.setServer(mqttIP, 1883);
  while (!client.connected()) {
    Serial.print("🔄 Connecting to MQTT...");
    String clientId = String(device_id) + "_client";
    if (client.connect(clientId.c_str())) {
      Serial.println("✅ Connected to MQTT Broker");
      client.subscribe(mqtt_data_topic.c_str());
      client.subscribe(mqtt_config_topic.c_str());
    } else {
      Serial.print("❌ Failed, rc=");
      Serial.print(client.state());
      Serial.println(" Retrying in 2 seconds...");
      delay(2000);
    }
  }
}




void publishDataToMQTT() {
  int generatedNumber = random(0, 1000);
  StaticJsonDocument<256> doc;
  doc["device_id"] = device_id;
  doc["timestamp"] = millis();
  JsonObject data = doc.createNestedObject("data");
  data["generatedNumber"] = generatedNumber;
  data["testBool"] = true;

  String payload;
  serializeJson(doc, payload);
  Serial.print("📤 Publishing message: ");
  Serial.println(payload);
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

  Serial.println("📦 Loaded Config from NVS:");
  Serial.print("   - Update Interval: ");
  Serial.println(updateInterval);
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
