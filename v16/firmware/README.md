# Ghost Companion V16 — firmware integration status
This directory contains **portable clock/timer/alarm logic** and an intentionally OFF-by-default **ESP-IDF manual OTA reference module**. It is NOT a full flashed application. The ESP32-S3 AMOLED, SSD1327, button/encoder, RTC, flash partitions, audio output, and Wi-Fi credentials still need manufacturer-specific driver integrations and physical validation.

## Host test
From repository root: bash v16/scripts/test_host.sh
Compiles v16/firmware/ghost_core_test.cpp with strict C++17 warnings and executes simulator state tests (Node).

## Board bring-up path
1. Buy nothing until real Pepper's Ghost contrast/scale is tested.
2. Verify actual board PCB variant, manufacturer demo, display QSPI, touch controller, RTC, PSRAM, I2C available connector pins, and SSD1327 power/level.
3. Copy vendor ESP-IDF startup/BSP into a NEW verified v16 build, do not reuse 4.3C vendor BSP.
4. Bind GhostCore monotonic tick, RTC/NTP clock, display frame cache, front OLED render, physical encoder, mute and alarm speaker.
5. Create actual verified app partitions and signed-update channel before enabling OTA.
6. Test sleep/wake, focus interrupted by reboot, alarm cut off on power loss, 4h thermal, unsafe reflection, viewing angle and five rollback cycles.

## Explicit exclusions
The browser preview's artwork is generic vector stand-ins; it isn't proof of real Pokémon animation, the physical image brightness, or production-quality UI. Nothing here flashes or deploys to a device. The older V15 hardware and output cannot be reused without redesign.
