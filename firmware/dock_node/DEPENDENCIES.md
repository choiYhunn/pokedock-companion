# Dock Arduino dependencies
Install:
- ESP32 by Espressif Systems
- Adafruit PN532
- Adafruit VL53L0X
- BH1750 by Christopher Laws
- Adafruit NeoPixel

Before compiling:
1. Confirm exact ESP32-C3 board pinout.
2. Change SDA_PIN/SCL_PIN/LED_PIN.
3. First flash prints the Dock MAC.
4. HMI firmware prints its MAC; paste it into `HMI_MAC`.
5. Learn NFC tag UIDs and populate `mapUidToPokemon()`.