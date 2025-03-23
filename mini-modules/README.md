# Mini-Modules and Integration

## Overview

This project demonstrates the seamless integration of mini-modules into an MQTT-based IoT system. Our primary goal is to showcase sensor-to-actuator communication and multi-modal control using a variety of hardware components. In this release, we have successfully completed the Temperature-Triggered Fan and LED Control module. Future enhancements will include additional modules for ambient light adjustment and gesture-controlled environmental overrides.

## Completed Module

1. **Temperature-Triggered Fan and LED Control**  
   This module monitors ambient temperature (and, optionally, humidity) via a sensor connected to the MQTT hub. When the temperature exceeds a predefined threshold, it triggers a small fan and activates LED status indicators. This demonstrates real-time sensor monitoring, automated control, and MQTT-based data communication.

## In-Progress / Future Modules

2. **Ambient Light and Environmental Adjustment Module**  
   *Future work:* This module will adjust the brightness of an LCD screen and LED indicators based on environmental conditions. When critical temperature or humidity levels are detected, the system will display alerts and dynamically modify display settings.

3. **Gesture-Controlled Environmental Overrides**  
   *Future work:* Leveraging the Smart Glove's sensor suite (e.g., flex sensors, MPU6050, FSR402 force sensors), this module will enable manual override of automated actions. A specific gesture, such as a swipe or pinch, will allow users to disable or adjust actuator responses (e.g., turning off the fan) regardless of sensor readings.

## Hardware Summary

The project uses the following hardware components:

- **Core Computing Modules:**  
  - Raspberry Pi 4 or 5 (or ESP-32 for sensor interfacing)

- **Sensors:**  
  - Temperature Sensor (and optionally a Humidity Sensor)

- **Actuators:**  
  - Small Fan  
  - LEDs (used as status indicators)

- **Supporting Equipment:**  
  - Stable Battery (or power supply) for the core computing module  
  - Basic wiring and interfacing components

*Note: Only hardware directly used for the temperature-based module is listed. Additional components for future modules will be integrated later.*

## Getting Started

### Prerequisites

- Python 3.8 (or later) installed via Conda.
- An MQTT broker (e.g., Mosquitto) accessible at the specified MQTT server address.
- For testing on non-Raspberry Pi systems (e.g., macOS), a dummy `RPi.GPIO` module is provided.

### Setting Up the Environment

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/embedded-systems-platform.git
   cd embedded-systems-platform/mini-modules
   ```

2. **Create and Activate the Conda Environment**

   Run:

   ```bash
   conda env create -f environment.yml
   conda activate embedded-systems
   ```

### Project Structure

```
.
├── main.py
└── temperature
    ├── __init__.py
    ├── fan_control.py
    └── led_control.py
```

A dummy `RPi` package is also provided for testing on non-Raspberry Pi platforms.

### Running the Project

From the root directory, execute:

```bash
python mini-modules/main.py
```

This will:
- Initialize the GPIO pins for the fan and LED.
- Connect to the MQTT broker.
- Simulate sensor readings.
- Control the fan and LED based on the temperature threshold.
- Publish sensor data to the MQTT broker at regular intervals.
