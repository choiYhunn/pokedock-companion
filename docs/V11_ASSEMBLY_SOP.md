> **HISTORICAL V11 SOP — use [V14 SOP](V14_ASSEMBLY_SOP.md), [V14 audit](V14_RELEASE_AUDIT.md) and [V14 electrical map](V14_ELECTRICAL_INTERFACE.md) for current 14 Pro landscape 70° hardware. Older 25°/30°/35° phone trial steps are obsolete.**

# PokéDock V11 — From boxes to working gift: assembly SOP

**This is a reproducible procedure, not evidence the physical device was assembled.** Use the milestone gates; stop when a test fails. Most time-consuming work is LVGL/native firmware port, not screwing the stand together.

## Time/budget planning, separated by dependency
- Stage 0 / Prep (before buying): 1–2 evenings to confirm target iPhone 14 variant/case, front display kit configuration, exact charger model, workspace depth, and vendor SDK/recovery files.
- Stage 1 / Bench hardware (after receiving): 1–2 sessions to inspect parts and run *factory* LCD/touch/RTC/SD/audio tests.
- Stage 2 / Mechanical mock (can overlap firmware): 1 afternoon using cardboard/acrylic and adjustable stand; iterate phone angle, cable path, heat.
- Stage 3 / **Native LVGL software** (largest uncertain work): several sessions to several weeks depending on BSP/library mismatches; make usable HOME/Focus first.
- Stage 4 / Final mount and durability: 1–2 sessions after both software and phone charging work separately.
- Stage 5 / Optional NFC/LED and OTA: only after the gift can already function offline.

Time estimates are planning placeholders, not manufacturing quotations or verified execution durations.

## Tools (do not need to buy all)
- 150mm digital caliper, steel rule, angle gauge/cardboard protractor, marker, masking tape.
- Multimeter with correct probe rating, certified board DC supply, phone USB-C PD adapter, insulated pigtails and proper terminal connector.
- Small screwdrivers, nonmetallic spudger, soldering station **only for future optional low-voltage PCB**, heat shrink, cable clips, rubber feet.
- Cardboard or foam board, scissors/craft knife with protective cutting mat, adjustable stand; PETG 3D printing/laser acrylic optional later.
- PC with VS Code/ESP-IDF; a reliable microSD reader, data USB-C, manufacturer factory restore image; smartphone with its normal case.
- Optional contact thermocouple/IR thermometer for repeatable thermal comparison. If not owned, at minimum use a conservative manual heat stop test without asserting numerical temperature accuracy.

## Phase 0 — keep one measurement/test record
Create a paper or local record containing:
- purchased part model, supplier URL, order number (private local only), hardware revision, included audio hardware;
- exact phone model, phone case thickness, charger puck diameter/cable direction, available desk depth;
- date/time, voltage under no-load and on load, factory example version and build logs;
- pictures of front/side/rear and cable exit before attaching anything.

Fill the table in [mechanical engineering](V11_MECHANICAL_DESIGN.md). No drilling or final printing until this is done.

## Phase 1 — electrical safety / factory test, **without** charger nearby
1. **Unpowered:** inspect screen case and contacts for cracks, obvious shorts, reversed terminal labels, stray screws and exposed conductors. Confirm the unit is **4.3C-BOX SKU 33630**, not old 4.3 or B.
2. Download/retain manufacturer factory image, ESP-IDF example, schematic and known working versions. Save USB recovery procedure.
3. Read the *actual* board label and manual DC terminal polarity. Verify regulated supply voltage with DMM before connection. Never try 12V on USB-C or signal header.
4. Connect manufacturer-compatible DC terminal with supply **off**, insulate/strain-relieve wires, then turn on. Observe power indication, unexpected heat/smell; stop if abnormal.
5. Run official LCD/touch test, check corners and swipe/selection stability. Verify RTC time read/write, backup cell orientation, power-off retention. Format microSD as vendor sample recommends; run read test and check hot-removal policy.
6. Test codec speaker path using manufacturer's sample **only if fitted/matched**; confirm volume and silent mode. Avoid ordering a random speaker until port/load specs known.
7. Run 60min basic on-bench operation, note resets, display drops, time drift, supply/board warmth. Gate: pass all before overriding factory example.

