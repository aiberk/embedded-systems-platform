from gpiozero import Button, LED  # Add Fan/LED/etc here

button = Button(17)
fan = LED(27)  # Example GPIO pin for fan

def setup_devices(button_callback):
    button.when_pressed = button_callback

def trigger_devices():
    print("Button was pressed, triggering devices.")
    fan.on()
