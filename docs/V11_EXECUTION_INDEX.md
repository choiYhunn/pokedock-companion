# PokéDock V14 — current MagSafe-ready manufacturing baseline

**Confirmed:** girlfriend uses **iPhone 14 Pro with MagSafe-compatible case**. Design is **landscape 70° slim rear cradle**, adjustable/removable *finished* MagSafe puck with its own PD adapter. No long portrait ramp or front phone tray. **No hardware purchased/flashed or case/puck fit tested yet**.

1. [V14 physical/industrial design and precise fit gates](V14_MAGSAFE_READY_DESIGN.md)
2. [V14 purchasing list with buy/reuse/defer](V14_PURCHASING_BOM.md)
3. [V14 build/test SOP](V14_ASSEMBLY_SOP.md)
4. [V14 parametric reference CAD](../cad/pokedock_v14_magsafe_ready.scad), [1:1 dry-fit templates](../cad/pokedock_v14_dryfit_templates.scad), and [updated calculator](../design.html)
5. [V14 release blockers and executable build/acceptance audit](V14_RELEASE_AUDIT.md); [vendor-derived electrical map](V14_ELECTRICAL_INTERFACE.md); [new ESP-IDF M0 scaffold](../firmware/hmi/espidf/README.md)
6. [Measurement register](V12_MEASUREMENT_REGISTER.md), [electrical isolation](V11_ELECTRICAL_WIRING.md), [native porting](V10_HARDWARE_PORTING.md)

---

# Archived: PokéDock V13 — compact iPhone 14 Pro re-evaluation (historical; V14 supersedes it)

## V13 historical engineering decision — do not use for new fabrication

1. **[V13 iPhone 14 Pro compact landscape slot; passive vs optional MagSafe](V13_COMPACT_IPHONE_14_PRO.md)** — previous decision baseline; superseded by V14 MagSafe-ready.
2. [Current V12 measurement register, corrected for 14 Pro & real C-BOX dimensions](V12_MEASUREMENT_REGISTER.md)
3. [V12 fabrication component architecture and assembly details](V12_FABRICATION_PLAN.md)
4. [V12 phased purchasing and item criteria](V12_PROCUREMENT.md)
5. [Rebaselined design calculator](../design.html) / **[V13 iPhone 14 Pro compact CAD mock](../cad/pokedock_v13_compact_slot.scad)** (sample clearances; NOT fabrication-ready)
6. [V11 step-by-step safe bring-up](V11_ASSEMBLY_SOP.md), [power separation](V11_ELECTRICAL_WIRING.md) and [ESP-IDF/LVGL port](V10_HARDWARE_PORTING.md)
7. [Progression policy](V11_STUDY_POKEMON_PROGRESS.md), [test acceptance](V10_TEST_ACCEPTANCE.md)

**Decision:** V13 A = passive landscape 65–75° slot (70° first), with optional removable MagSafe as B, both shallow. Old 32° portrait ramp is rejected as the default for desk-space reasons. iPhone model 14 Pro is confirmed; case model still unknown. C-BOX **116.3×79×18mm** dimensions are confirmed in manufacturer cased diagram. Derived footprint remains a sample until fit test.

This index is the **single reading order** for building an actually usable gift, not a promise that the Waveshare MCU product is already completed.

## Historical concept freeze (superseded by the V14 header)
- 4.3" 800×480 LCD = daily **HOME/Focus/Timer**, Gengar default, no overwhelming UI.
- One Poké Ball menu hides Pokémon game/party interactions; romantic private note and planner stay secondary.
- Historical assumption only: iPhone **14-family**, exact model/case pending. **V14 confirmed iPhone 14 Pro + MagSafe case.** Protected MagSafe puck behind display, **separate power**, no front phone tray.
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

Historic parametric fixture (superseded): [V11 OpenSCAD reference mock](../cad/pokedock_v11_fit_mock.scad) — sample dimensions only, not final print STL.
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
