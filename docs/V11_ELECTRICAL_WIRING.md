# PokéDock V11 — power domains, wiring and audio interfaces

## Mandatory supply split during prototype (no mains wiring)
\`\`\`text
Certified regulated 12V DC supply (candidate, verify rated board connector)
    -> polarity check with DMM -> 7–36V terminal on exact 4.3C-BOX
    -> onboard 3.3V/5V regulators -> display/RTC/codec/MCU

Separate certified USB-C PD power adapter (>=20W per charger requirements)
    -> finished MagSafe puck -> iPhone 14-family
    NO electrical wiring from MagSafe output to ESP32-S3 GPIO

PHASE B / OPTIONAL:
    separate approved regulated low-voltage adapter -> ESP32-C3 devboard
       3.3V-logic I2C -> PN532 or BH1750 after breakout verification
       correctly level-shifted data + regulated 5V -> 4–8 WS2812B LEDs
       ESP-NOW 2.4GHz wireless ↔ ESP32-S3 (NO physical signal cable)
\`\`\`

**Do not bridge DC power rails across subsystems**. Never apply 12V to USB-C, GPIO, USB, I2C or 5V sensor pads. The cased 4.3C differs from older ESP32-S3-Touch-LCD-4.3 that is 5V Type-C powered. Check 4.3C delivered PCB silkscreen, schematic terminal +/− and regulator rating. If unsure, stop before power-up.

## Confirmed from official Waveshare 4.3C documents
- SKU 33630 = cased C-BOX, 800×480, 16MB flash/8MB PSRAM, Wi-Fi/BLE.
- Display on RGB peripheral; GT911 touch, PCF85063A RTC and ES8311 codec use existing board buses.
- GPIO8 (SDA) and GPIO9 (SCL) are already on shared I2C; expansion board at I2C address 0x24. Do not attach unknown conflicting device/address.
- RTC backup cell CR927; follow board polarity.
- MicroSD uses onboard SDMMC, not arbitrary Arduino SPI GPIO assumptions.
- ES8311 codec is capable of audio playback **if an appropriate compatible speaker is actually installed/attached**. Verify MX1.25 2-pin speaker hardware and load rating on delivered product. Do not wire a loudspeaker directly to an ESP32 GPIO.
- Some product pictures list a speaker interface but package contents vary. Inspect physical unit before buying an extra speaker.

### Board connection list, Stage A
| Port / signal | Connect | Evidence needed |
| --- | --- | --- |
| DC terminal 7–36V | Regulated **12V DC candidate** via insulated properly rated connector | polarity/terminal access/supply from board marking + vendor schematic |
| USB-C | PC data cable for ESP-IDF flashing/debugging | COM/JTAG enumeration, manufacturer's prescribed power sequence |
| RTC coin holder | CR927 installed with correct polarity | board time retention after disconnect |
| TF/microSD | FAT-compatible card | factory SD read/write test |
| Speaker header | only manufacturer's matching impedance/rating speaker after inspection | audio example, volume/safe night test |
| GPIO8/9 shared I2C | DO NOT rewire for basic HMI | preserved by vendor BSP |
| MagSafe puck USB-C | its own separate compatible USB-C PD adapter | charge stability, real iPhone/case test |

Do not wire a generic 12V supply's DC barrel jack directly to a screw terminal without the correct insulated connector/pigtail and polarity check. The HMI should only be powered by a manufacturer-compatible supply path.

### Stage B Dock Node connector map (conditional, not a ready-to-solder pin assignment)
- ESP32-C3 **specific module SKU still TBD**: avoid strapping/flash pins, reserve GPIO for PN532 I2C or SPI, optional ToF/lux and LED.
- Some PN532 boards have 5V module power while logic is 3.3V; read the exact module's datasheet, supply and I2C pull-up voltage before connecting.
- Example optional sensor address table: BH1750 usually 0x23/0x5C, VL53L0X typically 0x29, PN532 address depends on I2C breakout/library. Must be scanned/verified on C3 separate bus.
- LED power: worst-case full-white draw ~60mA per WS2812B RGB LED (manufacturer variant dependent). For 8 LEDs budgeting up to ~480mA + headroom is safer than assuming theme color's small average current. Limit brightness in software. 330ohm series data resistor, adequately rated regulator, decoupling capacitor ~470–1000µF; use a proper 3.3V-to-5V digital level shifter if LED requires it. No solder until actual LED type identified.
- C3-to-HMI ESP-NOW peers must use compatible Wi-Fi channels; HMI and phone Wi-Fi STA behaviour can change channel. Packet sequence/CRC/timeout and bounded event queue are firmware tasks, not proven yet.
- VL53L0X phone presence ≠ actual Qi power transfer/charge state and cannot reveal iPhone battery %. If presence sensor adds little value, omit it.

## Basic bring-up / diagnostics
1. Verify DMM supply output unloaded. Confirm HMI DC terminal polarity/voltage. Observe vendor current draw and touch response with manufacturer firmware.
2. Insert backup RTC cell only as instructed, validate power-down holdover.
3. Use PC USB-C for serial. Don't probe high-density pads with a floating bare wire.
4. Check board temperature and cable strain under 1h LCD load without the phone charger attached.
5. Power independent MagSafe/phone. Compare before/after EMC/Wi-Fi/touch behaviour; do not assume zero interference.
6. Only after these pass, enable Stage B sensors one at a time on an independent C3 breadboard and measure actual voltages.
7. Disconnect DC supplies before rewiring, keep mains adapters closed/certified, use strain relief and service loops.

## Future personalized alarm audio (P2; NOT IMPLEMENTED)
1. Audio asset import: **user-provided files** via microSD or local HTTP upload, safe size/name validation and directory scoping (e.g. \`/alarms/\`).
2. Decode/resample to **PCM 16-bit mono WAV** (e.g. 16kHz or 22.05kHz) before ES8311/I2S playback, or add a separately verified MCU decoder for compressed formats. Limit duration, max bytes and simultaneous buffer load.
3. Sound options: quiet default tone, local user-supplied sound, optional Pokémon-like synthesized effect; mute, volume, fade-in, snooze, quiet hours, hardware failsafe fallback.
4. Pokémon cries/game music are copyrighted: do not ship scraped commercial files or distribute them through public repo. Personal audio should stay in user-owned storage. Do not assume DRM-protected iPhone Music/Spotify tracks are available as raw audio files.
5. Hardware test: verify compatible speaker/codec route using Waveshare \`11_speaker_microphone\` example. Do not promise full MP3/M4A compatibility until tested.

## Authoritative docs
https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3C
https://github.com/waveshareteam/ESP32-S3-Touch-LCD-4.3C/blob/main/HARDWARE_REFERENCE.md
https://support.apple.com/ko-kr/111850
