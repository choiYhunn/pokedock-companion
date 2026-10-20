# V16 Electrical and Power Interface — unverified hardware contract

## Candidate board selection (NO PURCHASE)
- First optical candidate: Waveshare ESP32-S3-Touch-AMOLED-2.41 / 2.41-B (manufacturer lists 600x450, 800cd/m2, ESP32-S3R8, 16MB Flash, 8MB PSRAM, USB-C, RTC, TF slot).
- PCB versions V1 and V2 have **different pin mappings** for some signals. Vendor expressly warns that firmware examples are NOT interchangeable; inspect PCB Rev2.0 or B model QC label, then pin the matching schematic and source revision.
- Integrated capacitive touch is underneath the reflector in the intended assembly; it is NOT the primary user input. One external push encoder is a candidate only after available GPIO are verified.
- Main board has **NO integrated speaker** per manufacturer comparison. An audible alarm needs a separately verified buzzer or I2S amplifier/speaker. Default design allows silent-only clock/focus.

## Electrical topology: candidate, not final pin assignment
Certified isolated 220Vac-to-5Vdc USB supply
  -> verified USB-C cable
  -> Waveshare 2.41 main board USB-C input (no loose live 220Vac wiring)
  -> exposed I2C connector at 3.3V-logic (pinout from matching V1/V2 schematic)
      -> SSD1327 1.5in clock OLED only after its I2C hardware-mode resistors and I2C address are checked
  -> verified spare GPIO + debounce/pull-up
      -> incremental encoder/push input (NOT bare 5V logic signals)
  -> OPTIONAL spare GPIO through suitable transistor/driver
      -> low power buzzer (audible alarm), only after current and back-EMF protection reviewed if inductive
  -> RTC PCF85063 for offline clock once appropriate backup-cell arrangement is verified;
     note manufacturer RTC backup header says CHARGING, do not insert a non-rechargeable cell without checking circuitry.
  -> optional TF/microSD for large private animation packs; no hardcoded network-only assets

## Interface risk register
- OLED module may ship configured for SPI; SSD1327 1.5 Waveshare supports I2C after module configuration; verify resistor selector and schematic before wiring.
- Shared I2C bus already carries touch, IMU and RTC. SDA/SCL candidate GPIO47/48 per V1 docs; **V2 variant needs matching schematic verification**; scan addresses (e.g. OLED nominal 0x3C/0x3D) for collisions.
- 5V USB supplies primary power; DO NOT feed OLED module from a 5V logic source into 3.3V I2C without verified translators.
- 3.3V regulator capacity for external OLED is UNKNOWN; measure current draw, idle and peak, before connecting.
- No battery in the final gift baseline. Thus clock/alarm cannot operate while power is disconnected; RTC backup preserves time only when its backup power arrangement is electrically verified.
- No mains wiring inside the case, no improvised lithium charging, no USB power-path assumptions from older 4.3C board.
- Physical USB bend radius and cable strain relief are the *rear CAD* design gates.

## Pin confirmation and first hardware acceptance
1. Photograph actual PCB markings, confirm V1/V2/2.41-B variant, record schematic URL+SHA.
2. Run maker factory graphics + RTC + TF demos. Do not flash a proposed dual OTA partition CSV first.
3. Measure 5V USB supply power budget at normal and max brightness; verify 60min no overheating.
4. Locate 3.3V/I2C header orientation with DMM and data sheet; scan I2C bus before SSD1327 connection.
5. Bring up front clock alone (large digits, daylight distance 60cm) then panel alone; only after both work test optical assembly.
6. Encoder action x30, silent/default alarm, optional buzzer mute/snooze; test 5 power cycles and RTC trust.
7. **Only after** repeated bench pass and USB recovery: configure signed HTTPS OTA.

Official references:
https://docs.waveshare.com/ESP32-S3-Touch-AMOLED-2.41
https://www.waveshare.com/esp32-s3-touch-amoled-2.41.htm
https://www.waveshare.com/wiki/1.5inch_OLED_Module
