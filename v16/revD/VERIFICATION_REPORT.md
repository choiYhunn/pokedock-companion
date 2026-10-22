# Rev D complete pre-purchase technical status

As of 2026-10-22 this work is **not ready for whole-basket payment**. It is the most detailed pre-procurement engineering simulation available without an actual device in hand. A zipped full independent host-test kit was also created for the current conversation.

Hardware selection:
- Waveshare bare 2.41in AMOLED V2 Rev2.0, factory QSPI GPIO9-14, I2C47/48, touch interrupt GPIO3. Vendor explicitly says V1/V2 are not interchangeable.
- WHITE Waveshare 2.42in SSD1309 128x64 default SPI module 61.5x39.5mm, active 55.01x27.49mm; manufacturer's MX1.25 7PIN cable is included. Existing Rev C front wide clock choice remains.
- Clock SPI GPIO38/39/40/41/42 and encoder GPIO7/8/1 are **candidates only** pending exact V2 physical header/pinout. GPIO43 active buzzer is blocked by UART0 TX unless rerouted. Clock adapter is mocked in host tests, not flashed.
- Beam splitter changed from 64x70mm to 82x88mm, flat 45deg, center front offset -7mm. Clear outer enclosure target 104x91x82mm; 132x105x54mm rounded base. PCB mounting hole fit, canopies, external optical grade and USB relief still not finished.
- Expensive teleprompter first-surface beamsplitter optical grade might cost more than budget; **a cheap clear acrylic cutout is not an equivalent high-quality substitute**.

Executed host test observations:
- Ideal 3D geometry, 18 view scenarios (500/700mm distance, 240/300/360mm eye height, yaw ±10deg, 11x11 display sample rays): Rev C ~56.5% average ray coverage; Rev D ~84.9%, low sample ~54.5%. Target front 600mm, eye 300mm ~90.9%. NO luminance or real face legibility simulated.
- Geometry plate clearances for Rev D 104x91 canopy, assuming unconstrained theoretical plane: front 7.39mm, rear 21.39mm, top 10.89mm, bottom 8.89mm, each side 11mm, BEFORE actual cover wall, mounting frame, tolerance.
- OpenSCAD Rev D base single watertight mesh 132x105x54mm and 110.89 cm3 CAD volume; optical rail components watertight. **No physical dry fit or manufacturer-approved STL**.
- Host C++17 -Werror + ASAN/UBSAN portable integration test passed: focus, pause, countdown, repeating alarm, snooze over month end, simultaneous focus+alarm, update gate, front OLED fake SPI sink writing 1024 display bytes. No real ESP32 firmware/RTC/OLED/OTA.
- Offline JavaScript browser simulator handlers tested under a stubbed DOM/VM: original 54.5% at example view, new 90.9%, sliders, ON/OFF and action. Chromium/Playwright direct browser navigation was rejected by the container's administrator policy; NOT passed as visual browser automation.
- Synthetic 5-generic-avatar×36-frame 256x256 compression experiment: 180 frames ~0.54MiB, average 3138 compressed bytes; two raw RGB565+alpha frames ~384KiB of PSRAM. Highly compressible test data, not actual premium Pokemon art performance.
- Exact Woo/price basket unavailable. Model BOM low 234,000 KRW high 483,000 KRW (this includes finish/optical customisation/one remake, and is NOT a supplier checkout). Buying all once without measured custom clear canopy/coated reflector is not a reliable no-rework plan.

Native board firmware status:
Current V16 device entry point still remains console-only. The portable Host Runtime and SSD1309 display protocol can be adapted into the official V2 hardware example at https://github.com/waveshareteam/ESP32-S3-Touch-AMOLED-2.41-V2 but have NOT been cross-compiled with its old LVGL/ESP-IDF source in this environment. No OTA signature/rollback, real sound driver or secure asset A/B installer exists on device. All manual OTA functions remain disabled by default.

Do not merge a visually nice rendered product concept into a purchase order without 1:1 optical test and a physical assembled proof. Device-ready means actual purchased board and panels run code from USB/OTA and can recover from interrupted update, not merely host source lint success.
