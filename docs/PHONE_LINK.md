# Phone integration strategy

PokéDock can use Wi-Fi and BLE, but phone integration must not become a hard dependency.

## Recommended layers

### Layer 0 — no phone connection required
Always works:
- clock / RTC
- alarm
- focus / Pomodoro
- countdown timer
- stopwatch / lap
- study log
- D-day / local todo
- NFC
- ambient light

### Layer 1 — Wi-Fi
Recommended for V1:
- NTP time sync
- weather
- local web settings
- OTA update
- optional LAN-side configuration / data export

The HMI acts as a small web server for configuration. Long text input belongs on the phone browser, not on the 4.3-inch screen.

### Layer 2 — BLE / phone bridge
Optional.

The product-facing abstraction is `PhoneBridge`, not a specific mobile OS implementation.

It publishes only:
- connection state
- phone charging/park state if known
- priority notification summary
- call state
- calendar reminder summary

## Why BLE is optional

A generic BLE peripheral cannot automatically read every Android/iOS system notification without platform-specific support.

### Android
Best route if notification forwarding becomes important:
- tiny companion app
- Android NotificationListenerService
- user-defined app/contact allowlist
- forward a sanitized event over BLE or local Wi-Fi

### iPhone
ANCS can support accessory notification access, but pairing/profile handling adds integration work. Treat as a later adapter rather than core V1.

## Focus-mode privacy rule
Default behavior:
- show category + app/contact alias only,
- hide message bodies,
- suppress non-priority notifications,
- never store notification bodies to microSD.

Example:
- `CALL · 엄마`
- `CALENDAR · 15분 뒤 일정`
- `PRIORITY · 선택한 연락처의 새 알림`

Not:
- full chat contents.

## Recommended V1 decision
Build the hardware and study functions first.
Implement the `PhoneBridge` interface now, but enable notification forwarding only after the girlfriend's phone platform is known and the core device is stable.
