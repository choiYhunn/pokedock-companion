# Porting checklist

## Base project
Start from an official 4.3C ESP-IDF LVGL example or a minimal managed-BSP project.

## First PokéDock screen
Only render:
- time
- Focus button
- timer
- bottom nav

Then connect `StudyEngine`.

## Required task separation
Suggested FreeRTOS ownership:
- UI/LVGL task: widgets only
- time/study tick task: monotonic timing
- network task: Wi-Fi/NTP/weather
- storage task: SD writes
- Dock receive callback → queue → app task

Never update LVGL directly from an ESP-NOW/Wi-Fi callback.

## Milestones
M0: display + touch + HOME mock + 60-second Focus test.
M1: RTC + pause/resume + timer/stopwatch + persistence.
M2: Wi-Fi/NTP + web settings + weather.
M3: Dock Node + rear phone parked state + side NFC + ambient LED.
M4: audio cues + Dex rewards + birthday event + optional phone bridge.

## V9 animated UI / OTA milestones

- M5a: Make LVGL version of PARTY SELECT with 5 core-character sprite sheets. Touch, back, selection, Focus gate, and reduced motion.
- M5b: Confirm 800×480 actual viewing distance, static/animated FPS and PSRAM usage. Limit background idle cues; never let animation starve input or RTC.
- M5c: Copy externally referenced sprite assets to a reviewed/licensed offline package; resize and pack; fallback assets on card failure.
- M6: Enable custom OTA partition layout and HTTPS firmware update on ESP-IDF project, perform health-gated rollback. The proposed 16MB table in `ota/` is not active yet.
- M6b: Design atomic, signed/integrity-checked asset-pack swaps after firmware OTA works. HMI and ESP32-C3 Dock need separate images/update procedures.
