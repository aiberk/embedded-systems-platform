#include <WiFi.h>
#include <ESPmDNS.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

const char* ssid = "platform-wan";
const char* password = "platform-wan";
const char* device_id = "tENd4pDme9M6t6KwxiefnX";
String mqtt_config_topic = String("devices/") + device_id + "/config";

WiFiClient espClient;
PubSubClient client(espClient);

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

void displayMessage(String msg) {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println(msg);
  display.display();
}

void callback(char* topic, byte* payload, unsigned int length) {
  payload[length] = '\0';
  String message = String((char*)payload);
  if (String(topic) == mqtt_config_topic) {
    StaticJsonDocument<256> doc;
    if (deserializeJson(doc, message))
      return;
    if (doc.containsKey("data")) {
      JsonObject data = doc["data"].as<JsonObject>();
      if (data.containsKey("massage")) {
        String msg = data["massage"].as<String>();
        displayMessage(msg);
      }
    }
  }
}

void setup_wifi() {
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
    delay(500);
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
    if (client.connect(clientId.c_str()))
      client.subscribe(mqtt_config_topic.c_str());
    else
      delay(2000);
  }
}

void setup() {
  setup_wifi();
  client.setCallback(callback);
  reconnect_mqtt();
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C))
    for (;;);
  display.clearDisplay();
  display.display();
}

void loop() {
  if (!client.connected())
    reconnect_mqtt();
  client.loop();
}
