# battery_monitor.py
import time

# Sprawdzenie, czy używać sprzętu (ADS1115) czy trybu mock
USE_HARDWARE = 0

if USE_HARDWARE:
    import board
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
else:
    print("⚠️  Running in mock mode (no hardware).")

def calculate_battery_percentage(measured_voltage):
    """
    Oblicza procent naładowania baterii Li-ion 3.7V.
    Zakłada dzielnik napięcia 2:1 (rzeczywiste V = measured_voltage * 2).

    Args:
        measured_voltage (float): Napięcie zmierzone na dzielniku (w V).

    Returns:
        float: Procent naładowania (0-100%).
    """
    
    actual_voltage = measured_voltage * 2
    FULL_CHARGE_VOLTAGE = 4.2  # 100%
    EMPTY_VOLTAGE = 3.0         # 0%

    # Ogranicz zakres i oblicz %
    actual_voltage = max(min(actual_voltage, FULL_CHARGE_VOLTAGE), EMPTY_VOLTAGE)
    percentage = (actual_voltage - EMPTY_VOLTAGE) / (FULL_CHARGE_VOLTAGE - EMPTY_VOLTAGE) * 100
    return round(percentage)

def read_battery_voltage():
    if USE_HARDWARE:
        i2c = board.I2C()
        ads = ADS.ADS1115(i2c)
        battery_channel = AnalogIn(ads, ADS.P3)
        return battery_channel.voltage
    else:
        # Zwróć przykładowe napięcie w trybie testowym
        return 1.75  # co odpowiada ~3.3V po przemnożeniu x2

if __name__ == "__main__":
    # Testowanie modułu (uruchamiane tylko przy bezpośrednim wykonywaniu pliku)
    try:
        while True:
            voltage = read_battery_voltage()
            percentage = calculate_battery_percentage(voltage)
            print(f"Bateria: {voltage:.2f}V ({voltage * 2:.2f}V) | {percentage}%")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Zamknięto monitor baterii.")
