# PokéDock ESP-IDF M0 project scaffold — NOT flashed / NOT compiled in repository

This directory makes the portable core discoverable to an ESP-IDF application build. **It is a console-only starting point**, not an LCD demo and not the V10 HTML simulator running on an ESP32.

- Board intended: Waveshare 4.3C-BOX SKU **33630**, 16MB flash / 8MB PSRAM, USB-C download/debug and separate manufacturer-specified DC power.
- Candidate deps: ESP-IDF 5.5.x and `waveshare/esp32_s3_touch_lcd_4_3c@3.0.1`; versions must be reconciled with official demo + actual PCB revision. Do **not** mix vendor's local LVGL v8 examples and managed LVGL v9 BSP blindly.
- The current `main/app_main.cpp` only imports `StudyEngine` and emits a warning on boot. It does not run GUI, start timers, persist data or connect peripherals.
- No board has been connected here and no `idf.py build` or `idf.py flash` results are claimed. Do not flash over a factory image until a backup/recovery method is verified.

## Windows development / build attempt

1. Save the verified Waveshare factory firmware + official vendor sample sources and commit ID before replacing them.
2. In VS Code ESP-IDF terminal with ESP-IDF 5.5.x installed, open `firmware/hmi/espidf` (not parent `firmware/hmi`).
3. `idf.py set-target esp32s3`.
4. `idf.py menuconfig`: verify 16MB flash and correct PSRAM settings from the matching vendor example. This repository has no locked hardware `sdkconfig.defaults` yet.
5. `idf.py build`. Capture full output, exact IDF version, dependency lock and binary size. Fix BSP version conflicts rather than editing GPIO pin values ad hoc.
6. With board's **certified power already verified**, use vendor-approved `idf.py -p COMx flash monitor` and retain physical BOOT/RST/USB recovery access.

## Next integration order (separate gated commits)

1. **M0a**: official Waveshare `examples/esp-idf/03_lcd` + `06_touch`, `02_rtc`, `05_sd`, `12_lvgl_transplant` / `13_lvgl_codec` cloned **at one recorded vendor SHA**, factory smoke test.
2. **M1**: compatible BSP LCD+GT911 touch/800x480 LVGL task, static HOME with clock and optional simple generated Gengar placeholder (licensed assets later).
3. **M2**: Focus and 5-minute rest via portable `StudyEngine`; general countdown no study credit; NVS versioned exactly-once session IDs.
4. **M3**: RTC PCF85063A + NTP (separate monotonic Focus timer); microSD with built-in fallback; USB recovery.
5. **M4**: local animations and accessible Night mode; speaker only if delivered wiring/impedance is verified; OTA/rollback last.

References: [production blockers](../../../docs/V14_RELEASE_AUDIT.md), [vendor BSP notes](../../../docs/V10_HARDWARE_PORTING.md), [Waveshare C official](https://github.com/waveshareteam/ESP32-S3-Touch-LCD-4.3C), [study engine](../core/study_engine.cpp).
