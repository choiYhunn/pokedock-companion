# PokéDock V10 — ESP-IDF / LVGL / Hardware port checklist

## Current status — important
GitHub Pages V10 is a functional **browser simulation**, NOT a flashable ESP-IDF application. The repo has portable C++ engines, UI screen IDs, a BSP dependency manifest, and now a **console-only ESP-IDF M0 scaffold** at [firmware/hmi/espidf](../firmware/hmi/espidf/README.md). This scaffold has **not been compiled or flashed**, and no native LVGL HOME/Focus screen exists. The old `firmware/hmi/main/idf_component.yml` was never a standalone buildable app. No hardware has been flashed in this chat.

### Official references
- Board & pin map: https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3C
- Manufacturer examples/factory image/schematics: https://github.com/waveshareteam/ESP32-S3-Touch-LCD-4.3C
- BSP 3.0.1: https://components.espressif.com/components/waveshare/esp32_s3_touch_lcd_4_3c/versions/3.0.1/readme
- OTA: https://docs.espressif.com/projects/esp-idf/en/release-v5.5/esp32s3/api-reference/system/ota.html

**Board naming:** 4.3C-BOX (SKU 33630) != older 4.3 and != 4.3B. Do not copy GPIO/power instructions from older boards. 4.3C has 7–36V DC input terminal and dedicated USB-C download/debug port per vendor documentation. On 4.3C the board uses GPIO8/9 I2C shared with touch/RTC/audio and a vendor IO expander (0x24). Manufacturer example driver naming (CH422G) and managed BSP naming (CH32V003) may differ: trust the actual PCB revision/schematic and stable factory example, not guesses.

## M0 — Set up and recover vendor factory system
Windows 11 (development host) workflow:

1. Install VS Code + Espressif ESP-IDF extension. Start with ESP-IDF **5.5.x**, but follow the chosen manufacturer example's declared version where different; do not mix unmanaged LVGL v8 source with new LVGL v9 BSP.
2. Download a specific version/commit of official Waveshare 4.3C examples, factory firmware, and schematic. Save the exact manufacturer commit hash/board revision in a local test log.
3. Confirm board power terminal/polarity and certified regulated supply against manual/silkscreen. Power off before changing wires.
4. Use **factory 4.3C** firmware to verify LCD, touch, RTC, SD, audio if speaker fitted, brightness and Wi-Fi.
5. From the manufacturer-provided **ESP-IDF example directory** containing an application CMakeLists.txt (not from the root of this PokéDock repo), run:

    idf.py --version
    idf.py set-target esp32s3
    idf.py build
    idf.py -p COMx flash monitor

   COMx = actual Device Manager COM port, not a literal port name. Vendor example and CMake dependencies must be selected first. Log warnings/errors and export the factory-recovery procedure.

**Gate:** screen + touch orientation correct, RTC/date persists when power removed with CR927, SD mount/read pass, no repetitive crashes for 60 min.

## M1 — Real basic native UI
Starting from a *passing* vendor ESP-IDF project:

- Turn on BSP LCD/touch/LVGL, HOME screen with clock and Gengar static frame. Keep display and UI ownership on LVGL task. Validate an 800×480 pointer at all four corners.
- Copy portable StudyEngine core into the native project; use monotonic elapsed time rather than counting FreeRTOS callbacks (a tick may arrive late).
- Implement focus 15/25/45 min → 5 min rest; plain 3/5/10/30 min timer and a single Back stack. Completion must increment study/reward exactly once; break gives no EXP.
- Implement versioned NVS for settings/todos/D-day/partner/anniversary/private note with explicit erase controls. RTC/NTP timezone and unsynced-time UI are separate concerns.
- A 4.3inch screen has very small physical touch dimensions: evaluate real text legibility and >= ~44 display-pixel touch boxes in a photo/physical finger test.
- Ensure button acceptance and timer are correct while user opens a menu; do not block LVGL with networking callbacks.

Suggested **future** project (not yet compiled):
    firmware/hmi/espidf/
      CMakeLists.txt
      main/app_main.cpp
      main/screens/{home,focus,menu,party,settings}.cpp
      main/services/{clock,study,nvs,asset_reader}.cpp
      main/ui_navigation.cpp
      assets/

## M2 — Native animation / assets
- The web PARTY SELECT uses remote PokeAPI artwork/GIF and CSS. ESP32-S3 does NOT run that HTML page via LVGL. Convert licensed/reviewed sprites to LVGL compatible static image + small sprite sheet and control their state with the portable partner_motion.h.
- 5 key motions: Gengar sneak/peek, Piplup hop, Togekiss glide, Lucario stance, Quagsire sway.
- Limit animation to idle/preview/tap events, no continuous GPU-intensive full-screen transitions. Freeze during Focus/Night/reduced-motion. Profile CPU, external PSRAM, SD latency, LVGL mutex, input latency.
- Keep 1 static fallback portrait per character when SD missing. Do not depend on internet for gifts to work.

## M3 — Mechanical assembly & MagSafe
- Confirm iPhone 14 variant/case/camera bump. Assemble temporary sloped support with a complete protected MagSafe charger and a dedicated USB-C PD adapter.
- Keep the complete Qi/MagSafe RF electronics factory-built. Don't hide wiring under pressure or obstruct puck cooling.
- Test 30 phone dock/undock cycles, one-hand retrieval, 60 min charging temperature/stability with HMI also powered. HMI presence sensors cannot know true Qi/battery state.

## M4 — OTA — after first stable native build
The files under firmware/hmi/ota/ are **only a 16MB partition proposal**, not automatically active. Ensure compiled app fits both OTA slots; ensure bootloader, partitions and signing/network validation tested.

- HTTPS firmware download into inactive ota_0/ota_1; integrity and board identity check.
- Reboot and self-test LVGL/touch/RTC/user storage before confirming valid app.
- On failure rollback to prior working app; always preserve USB-C rescue workflow.
- Private settings must live outside OTA app partitions and remain across upgrades.
- Future independently updated SD artwork needs atomic staging, manifest SHA-256 and compatible version mapping — not implemented yet.
- ESP32-C3 Dock node would be a **separate firmware/OTA image**, not the HMI binary.

## M5 — Optional Dock node, last
Only if M0–M4 are stable and still time/budget:
- ESP32-C3 + PN532 NFC, optional BH1750 lux, optional VL53L0X presence, optional small WS2812B LEDs. Verify actual selected board pinout and each breakout's voltage/level requirements.
- ESP-NOW transport requires HMI STA Wi-Fi channel and C3 peer channel coordination. Callback → ring/queue → task → UI state; never mutate LVGL directly from ESP-NOW callback.
- Do **not** make iOS ANCS alerts a gift-readiness blocker. Ordinary BLE pairing is insufficient for phone-wide iPhone notifications.

## Validation gates before calling it gift-ready
- M0 manufacturer factory hardware passes.
- M1 physical HOME/Focus/plain timer/back tested 1 hour, 5 power cycles, no lost personal note.
- M2 chosen animations run with no touch lag and stop in Focus/Night.
- M3 MagSafe phone/case fit/heat and rear mechanical safety proven.
- M4 optional OTA only if rollback and bad-image/power-loss tests passed; until then explicitly offer USB updates.
- M5 optional NFC/LED only after previous gates.

## Do not misrepresent
Do not say complete device UI, sensor, charging state, iPhone notification adapter or OTA is working until tested with hardware. Initial Wi-Fi can be used for NTP in a later milestone; no internet should be required for normal clock/timer after RTC sync.
