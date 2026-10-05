# Purchase list — V4 compact layout

## Core HMI
- Waveshare **ESP32-S3-Touch-LCD-4.3C-BOX**, SKU 33630
- microSD 16–32 GB
- CR927 RTC cell
- compatible speaker if not included in the purchased package

The board already provides Wi-Fi/BLE, RTC, TF/microSD, touch and audio capability; do not duplicate those modules.

## Dock node
- ESP32-C3 small dev board
- PN532 module
- NFC tags/cards
- VL53L0X
- BH1750
- 8–12 addressable RGB LEDs
- 330 Ω data resistor
- 470–1000 µF rail capacitor
- small perfboard / connectors

## Rear phone charging
Preferred:
- protected finished Qi/Qi2 charging puck/pad
- its specified power supply
- thin non-slip pad
- removable adhesive/Velcro or printed retention feature

Do **not** buy a bare anonymous Qi coil/driver as the main charging solution.

### Before choosing the final charger
Check the girlfriend's phone:
- exact model,
- normal case thickness,
- whether magnetic/Qi2 alignment is supported,
- charging coil location.

The enclosure is designed around the phone + charger, not the other way around.

## Mechanics
Fast path:
- commercial mini display/tablet stand,
- 2–3 mm acrylic/polycarbonate for rear phone slope,
- small side plate for NFC,
- VHB / screws / rubber feet,
- cable sleeve.

Custom path:
- print `cad/pokedock_v4_compact.scad` after physical dimensions are verified.

## Do not buy yet
- custom battery pack
- servo
- microphone array
- separate RTC
- separate screen
- DFPlayer
- giant RGB strip
- custom Qi RF stage
