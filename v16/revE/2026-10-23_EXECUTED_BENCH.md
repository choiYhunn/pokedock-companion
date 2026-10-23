# V16 Rev E — 2026-10-23 executed asset and price experiments

**Decision: HOST SOFTWARE PASS / ONE-SHOT HARDWARE CHECKOUT NO-GO.**
Rev D remains the optical engineering basis, pending a cheap stock-cover 100×100×100mm variation. Do **not** purchase complete kit on the strength of host tests. This report accompanies an archive delivered in the user's conversation; the archive contains more generated binaries than this public repository.

## Executed in local container (not simulated results invented)
- Existing Rev D suite: Python optical tests, C++17/ASAN/UBSAN timer+alarm state core, fake 128×64 SSD1309 SPI, OpenSCAD watertight base, static GPIO pin collision, Node browser VM all pass.
- NEW original NON-POKÉMON character animation test pack: 5 types × 48 frames = **240 frames**, authored 256×256 RGBA at intended 24fps. Five animated WebP files each retain 48 frames and background transparency. These are simple stand-ins, **not premium Gengar/Piplup/Togekiss/Lucario/Quagsire game-like animation**.
- NEW GHF1 codec: all 240 generated frames encode/decode in Python, total **2,983,326 bytes (2.845MiB)**. Average ~12.43KiB/frame. C++17 ASAN/UBSAN decoder reads 240/240 with explicit alpha mask, checks opaque RGB565 black vs transparent, rejects truncated frames. Host mean decode ~3.7–4.4ms/frame, NOT ESP32 runtime.
- For 256², one decoded RGB565+8-bit alpha frame =196,608 bytes; double buffer =393,216B (384KiB). 600×450 RGB565 framebuffer =540,000B. Storage fits model 8MB PSRAM at first order; SD/QSPI bandwidth real validation remains required.
- NEW actual Chromium test through Playwright with content injection: switch 5 characters and dial, power ON/OFF, focus start/pause/reset, mobile & desktop screenshots; no page errors. No assertion that a floating optical image will look like web preview.
- NEW 100×100×100mm off-the-shelf transparent box variation. Model assumes 2mm wall =96mm usable width/depth; 82×88mm beam splitter + prior rails are near-fit. In ideal 18-view ray geometry, this retains RevD average 84.85%, minimum 54.55% (NOT real optical measured). Cover raises estimated product height from 136mm to ~154mm; internal rounded corners and fasteners unknown.
- NEW printable stock-cover BASE-only OpenSCAD envelope: 132×105×54mm, 111.02cm³, watertight. It is **not** final assembled geometry (USB clearance/real holes/rails/pressure and glass safety not done).

## Date-stamped price discovery — NO actual cart
- Exact Waveshare ESP32-S3-Touch-AMOLED-2.41 bare V2 catalog **$49.99–53.99** (version option dependent), refer to official maker V2 pin docs.
- Exact Waveshare 2.42inch WHITE SSD1309 OLED **$12.99**, default SPI, active 55.01×27.49mm.
- USD/KRW ~1,325 on 2026-10-23: 49.99×1325≈₩66,237, 12.99×1325≈₩17,212, **two parts ~₩83,449 before import freight/tax/card fee**.
- Stock clear full case 100³ observed search product ~₩5,500, **size/stock/internal dimensions not verified**.
- 3DFARM PLA 100cm³ **₩34,000 example only** (PETG higher; slicer-specific quote not obtained).
- Genuine 70T30R beam-splitter plate local 82×88mm price/stock **not verified**. Ordinary acrylic is not a coated beam splitter. Custom chamber also unquoted.
- **Scenario cost planning:** low ₩171,949, target ₩260,749, high ₩461,000; these sum lower/target/upper line estimates including allowances and optional reused parts, NOT checkout shipping-confirmed prices or market universal minima.

## Hardware/firmware missing and strict no-go
Actual V2 RM690B0 panel build, 2.42 SSD1309 actual SPI, RTC/NTP cold recovery, GPIO available on header and solder state, microSD GHF on-board decode throughput, optical luminance/ghost double images at 150/300/500lux, complete assembly mounting/cable length, safe manual signed OTA+asset A/B rollback, private Pokémon animation rights & quality, final outside vendor quotes.

**Next sign-off:** written supplier V2 and connectors, 82×88 coated beam splitter and stock cover actual usable interior dims, merged 3D fit and supplier one-off assembled price. Until all signed, DO NOT send a user one-click shopping basket or promise drop-in complete assembly.

Source references:
https://docs.waveshare.com/ESP32-S3-Touch-AMOLED-2.41
https://www.waveshare.com/esp32-s3-touch-amoled-2.41.htm
https://www.waveshare.com/product/ai/2.42inch-oled-module.htm
https://3dfarm.co.kr/3d-printing-price/
