from gpiozero import Button
from signal import pause

button = Button(17) # GPIO pin 17

def button_callback():
    print("Button was pressed!")

button.when_pressed = button_callback

pause()
