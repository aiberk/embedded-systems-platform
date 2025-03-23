import logging
import RPi.GPIO as GPIO

# Define the GPIO pin for the fan
FAN_PIN = 17


def setup_fan():
    """Initialize the fan GPIO pin."""
    # Set the pin numbering mode if not already set
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(FAN_PIN, GPIO.OUT)
    GPIO.output(FAN_PIN, GPIO.LOW)
    logging.info("Fan GPIO initialized; fan is OFF.")


def control_fan(state: bool):
    """
    Control the fan state.

    Args:
        state (bool): True to turn the fan ON, False to turn it OFF.
    """
    if state:
        GPIO.output(FAN_PIN, GPIO.HIGH)
        logging.info("Fan turned ON.")
    else:
        GPIO.output(FAN_PIN, GPIO.LOW)
        logging.info("Fan turned OFF.")
