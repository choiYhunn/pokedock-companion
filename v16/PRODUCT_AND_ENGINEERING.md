# Ghost Companion V16 — Product & Engineering Contract
Status: DESIGN + browser interaction implementation; **NOT** physical/production firmware. 2026-10-20.
V14/V15 remain historically preserved. V16 is a new concept until optical, hardware, and finish acceptance.

## User-facing product
- Type: rounded mini hybrid Pepper's Ghost desk clock, NOT regular LCD photo frame.
- Target: 132(W) x 105(D) x 136(H) mm Rev-B planning envelope (base 54 + chamber 82), not final fit, **not a mechanically verified assembly**.
- Main visual: a 3–5 cm apparent animated ghost character floating behind a flat 45-degree beam splitter; round edges are on the OUTER housing only.
- Clock: independent front-facing 1.5-inch grayscale OLED, persistent legibility even if optical content has low contrast.
- Character roster: Gengar (default), Piplup, Togekiss, Lucario, Quagsire. Character names only; art is not bundled.
- Interaction: one encoder/button or capacitive touch candidate; single press next character, long press mode, focus start/stop through a simple settings interface; no faked gesture sensor.
- Use cases: KST clock, 15/25/45 focus, one configurable local alarm, silent character interactions, manually revealed personal message (not bundled in public repo).
- Default muted; 5V USB-certified isolated adapter, no enclosed mains / no custom lithium pack.
- Gift rule: no screen-only/table-order appearance; no cloud dependency for core display; no punitive streaks.

## Provisional architecture
5V USB-C -> FIRST OPTICAL CANDIDATE: Waveshare ESP32-S3-Touch-AMOLED-2.41, 600x450, 800cd/m2 maker-rated; MCU/RTC/TF/QSPI. Board **V1 versus V2 differs in pin mappings**. The 1.43in 466x466, 350cd/m2 part is now SMALLER FALLBACK only; neither is optically validated.
  -> internal upward AMOLED source -> flat beam splitter ~45° -> apparent animation (limited viewing cone)
  -> external I2C SSD1327 1.5inch grayscale 128x128 -> clock, timer, basic settings (connector/pin and pullup verification required)
  -> optional encoder/push-button -> app event queue
  -> OPTIONAL ambient light/proximity sensors AFTER baseline works; I2C address/pin collision & voltage checks needed.
The 2.41-inch source may still be too dim or produce doubled reflections; screen brightness is NOT reflected apparent luminance. The 1.43-inch and 2.1-inch Qualia TFT are alternate candidates, not approved buys. No board purchase approved by this design.

## Renderer contract
- Software pipeline: assets -> decoded frame cache -> character animation state -> composition -> panel driver.
- Character behavior: idle float; enter; hop; dance; spin; peek; pose; celebrate; exit (asset transitions; the simulator uses placeholder vector stand-ins).
- Target 24fps normal animation, 30fps action. These are GOALS, not measured ESP32 output.
- Multiplane animation only when it does not produce fake claims of true volumetric 3D.
- For Pepper's Ghost, an almost-black background is essential; mirror and inversion need real test.
- Separate persistent clock does not steal optical image area; dynamic theme color/clock icon may change by character.
- Content policy: keep copyrighted Pokémon artwork/audio out of public code unless authorized; use a locally supplied private asset pack for a private gift. No automatic scraping or downloaded game ROM assets.
- Adaptive reduced-motion and night brightness controls, default low distraction.

## Software modes
CLOCK -> CHARACTER_EVENT -> CLOCK, CLOCK -> FOCUS (running/paused/completed) -> CLOCK
CLOCK -> ALARM (manual dismiss/mute/snooze target) -> CLOCK; SETTINGS -> manually check/update after confirmation.
App timers use monotonic ticks; RTC/NTP used for wall clock and alarm dedup; NTP failures do not fabricate calendar days.
Future asset packs support new characters and animations separately from application binary when their decoder/API contract is compatible.

## Manual update policy
- NEVER auto-install or auto-check on a schedule. Update is triggered by a physical Settings > Updates action.
- Firmware path: user consent -> HTTPS trusted issuer and release signature/version/board/schema check -> inactive slot -> restart -> display/RTC/UI/storage health -> confirm or rollback.
- Media-only path: user consent -> signed manifest and SHA256 per blob -> staging directory -> atomic pointer flip -> retain old pack and built-in fallback -> validate.
- Neither path is enabled in the prototype. OTA reference code is not a finished safe update service. See OTA_MANUAL.md.

## Acceptance gates, in order
G0 appearance: 1:1 paper/cardboard mock on real desk; off-state looks gift-grade, front clock not industrial.
G1 optics: phone + 45-degree film experiment, record photo at 50/70cm under 150/300/500lux; <=20deg off-axis target. Need recognizable facial expression and stable readable size; if not, no hardware purchase.
G2 sourcing: exact physical panel dimensions, panel direction, I2C pins, touch, RTC backup/power and DC input confirmed from vendor datasheets.
G3 3D geometry: optical plane does not distort; connector/power bend, enclosure strength, accessible USB, print surface, light leakage and dust management.
G4 bring-up: official source panel and OLED examples individually verified; 60-min continuous display run, 30 button actions; characterize brightness and heat.
G5 software: 5 roster, focus monotonic, clock KST offline+NTP, alarm mute/snooze, home reset; frame timings measured on board.
G6 content: user-owned or permitted high quality images; 5x idle+1x enter/exit+2 signature motions, frame budget and memory profiling.
G7 OTA: build dual slots+safe boot/USB rescue; HTTPS and signature checks, invalid image, WiFi/time loss, power interruption and 5 consecutive rollback tests.
G8 gift sign-off: supervised 4h operation, no hot surfaces, no alert surprises, removable private messages, neat finishing, soft feet, packaging.
Gates failing -> fallback: animated screen-only rounded device or clean shadow-art clock, not forced expensive assembly.

## Verified source references
Waveshare preferred optical prototype: https://www.waveshare.com/esp32-s3-touch-amoled-2.41.htm\nV1/V2 board revision warning: https://docs.waveshare.com/ESP32-S3-Touch-AMOLED-2.41\nAlternative compact AMOLED: https://www.waveshare.com/product/esp32-s3-touch-amoled-1.43.htm
Waveshare clock OLED: https://www.waveshare.com/wiki/1.5inch_OLED_Module
Adafruit new Pepper's Ghost project: https://learn.adafruit.com/peppers-ghost-monster-eye
Espressif OTA docs: https://docs.espressif.com/projects/esp-idf/en/v5.5.1/esp32s3/api-reference/system/esp_https_ota.html

## Audit additions 2026-10-21
- Source inventory: [assets/asset_sources.json](assets/asset_sources.json); files are rights-uncleared reference links, not redistributed.
- Portable offline animation GHF1 encoder/decoder added with local Python and C++ tests. Native ESP32 screen streaming still absent.
- Vendor V2 official example contains a legacy I2C driver conflict report; reuse a single compatible I2C bus driver rather than init a second bus.
- Purchasing authority: [PROCUREMENT_CURRENT.md](PROCUREMENT_CURRENT.md) and [VERIFICATION_MATRIX.md](VERIFICATION_MATRIX.md), not historical V15 BOM.
