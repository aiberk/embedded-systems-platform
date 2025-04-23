import logging

# Set a BCM-like mode constant (dummy)
BCM = "BCM"

# Define some dummy pin modes and states
OUT = "OUT"
IN = "IN"
HIGH = True
LOW = False

# A dictionary to simulate pin states
_pin_states = {}

def setmode(mode):
    logging.info(f"RPi.GPIO: setmode({mode})")

def setup(pin, mode):
    _pin_states[pin] = LOW
    logging.info(f"RPi.GPIO: setup(pin={pin}, mode={mode})")

def output(pin, state):
    _pin_states[pin] = state
    logging.info(f"RPi.GPIO: output(pin={pin}, state={state})")

def cleanup():
    global _pin_states
    _pin_states = {}
    logging.info("RPi.GPIO: cleanup()")
