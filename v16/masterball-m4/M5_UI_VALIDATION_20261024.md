# PokéDock M5 — readable button UI audit (2026-10-24)

**Design direction unchanged:** M4 Master Ball 138mm, center standard Waveshare 1.43-inch 466×466 AMOLED, ivory/white background when powered on, pink lobes, white M logo, rechargeable 1S LiPo candidate, eight true Pokémon (subject to artwork permissions), BLE companion app V17. No return to hologram/top-screen concepts.

## What changed in M5

The prior M4 simulator showed the timer principally in the outer desktop settings panel, not as large digits in the actual circular device UI. M5 switches the 466px diameter UI by state:

- **Idle:** large 88px clock + 300×243px Pokémon picture region + name. Different Pokémon selected by their National Dex IDs.
- **Focus:** **121px remaining-time digits inside the circular screen**, progress arc, reduced 118×105px Pokémon picture region. 25:00 → 24:59, pause/resume/reset; 15/25/45/60 minute presets.
- **Alarm:** large 96px digits, separate dismiss and simulated five-minute snooze touch zones.
- **Power:** larger battery status, distinct low-light/OFF preview.
- True artwork is NOT included in public repo: private local GIF loader first, then online PokeAPI reference, clearly marked emoji fallback if absent. Do not call fallback “Gengar art.”
- Physical font em heights based on 36.75mm/466: idle 88px→6.94mm, focus 121px→9.54mm. Real font cap height less, visibility at desk distance still unverified.
- AMOLED becomes black when powered OFF; ivory is only a powered-on appearance. Always-on white screen risks higher power/burn-in; dim/sleep policy planned.

## Executed host tests (from the current ChatGPT artifact)

A separate downloadable **M5 review package** contains the upgraded interactive HTML, Chromium screenshots, tests, numeric report, and archived M4 source. It is not yet committed as a public repository binary.

- Chromium Playwright: **25 PASS checks** (timer numbers in actual round screen, elapsed updates, freeze/resume, alarm snooze/dismiss, battery/off mode, 8 partner selection, mobile width), page JS exceptions none. Browser administrator blocked real http/file navigation, so page rendered with set_content; persistent local storage across reload not validated.
- C++17 host state logic under AddressSanitizer/UBSan: **50 PASS assertions** (monotonic timer, midnight and day rollover, no belated alarms, five-minute snooze, bounds).
- Host-only BLE JSON/ACK codec: **22 PASS assertions**. This is not connected BLE.
- Nine prior M4 CAD/STL parts independently read by trimesh, **9/9 watertight**. This does not certify assembled product.

## Newly explicit manufacture defects — **DO NOT ORDER**

1. Manufacturer standard-board STEP and connector/cable keep-outs not registered to CAD; official resource link: https://files.waveshare.com/wiki/ESP32-S3-Touch-AMOLED-1.43/ESP32-S3-Touch-AMOLED-1.43-3DFile.zip . The download is listed in official Waveshare Resources but was unavailable to this execution environment.
2. Old M4 battery tray is **67mm wide**, rear service aperture **58mm**: face-on insertion cannot occur; an angled insertion path was never verified. Redesign service architecture.
3. The bezel through aperture is Ø38mm for a nominal Ø36.75mm active OLED, only 0.625mm nominal radial difference. Glare/dark ring, centering and glass preload risks; final tolerance drawing missing.
4. Upper/lower fastener bosses, hatch screw/latch and pink-lobe retainers not completed. Nine watertight STLs alone are not print-ready.
5. Actual battery part number, connector polarity, charger thermal behavior, separate RTC backup and protected-cell compatibility not verified. No simulation can guarantee safe LiPo charging.
6. ESP-IDF vendor BSP hardware build/flash, display/microSD FPS, RTC backup, power cycling, real buzzer and encrypted GATT server, signed Android/iOS BLE interoperation **NOT COMPLETE**. User's remote notebook currently offline, and no live hardware connected.
7. Final licensed/private eight Pokémon animation pack and actual motion frame quality not included.

Official Waveshare: https://docs.waveshare.com/ESP32-S3-Touch-AMOLED-1.43 ; ESP-IDF example requires version 5.3.1+.

**Status:** product concept LOCKED; M5 UI host verification PASS; CAD mesh geometry PASS; **fabrication and complete electronics purchase HOLD**. No new GitHub Actions, scheduled workflow, OTA, or automatic purchase.
