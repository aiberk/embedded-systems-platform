# Mini-Modules and Integration

This project demonstrates a complete embedded systems solution using MQTT to coordinate communication between multiple hardware components. The system includes a button (input device), and three actuators: a fan (LED), a buzzer, and an LCD display. These devices interact through an MQTT broker to simulate a responsive smart environment using Raspberry Pi.


## 📡 Project Overview

This system is structured around MQTT-based publish/subscribe messaging. When the **button is pressed**, a message is published to a topic subscribed by the **fan**, **buzzer**, and **LCD** devices. Each device responds to messages according to its role:

- **Fan (LED)**: Turns ON/OFF on command.
- **Buzzer**: Plays melodies by frequency.
- **LCD Display**: Shows text (e.g., emotion or status).

Each device has a unique `device_id` and MQTT configuration.


## 🧰 Hardware Components

| Device       | GPIO Pin | Description                        |
|--------------|----------|------------------------------------|
| Button       | GPIO 17  | Input button (triggers message)    |
| Fan (LED)    | GPIO 22  | LED used to simulate a fan         |
| Buzzer       | GPIO 18  | PWM pin used for tone generation   |
| LCD Display  | I2C (SDA: GPIO 2, SCL: GPIO 3) | Displays text via Grove JHD1802 |


## 🗂️ Project Structure

```

.
├── main.py                     # Main runner script
├── config/                     # MQTT topics and device IDs
│   ├── button_config.py
│   ├── fan_config.py
│   ├── buzzer_config.py
│   └── lcd_config.py
├── devices/                    # Device logic
│   ├── button_device.py
│   ├── fan_device.py
│   ├── buzzer_device.py
│   └── lcd_device.py
├── core/                       # MQTT client and broker resolver
│   ├── mqtt_client.py
│   └── broker.py
└── hardware/
    └── gpio.py                 # GPIO pin mapping

````

## ⚙️ Software Setup

### Prerequisites

- Raspberry Pi OS (Lite or Full)
- Python 3.8+
- MQTT broker running (e.g., Mosquitto)
- Python packages:

```bash
pip install paho-mqtt gpiozero grove.py
````

### Clone and Run

```bash
git clone https://github.com/aiberk/embedded-systems-platform.git
cd embedded-systems-platform/mini-modules
python main.py
```

## 🔁 System Behavior

### 📥 Button

When pressed, it sends the following MQTT payload:

```json
{
  "device_id": "jLDT3JpuGeC6Ard52HYkHN",
  "timestamp": 1690000000000,
  "data": {
    "ping": false,
    "isClicked": true
  }
}
```

### 🌀 Fan (LED)

Listens for:

```json
{
  "data": {
    "fan": "true"
  }
}
```

Turns ON if `"true"`, OFF if `"false"`.

### 🔊 Buzzer

Listens for:

```json
{
  "data": {
    "notes": [440, 494, 523],
    "duration": 0.3
  }
}
```

Plays a tone for each note.

### 📺 LCD Display

Listens for:

```json
{
  "data": {
    "emotion": "happy"
  }
}
```

Displays `Emotion: happy` or any 16-character message.


## 🧩 Extensibility

To add new devices:

1. Create a new device module under `devices/`.
2. Add a config file under `config/`.
3. Register it in `main.py` using `MQTTDeviceClient`.