## Phase 2 — rear phone stand without electronics modification
1. Use paper template to compare phone at 25°, 30°, 35° (degrees **above tabletop**), with case installed; photograph eye-level view behind HMI.
2. Measure actual iPhone rear coil alignment with the **finished** MagSafe puck. Keep open air/contact face and side cable relief.
3. Cut adjustable side rails or choose a commercial stable stand; add soft replaceable edge stop, rubber contact pads and a *rear* foot for anti-tip.
4. With all power **off**, check phone removal one-handed. No rear sway, interference with HMI terminal/SD/USB, no camera bump pushing phone off charger. Be sure the phone will not fall when magnet is removed.
5. Connect charger to **its own** PD adapter. Run 60min charge test (phone and case combination), repeatedly touch the screen and inspect Wi-Fi stability and thermal trends. If phone becomes unusually hot or charger malfunctions, stop/unplug and revise geometry. Do not bury puck in insulating printed material.
6. Repeat 30 attach/remove motions and a light desk bump test; document whether the phone remains hidden from actual seated viewpoint. Record real footprint measured from front to rearmost support.
7. Only after passing, enter actual measurements into \`cad/pokedock_v11_fit_mock.scad\` to replace sample placeholders. The CAD is a mock, not a structural or print-ready release.

## Phase 3 — firmware first flash / minimum daily utility
1. Start from **working official 4.3C** ESP-IDF LVGL example; pin IDF, LVGL and BSP versions in a reproducible build manifest.
2. Draw static HOME clock + Gengar picture, then touch navigation.
3. Integrate portable \`StudyEngine\` and implement Focus 15/25/45 + 5min rest, generic countdown with no XP, universal Back state.
4. Persist user-entered Todo/D-day/partner and the couple note in versioned NVS/SD, separating keys/asset cache. Use no hard-coded personal message in public source.
5. Test time loss (RTC missing), touch calibration, power cycle 5x, navigation while timer running, quiet mode, accessibility.
6. Gate: 60min stable without Wi-Fi or side electronics. No "working gift" claim until this gate passes.

## Phase 4 — handoff polish
- Add static/few-frame Gengar animation and, optionally, five favorite Pokémon motion cues after profiling memory and touch latency.
- Add final gentle voice/sound option **only if proper speaker installed and mute/volume tested**. Sound import later, not a first-gift blocker.
- Tidy and label **low-voltage** cables, provide strain relief where motion occurs, make HMI reset/USB/SD/speaker access serviceable.
- Recheck MagSafe thermal/phone stability with the 4.3C actually powered and animated for >=60min.
- Photograph any remaining exposed wiring; use a removable, nonconductive back cover that does **not** trap thermal load or block Wi-Fi.

## Phase 5 — optional expansions, strictly ordered
1. Connect ESP32-C3 on isolated low-voltage test setup, confirm stable ESP-NOW link with HMI in its real Wi-Fi configuration.
2. Add PN532 + NFC tag with physical reading; check interferences while MagSafe active.
3. Add BH1750 only if actual need for auto-dimming. Add 4–8 LEDs with rated supply, level shifting and low brightness.
4. Add OTA **after** OTA partition layout fits compiled firmware and failed-update recovery has been tested. USB flashing remains the baseline fallback.

## Acceptance matrix — capture proof, not just "it works"
| Test | Repetitions/period | Pass criterion | Stage |
| --- | --- | --- | --- |
| Panel boot/touch corners | cold start + 4 corners x 5 | No swapped axes or dead points | 1 |
| RTC and backup | 5 disconnect/reconnect cycles | Does not forget date/time with proper cell | 1 |
| SD access | 10 open/read cycles | No corrupted assets or crash on missing card | 1/3 |
| General countdown | 3,5,10min + pause | Correct time; no study credit | 3 |
| Focus and break | 15/25/45 + 5min; background page changes | Exactly-once study credit; zero rest reward | 3 |
| Todo/D-day/private note | 5 power cycles | Fields persist, erase works, not in serial logs | 3 |
| Qi phone charge | >=60min | Stable alignment, expected charging, no excessive heat | 2/4 |
| Docking | 30 cycles | One-hand pickup and replacement, no slip/camera obstruction | 2/4 |
| Gengar animation | 60min | No lag or LVGL memory leak; stops at Night/Focus | 4 |
| Optional sensor/ESP-NOW | >=60min | No false presence claim, no dropped critical UI | 5 |
| Optional OTA | 5 round trips and forced failure | Previous firmware recoverable, user data preserved | 5 |

## Recovery paths
- No LCD: power down; return to manufacturer known-good demo and porting logs.
- No RTC: show explicit "time unsynced", allow offline timer without fabricated absolute time.
- No microSD: static fallback Gengar and core timer still open.
- Magnet/charging unreliable: remove charger from stand and test it separately, do not route power from LCD header.
- C3 unreachable: ignore side module, HOME/Focus remain offline-capable.
- Firmware upgrade fails: if OTA not proven, flash recovery over USB; never overwrite only known-good app in a consumer gift.

## Owner-supplied information pending
Exact phone variant (14/Plus/Pro/Pro Max) and case, measured case size of delivered Waveshare 4.3C-BOX, chosen MagSafe charger and power supply connector, workbench tools, intended screen/phone arrangement and desk rear depth. Do not fill these values with guesses.
