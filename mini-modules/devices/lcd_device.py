from grove.display.jhd1802 import JHD1802
from time import sleep

lcd = JHD1802()

def setup():
    lcd.clear()
    lcd.setCursor(0, 0)
    lcd.write("LCD Ready...")
    lcd.setCursor(1, 0)
    lcd.write("Waiting...")

def handle_message(topic, payload, mqtt_client):
    lcd.clear()
    lcd.setCursor(0, 0)
    print(payload)
    