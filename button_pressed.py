import RPi.GPIO as GPIO
import time

# Inicjalizacja GPIO
GPIO.setmode(GPIO.BCM)  # Numeracja BCM (np. GPIO17, a nie pin 11)

def is_button_pressed(pin, debounce_time=0.15):
    """
    Sprawdza, czy przycisk podłączony do danego pinu GPIO został wciśnięty.
    Uwzględnia debouncing (eliminację drgań styków).

    Parametry:
        pin (int): Numer pinu GPIO (w numeracji BCM).
        debounce_time (float): Czas debounce w sekundach (domyślnie 0.05s).

    Zwraca:
        bool: True, jeśli przycisk jest wciśnięty (po uwzględnieniu debounce).
    """
    # Konfiguracja pinu jako wejście z podciągnięciem do góry (przycisk podłączony do GND)
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Odczytaj stan początkowy
    current_state = GPIO.input(pin)

    # Jeśli przycisk jest wciśnięty (stan LOW, bo podciągnięty do VCC)
    if current_state == GPIO.LOW:
        time.sleep(debounce_time)  # Czekaj na ustabilizowanie
        if GPIO.input(pin) == GPIO.LOW:  # Sprawdź ponownie
            return True
    return False

# Przykład użycia:
if __name__ == "__main__":
    try:
        BUTTON_PIN = 21  # Przykładowy pin GPIO17
        while True:
            if is_button_pressed(BUTTON_PIN):
                print("Przycisk wciśnięty!")
                time.sleep(0.2)  # Dodatkowe opóźnienie, aby uniknąć wielokrotnych detekcji
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("Zakończono program.")
