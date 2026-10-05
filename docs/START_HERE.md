# PokéDock V2 — START HERE

목표: 생일 직전 **하루**에 납땜·조립·플래시·검증을 끝내는 Pokémon-themed bedside/desk companion dock.

## 최종 아키텍처
- **HMI Node:** Waveshare ESP32-S3-Touch-LCD-4.3C-BOX (SKU 33630)
  - 4.3" / 800×480 capacitive touch
  - RTC / microSD / audio / Wi-Fi / BLE
  - LVGL UI, clock, focus timer, Dex, birthday event
- **Dock Node:** ESP32-C3 SuperMini
  - PN532 NFC
  - VL53L0X phone presence
  - BH1750 ambient light
  - WS2812/SK6812 ambient LEDs
- **Link:** ESP-NOW, heartbeat + event packets
- **Charging:** independent certified Qi pad, mechanical integration only

## V1 fixed features
1. Clock/date
2. Pokémon ambient home
3. Focus timer
4. NFC theme switching
5. Phone-docked → Pachirisu
6. Night/low-light → Gengar
7. Morning → Togepi
8. Calm evening → Togekiss
9. Birthday → Jirachi special event
10. Random Encounter / Dex
11. Ambient LED theme
12. Wireless charging pad

## Not in birthday V1
- custom Li-ion battery pack
- voice recognition
- servo mechanisms
- live weather API dependency
- phone battery percentage
- custom Qi RF electronics

Those are V2-after-birthday features.

## 3D printing
Optional. It is only one mechanical implementation. A commercial stand is the preferred one-day-build fallback.

## Read in this order
1. `docs/PURCHASE_NOW.md`
2. `docs/PRE_BUILD.md`
3. `docs/ARCHITECTURE.md`
4. `prototype/ui_v2.html`
5. `docs/BUILD_DAY.md`
6. `docs/TEST_MATRIX.md`