# HMI firmware architecture

## Platform
Target:
- Waveshare ESP32-S3-Touch-LCD-4.3C-BOX
- ESP-IDF + official Waveshare BSP / examples
- LVGL for UI

Do not rewrite display/touch/audio/RTC drivers unless required.

## Layers

```text
LVGL screens
  ↓
UI state / overlays
  ↓
StudyEngine ──────────────┐
Todo / D-day              │
Alarm                     │
Weather                   │
PhoneBridge abstraction   │
  ↓                       │
Persistence / NVS / SD ←──┘
  ↓
ESP-IDF services

Dock ESP-NOW adapter
  ↓
ESP32-C3 sensors / NFC / LED
```

## Core rule
Timer/study logic must not depend on LVGL frame rate or Wi-Fi.

All engines receive monotonic `now_ms` and are testable without the Waveshare board.

## Phone bridge
`PhoneBridge` is optional and disabled by default.
Android/iOS-specific adapters plug into the same interface later.

## UI tabs
- HOME
- FOCUS
- TIMER
- STOPWATCH
- TODAY
- DEX
- SETTINGS

Text-heavy editing is done through the local web page rather than the HMI keyboard.
