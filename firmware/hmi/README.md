# HMI implementation path

Use the official Waveshare ESP32-S3-Touch-LCD-4.3C example / BSP as the hardware layer.

Recommended:
- ESP-IDF 5.5
- Waveshare managed BSP `waveshare/esp32_s3_touch_lcd_4_3c`
- LVGL 9.x per current BSP direction

Do NOT rewrite:
- RGB panel init
- GT911 touch
- RTC driver
- audio codec init
- SD init

Add:
- ESP-NOW receiver task
- `app_state.h`
- UI screens corresponding to `prototype/ui_v2.html`
- SD artwork loader
- config JSON parser
- birthday/date engine

Important:
The generated HMI code here is a product/application scaffold, not a hardware-validated binary.
The exact BSP API should be locked to the board revision once the physical unit arrives.