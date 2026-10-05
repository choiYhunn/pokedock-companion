# Vendor baseline — Waveshare 4.3C

Checked: 2026-10-05.

## Board
Target:
- Waveshare ESP32-S3-Touch-LCD-4.3C-BOX
- SKU 33630
- ESP32-S3R8
- 16 MB flash
- 8 MB PSRAM
- 800×480 GT911 touch
- PCF85063A RTC
- microSD
- ES8311 speaker codec / ES7210 microphone ADC
- 2.4 GHz Wi-Fi + BLE 5

## First-party repository
Use Waveshare's product repository as the hardware bring-up reference:
`waveshareteam/ESP32-S3-Touch-LCD-4.3C`.

Useful ESP-IDF examples:
- 02_rtc
- 05_sd
- 08_wifi_scan
- 09_wifi_sta
- 10_wifi_ap
- 11_speaker_microphone
- 12_lvgl_transplant
- 14_udp_tcp_ntp

Do not combine all examples at once. Bring up the board in this order:
1. display/touch
2. RTC
3. SD
4. Wi-Fi
5. NTP
6. audio
7. application UI

## Managed BSP
Current published direction:
- component: `waveshare/esp32_s3_touch_lcd_4_3c`
- version: `3.0.1`
- target: esp32s3
- ESP-IDF: 5.3+
- current dependency direction uses LVGL 9.4.

For PokéDock, pin the dependency rather than pulling an unbounded latest version.

## Hardware caution
Waveshare's current component notes an IO-expander naming/revision caveat and local protocol use of I2C address 0x24.

This reinforces the PokéDock decision: PN532 stays on the separate ESP32-C3 Dock Node, not on the HMI I2C bus.

## Framework policy
- Initial target: ESP-IDF 5.5.x family.
- Do not jump to a new major IDF/LVGL version during birthday bring-up.
- Upgrade only after a known-good tagged PokéDock build exists.
