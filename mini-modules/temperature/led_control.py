import logging
import RPi.GPIO as GPIO

# Define the GPIO pin for the LED
LED_PIN = 27


def setup_led():
    """Initialize the LED GPIO pin."""
    # Set the pin numbering mode if not already set
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_PIN, GPIO.OUT)
    GPIO.output(LED_PIN, GPIO.LOW)
    logging.info("LED GPIO initialized; LED is OFF.")


def control_led(state: bool):
    """
    Control the LED state.

    Args:
        state (bool): True to turn the LED ON, False to turn it OFF.
    """
    if state:
        GPIO.output(LED_PIN, GPIO.HIGH)
        logging.info("LED turned ON.")
    else:
        GPIO.output(LED_PIN, GPIO.LOW)
        logging.info("LED turned OFF.")
