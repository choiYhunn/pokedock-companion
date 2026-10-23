# PokéDock Master Ball M4 — design lock (2026-10-24)

**Status: PRODUCT REQUIREMENTS LOCKED / FABRICATION & PURCHASE HOLD.**

This supersedes the older M3 centered black-screen and Rev18 Pepper's Ghost hardware concepts as the **chosen gift design**. Keep V10/V17 app history and all previous V16/Rev18 engineering evidence intact.

## Locked user decisions

- Master Ball silhouette: glossy/matte purple upper hemisphere, ivory white bottom, narrow black belt, white M decal, two low rounded pink protrusions; simple cute look, no bright LEDs or gold trim.
- Nominal 138 mm diameter ball, flat anti-roll base. Center button is replaced with a **1.43-inch circular AMOLED** showing an ivory-white default background with a small, actual Pokémon character. It should read as a friendly button when powered on, not a pasted black smart watch.
- Primary Gengar #94; Piplup #393, Togekiss #468, Lucario #448, Quagsire #195, Togepi #175, Pachirisu #417, Jirachi #385. Do not fabricate generic look-alike ghost artwork in place of the actual Pokémon.
- Core device functions: near-view clock/date, tap reactions, 15/25/45 focus timer, once-daily alarm + snooze, battery status, dim/sleep screen policy, private message Easter egg.
- Battery: standard Waveshare **ESP32-S3-Touch-AMOLED-1.43 WITHOUT CASE**, onboard charging, protected 1S 3.7V LiPo (capacity candidate 1000–1500mAh subject to safety/polarity/space approval), USB-C power via rear service opening. The standard board has no built-in speaker amplifier; propose a verified low-current 3.3V active piezo circuit driven by NPN + GPIO18, not a USB_5V-only buzzer.
- V17 native Android/iOS companion controls Pokémon, alarm, focus, brightness, time sync and messages via authenticated BLE. Preserve existing V17 mobile UX and repository history. The user reports a locally created APK; the connected computer is offline and this session did NOT read/modify or install that APK.
- 4-color modular FDM shell to avoid expensive multi-color paint: purple upper, ivory lower, black belt, pink lobes; white M vinyl. No MagSafe, no hologram, no second OLED clock.

## Fixed/reference information

- Manufacturer: https://www.waveshare.com/product/esp32-s3-touch-amoled-1.43.htm
- 466x466 AMOLED, approximately 36.75mm circular active area, vendor nominal max 350nit, touch, RTC, microSD, Wi-Fi/BLE and onboard LiPo charging. Display QSPI 9–14, reset21, enable42, touch I2C47/48; GPIO4 BAT_ADC. Standard board, **not 1.43C, not metal case 1.43-B**.
- CAD *target*: 138 mm outside diameter, 2.8 mm printed wall, bezel 60 mm OD, aperture 38 mm; only a geometrical reference with 0.625 mm **nominal** radial aperture-to-active-screen clearance.
- Working planning BOM with four-color FDM printing and contingency ~KRW142,000–325,000 (not actual supplier checkout/landed cost).

## Executed audit from independent conversation artifact

M4 engineering ZIP generated in current ChatGPT conversation named `PokeDock_MasterBall_M4_DesignLock_Simulation_20261024.zip` (NOT uploaded as a repo binary).
Contains parametric OpenSCAD source, **9 watertight provisional STL parts**, CAD parameters, white M decal, 3.3V piezo/battery wiring plan, host-tested C++ state logic, browser-interactive bright-button UI, BLE Capacitor 7 integration **sample**, BOM, RFQ, QA matrix, and screenshots. Host C++ state tests passed, HTML core controls exercised in headless Chromium using set_content; remotely loaded Pokémon images were unavailable in the test environment. These are NOT hardware verification.

## Manufacture / order blockers (DO NOT BUY OR PRINT AS FINAL)

1. Exact vendor STANDARD BOARD STEP (not B/C variant), component heights/antenna/USB/TF connector and connector orientation not obtained in this environment. Provisional STL contains a 46mm board envelope but no certified safe glass/PCB clamping surface.
2. Shell joining bosses/screws, actual rear service hatch closure, pink-lobe retention, battery tray fastening and USB-C panel-fit not finalized. **Watertight STL != print-and-assemble-ready**.
3. Battery part number, polarity, actual size, charger current/temperature, protection, 3V3 availability during discharge, buzzer power/charging heat and safety cannot be certified by software simulation.
4. Real 466×466 Waveshare BSP integration + firmware flashing, RTC persistence, charging/battery runtime, secure BLE GATT peripheral & end-to-end app connection, and actual character animation pack all remain untested or unimplemented.
5. Full slicing/fit/tolerance worst-case, professional exterior finish, real on-desk viewing, power cycles and independent vendor signoff remain outstanding; user wishes to avoid prototype testing, which necessarily leaves residual physical risk.

**Decision:** the product direction is final; the production release is NOT. Avoid claiming end-to-end manufacturing or signed native apps from conceptual assets. Do not add scheduled GitHub Actions, OTA, automated purchases or new hosting workflows.
