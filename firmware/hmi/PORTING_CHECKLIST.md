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
