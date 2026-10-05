# Architecture

```text
                       ┌─────────────────────────────────┐
                       │         HMI NODE                │
                       │ ESP32-S3-Touch-LCD-4.3C-BOX     │
                       │                                 │
                       │ LVGL / 800x480 Touch            │
                       │ RTC / SD / Audio                │
                       │ State Engine / Dex / Timer      │
                       │ Birthday Script                 │
                       └──────────────┬──────────────────┘
                                      │
                               ESP-NOW 2.4 GHz
                           heartbeat + event packet
                                      │
                       ┌──────────────▼──────────────────┐
                       │         DOCK NODE               │
                       │        ESP32-C3                 │
                       │                                 │
                       │ I2C: PN532 / VL53L0X / BH1750   │
                       │ GPIO: WS2812/SK6812             │
                       └──────┬────────┬────────┬────────┘
                              │        │        │
                             NFC     Phone     Room
                                     Presence   Lux

               ┌─────────────────────────────────────┐
               │  Qi charging pad — independent     │
               │  no firmware dependency            │
               └─────────────────────────────────────┘
```

## 왜 2 MCU인가?
Waveshare HMI 내부 control device가 I2C 0x24를 사용하고, PN532도 I2C에서 0x24를 사용한다.
Dock 센서를 C3에 분리하면:
- address collision 회피
- HMI display BSP 수정 최소화
- 센서 문제로 화면 bring-up이 깨지는 것 방지
- 하부 dock만 별도로 bench test 가능
- LED timing / sensor polling이 GUI frame rate에 영향 주지 않음

## Event priority
1. alarm / critical UI
2. birthday
3. NFC override
4. focus timer
5. phone dock
6. night / dark
7. morning/evening
8. idle/random encounter

## graceful degradation
- Dock node 죽음 → clock/timer/Dex still usable
- microSD 없음 → built-in fallback background + text UI
- Wi-Fi 없음 → RTC continues
- NFC 없음 → touch UI still works
- Qi charger failure → unrelated to MCU operation

## Mechanical implementation
3D printing is not a firmware dependency. A commercial display stand and externally mounted Qi pad are fully supported and are the preferred fallback for a one-day build.