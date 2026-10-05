# PokéDock Companion

A compact Pokémon-themed **study / desk companion** built around a 4.3-inch ESP32-S3 touch HMI.

## V4 direction

The product is now deliberately compact:
- no front charging tray,
- phone parked behind the display on a simple sloped support,
- Qi charger integrated into that rear support,
- small NFC / figure pod on the side,
- clean front edge,
- subtle underside light.

The screen is the product; charging and NFC are supporting interactions.

## Daily functions
Offline core:
- clock / RTC
- alarm
- Pomodoro / focus
- countdown timer
- stopwatch + lap
- study-session log
- daily / weekly totals and streak
- D-day / small todo list
- NFC modes
- ambient/night mode

Wi-Fi enhancement:
- NTP
- weather
- local phone web settings
- OTA

Optional phone bridge:
- priority call / calendar / selected-contact summaries
- implemented behind a platform adapter so Android/iOS differences do not block V1

## Hardware
- HMI: Waveshare ESP32-S3-Touch-LCD-4.3C-BOX, SKU 33630
- Dock node: ESP32-C3
- NFC: PN532 on Dock Node
- phone presence: VL53L0X
- room light: BH1750
- ambient light: WS2812B/SK6812
- charging: independent protected Qi/Qi2 charger
- HMI ↔ Dock: ESP-NOW

## Read first
1. `docs/PRODUCT_V4.md`
2. `docs/PHYSICAL_LAYOUT_V4.md`
3. `docs/PHONE_LINK.md`
4. `docs/PURCHASE_NOW.md`
5. `docs/BUILD_DAY.md`

## Firmware
Portable core logic now lives under `firmware/hmi/core/`.
Board-specific Waveshare/LVGL integration stays separate so UI/driver bring-up cannot corrupt timer/study logic.

## Mechanical note
3D printing is optional. `cad/pokedock_v4_compact.scad` is a reference geometry, not a final production enclosure.

## IP note
Personal, non-commercial fan project. Pokémon names/characters/artwork belong to their respective rights holders. Artwork is not committed to this repository.
