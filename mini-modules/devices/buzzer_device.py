from gpiozero import PWMOutputDevice
from time import sleep

buzzer = PWMOutputDevice(18)

def setup():
    buzzer.off()
    print("[Buzzer] Ready.")

def handle_message(topic, payload, mqtt_client):
    """
    Expected payload:
    {
        "data": {
            "notes": [440, 494, 523, 587, 659, 698, 784, ...]   # List of tones (Hz)
                     [330,294,262,294,330,330,294,294,294,330,392,392]
            "duration": 0.3                                     # Optional: duration per tone (sec)
        }
    }
    """
    try:
        notes = payload.get("data", {}).get("notes", [])
        duration = payload.get("data", {}).get("duration", 0.3)

        if not isinstance(notes, list):
            print("[Buzzer] Invalid notes format")
            return

        for tone in notes:
            buzzer.frequency = int(tone)
            buzzer.value = 0.5
            print(f"[Buzzer] Playing tone: {tone}Hz")
            sleep(duration)
            buzzer.off()
            sleep(0.05)  # short pause between tones

    except Exception as e:
        print(f"[Buzzer] Error: {e}")
