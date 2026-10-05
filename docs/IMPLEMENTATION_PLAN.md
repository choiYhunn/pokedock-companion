# Implementation roadmap

## Already scaffolded
- V4 product scope
- physical layout
- study engine
- UI decision model
- phone bridge abstraction
- notification filter
- web API contract
- local settings HTML
- Dock protocol
- CAD concept

## Phase A — before hardware
Can be completed without the board:
1. host tests for StudyEngine
2. JSON config parser contract
3. study log CSV/JSON schema
4. todo/D-day model
5. weather provider interface
6. LVGL screen component map
7. ESP-NOW packet simulator
8. browser settings page behavior

## Phase B — first HMI
Start from official Waveshare BSP/example.
Adapters:
- `ClockService` → PCF85063 + NTP
- `StorageService` → NVS + microSD
- `DisplayService` → LVGL
- `AudioService` → ES8311
- `WebSettingsService` → ESP-IDF HTTP server
- `DockLink` → ESP-NOW

## Phase C — first Dock
- sensor bring-up
- heartbeat
- filtered phone distance
- NFC UID enrollment
- LED theme

## Phase D — product integration
- rear phone presence affects only status/charging animation
- side NFC changes companion/theme
- focus state controls LEDs and notification policy
- network failures never stop timing

## Phase E — optional phone bridge
Choose based on target phone OS:
- Android helper app + notification listener, or
- iOS ANCS adapter.

Do not start both in parallel.

## Definition of V1 done
The product is gift-ready when:
- all offline study tools survive reboot/network loss,
- phone charges stably behind the HMI,
- NFC works with Qi active,
- web settings work on local Wi-Fi,
- one-hour soak passes,
- birthday event can be test-triggered,
- no debug UI or exposed wiring remains.
