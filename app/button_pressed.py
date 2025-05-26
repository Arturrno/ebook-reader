# button_checker.py
import time

# Przełącznik: czy używać sprzętu GPIO (RPi), czy trybu symulowanego
USE_HARDWARE = 0

if USE_HARDWARE:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
else:
    print("⚠️  Running in mock mode (no GPIO).")

def is_button_pressed(pin, debounce_time=0.15):
    """
    Sprawdza, czy przycisk podłączony do danego pinu GPIO został wciśnięty.
    Uwzględnia debouncing (eliminację drgań styków).

    Parametry:
        pin (int): Numer pinu GPIO (BCM).
        debounce_time (float): Czas debounce w sekundach.

    Zwraca:
        bool: True, jeśli przycisk wciśnięty; False inaczej.
    """

    if USE_HARDWARE:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        current_state = GPIO.input(pin)

        if current_state == GPIO.LOW:
            time.sleep(debounce_time)
            return GPIO.input(pin) == GPIO.LOW
        return False
    else:
        # W trybie testowym zawsze zwracaj False lub losowo
        # Możesz zmienić to na np. random.choice([True, False])
        return False

if __name__ == "__main__":
    try:
        BUTTON_PIN = 21  # np. GPIO21 (pin fizyczny 40)
        while True:
            if is_button_pressed(BUTTON_PIN):
                print("Przycisk wciśnięty!")
                time.sleep(0.2)
    except KeyboardInterrupt:
        if USE_HARDWARE:
            GPIO.cleanup()
        print("Zakończono program.")
