"""
collect.py

This script collects sensor data from the MPU9250 for motion recognition training.
Hardware connections (refer to documentation):
  SDA → GP0 (Pin 1)
  SCL → GP1 (Pin 2)
  GND → Pin 36
  VCC → Pin 38

Collection procedure:
1. Collect data for two actions: raising the arm and lowering the arm.
2. For each action, the script will prompt you to type 'y' to start data collection (about 2 seconds).
3. Data collection automatically stops after the duration and moves on to the next action until all cycles are complete.
4. The collected data is organized into a CSV file saved on the Pico's filesystem (typically in the root directory).
"""

import utime
from machine import I2C, Pin
from mpu9250 import MPU9250

# ---------------------------
# 1. Initialize I2C and MPU9250 sensor
# ---------------------------
# Note: sda=GP0, scl=GP1
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
sensor = MPU9250(i2c)
print("MPU9250 id: " + hex(sensor.whoami))

# ---------------------------
# 2. Data collection settings
# ---------------------------
# Define two actions in order: raise arm then lower arm
actions = [("raise", "Raise Arm"), ("lower", "Lower Arm")]

# Set collection duration (in seconds) and sampling interval (in seconds) for each action
trial_duration = 1      # Collect data for 2 seconds per action
sampling_interval = 0.1 # Sampling interval of 100 milliseconds

# Prompt the user to enter the number of cycles for each action
try:
    num_cycles = int(input("Please enter the number of cycles for each action (e.g., 3): "))
except Exception as e:
    print("Invalid input, defaulting to 1 cycle")
    num_cycles = 1

# List to store all collected data.
# Each record contains: action label, time elapsed (ms) since start of collection,
# acceleration, gyroscope, magnetic data, and temperature.
data = []

# ---------------------------
# 3. Data collection loop
# ---------------------------
for cycle in range(num_cycles):
    print("======== Cycle {}/{} ========".format(cycle+1, num_cycles))
    # Loop through each action in order
    for label, prompt in actions:
        print("Please perform the action: {}".format(prompt))
        # Wait for the user to type 'y' to start collection
        while True:
            start_cmd = input("Type 'y' to start data collection: ").strip().lower()
            if start_cmd == 'y':
                break
            else:
                print("Invalid input. Please type 'y' to start.")
        print("Starting data collection for '{}' for {} seconds...".format(prompt, trial_duration))
        start_time = utime.ticks_ms()
        elapsed = 0
        while elapsed < trial_duration * 1000:
            current_time = utime.ticks_ms()
            elapsed = utime.ticks_diff(current_time, start_time)
            # Read sensor data
            acc = sensor.acceleration   # (x, y, z) in m/s^2
            gyro = sensor.gyro          # (x, y, z) in rad/s
            mag = sensor.magnetic       # (x, y, z) in uT
            temp = sensor.temperature   # Temperature in Celsius

            # Record one sample (time in milliseconds)
            record = {
                "action": label,
                "time": elapsed,
                "acc_x": acc[0],
                "acc_y": acc[1],
                "acc_z": acc[2],
                "gyro_x": gyro[0],
                "gyro_y": gyro[1],
                "gyro_z": gyro[2],
                "mag_x": mag[0],
                "mag_y": mag[1],
                "mag_z": mag[2],
                "temp": temp
            }
            data.append(record)
            utime.sleep(sampling_interval)
        print("Data collection for action '{}' completed.\n".format(prompt))
        utime.sleep(1)  # Brief pause between actions

print("All data collection cycles completed.")

# ---------------------------
# 4. Save data to a CSV file
# ---------------------------
csv_filename = "data.csv"
try:
    with open(csv_filename, "w") as f:
        # Write CSV header
        header = "action,time,acc_x,acc_y,acc_z,gyro_x,gyro_y,gyro_z,mag_x,mag_y,mag_z,temp\n"
        f.write(header)
        # Write data rows
        for rec in data:
            line = "{action},{time},{acc_x},{acc_y},{acc_z},{gyro_x},{gyro_y},{gyro_z},{mag_x},{mag_y},{mag_z},{temp}\n".format(**rec)
            f.write(line)
    print("Data successfully saved to '{}' in the Pico's filesystem.".format(csv_filename))
    print("You can access the file using your development environment or by connecting the Pico to your computer.")
except Exception as e:
    print("Error saving data: ", e)
