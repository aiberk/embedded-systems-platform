# SmartGlove

The Smart Glove module is a sub-module in out IoT Platform project. It will contain following features:
- A phisical glove implemented with Raspberry Pi 4B and several sensors.
- Gesture recognition funcion.
- Fist recognition.
- Press recognition.
- Integrated with IoT platform.

## Framework

The framework of the hardwares are:

<img src="docs/readme/v1/framework.png" alt="Framework Structure" width="450"/>

The repo here mainly is about computing server side, glove side is responsible for collecting sensor data and publish them into ROS network and allow computing center to calculate.

The code deployed on the Raspberry Pi 4B (Glove Side) is stored separately in the following repository:

https://github.com/jeffliulab/SmartGlove_GloveSide

The communication layer is based on ROS Humble:

<img src="docs/readme/v1/ros.png" alt="Framework Structure" width="450"/>


## V1: Gesture Recognition


In the first phase, this project will complete a smart glove that can recognize gestures.

The project adopts a ROS architecture, with Ubuntu 22.04 and ROS Humble installed on both Raspberry Pi 4B and PC (virtual machine) to facilitate future expansion and implementation of complex functions.

The configuration structure is as follows:

- [Demo Video](https://youtube.com/shorts/qYl0_Sqa9_Q?si=NIhDoCjUwTQr8ySr)

Using gravity detection from the MPU9250, we've implemented UP and DOWN detection:

<img src="docs/readme/v1/detect_1.png" alt="Upward Detection" width="350"/> <img src="docs/readme/v1/detect_2.png" alt="Downward Detection" width="350"/>


The physical implementation looks like this:

<img src="docs/readme/v1/prototype.jpg" alt="Physical Prototype" width="350"/>

