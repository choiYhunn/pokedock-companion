# PokéDock V11 — Master fabrication handoff

This index is the **single reading order** for building an actually usable gift, not a promise that the Waveshare MCU product is already completed.

## Concept freeze
- 4.3" 800×480 LCD = daily **HOME/Focus/Timer**, Gengar default, no overwhelming UI.
- One Poké Ball menu hides Pokémon game/party interactions; romantic private note and planner stay secondary.
- iPhone **14-family**, exact model/case pending. Protected MagSafe puck behind display, **separate power**, no front phone tray.
- Rear phone support geometry **not yet physically validated**; old V4 78mm total depth is not a real build fit.
- C3/NFC/ambient light are optional second-stage modules; avoid blocking the gift waiting for these.
- Focus-to-Pokémon is cumulative minutes, no artificial reward for regular countdown or 5-minute breaks.
- Pokémon cry/music alarm + OTA + iPhone BLE ANCS are future work, not promised ready features.

## Official mechanical source

Waveshare publishes **2D DXF / 3D STEP** for ESP32-S3-Touch-LCD-4.3C in [hardware/dimensions](https://github.com/waveshareteam/ESP32-S3-Touch-LCD-4.3C/tree/main/hardware/dimensions). These are a better reference for the actual board than freehand guessed screen geometry; they still may not represent the **plastic external C-BOX SKU 33630** exactly. Measure the physical case, port cutouts and screw sites before applying any model to it.

## Source-of-truth documents, recommended sequence
1. [Mechanical dimension & geometry](V11_MECHANICAL_DESIGN.md) — why low-angle rear stand occupies desk depth, all physical measurement fields, 25/30/35-degree tests.
2. [Electrical/power & later audio](V11_ELECTRICAL_WIRING.md) — exact 4.3C board power vs MagSafe, connector check and optional C3/LED wiring rules.
3. [Buy in two phases](V10_BOM_AND_PURCHASE.md) — materials, quantities, verified vendors and explicit deferred items.
4. [Assembly SOP](V11_ASSEMBLY_SOP.md) — initial inspection, factory bring-up, phone fit jig, native firmware, final system test.
5. [ESP-IDF/LVGL port](V10_HARDWARE_PORTING.md) — official example baseline, portable C++ integration, native UI, NVS/RTC, OTA only after working build.
6. [Study/level progression](V11_STUDY_POKEMON_PROGRESS.md) — 1h/2h/5h/10h/20h milestones, deterministic verified minute accounting and no grind.
7. [V10 acceptance tests](V10_TEST_ACCEPTANCE.md) — web mock tests already checked vs device/power tests still pending.
8. [Future OTA](../firmware/hmi/ota/README.md) — dual slots and rollback **proposal**, not running on device.

Parametric design fixture: [V11 OpenSCAD reference mock](../cad/pokedock_v11_fit_mock.scad) — sample dimensions only, not final print STL.
Current web prototype: https://choiyhunn.github.io/pokedock-companion/simulator.html?v=10

## Decision gates and next action
| Stage | Spend now? | Exact result to demonstrate before proceeding |
| --- | --- | --- |
| G0: measure/scope | No | exact iPhone/case, chosen MagSafe puck, bench desk dimensions, supplier choice |
| G1: Phase-A purchase | Yes, after G0 | verified Waveshare C-BOX and proper DC adapter, PD puck+adapter, SD/RTC cell and adjustable stand |
| G2: vendor firmware | Already purchased | LCD+touch+RTC+SD+audio path (if fitted) pass 1h |
| G3: charger/stand | No printed housing yet | real phone fits and charges 60min, one-hand 30 dock/undock |
| G4: native functionality | Engineering effort | real LVGL HOME, monotonic Focus and generic timer, Back, persistent settings |
| G5: cosmetic/partner | Engineering effort | animations bounded and offline, reduced-motion and night safe |
| G6: optional sensor/OTA | Separate later buy | no regresion in core function, proven recovery |

## Estimated build shape (not an order or shipping promise)
- One S3 screen/base + rear support + independent protected magnetic charger can deliver most daily value.
- Optional C3/NFC/LED add parts, power and debugging complexity; build after minimum gift is usable.
- Acoustic alarms require speaker + codec driver and sound assets. Provide basic offline beep first, custom audio once verified.

## What is complete vs missing
- DONE: V10 browser navigation/Focus/ToDo and V9 character-select prototype, portable study/motion/reward policy scaffold, V11 measured-fit CAD guide, build documentation, deterministic growth policy.
- NOT DONE: actual board purchase, actual case measurements, phone charger fit, prototype build, factory firmware smoke, native LVGL port/flash, real NVS data store, actual audio import, optional radio bridge, OTA.
- This project is a **personal non-commercial fan gift** and remains unaffiliated with Pokémon. Artwork used in the web simulator does not automatically grant redistribution rights for firmware/asset downloads.
