# PokéDock Companion V14 — single production execution index (2026-10-19)

> **Start here:** [actual budget/buy-now instructions](V14_BUY_NOW_AND_OWNER_ACTIONS.md) · [two-domain wiring SVG](../hardware/v14_wiring_topology.svg) · [harness SOP](V14_WIRING_HARNESS_BUILD.md).

## Product definition and non-goals
**One gift:** a compact, quiet 800×480 Gengar desk companion, with a cased Waveshare ESP32-S3-Touch-LCD-4.3C-BOX **SKU 33630** HMI facing front, a removable iPhone **14 Pro** in landscape at about **70°** behind it, and a detachable **finished** Apple MagSafe puck on **independent USB-C PD**. Confirmed MagSafe-compatible everyday case. Keep a padded *passive* phone ledge functional without wireless charging. No front trays, portrait ramps, giant rear pedestal, exposed mains, battery pack, extra MCU or RGB as baseline.

**MVP acceptance, not merely source-complete:** clock/time+NTP/RTC holdover, working physical 800×480 touchscreen, Focus 15/25/45 + 5-min rest, plain timer without XP, simple agenda/DDay/erasable couple note, quiet Gengar image/animation local/offline, safe power, serviceable case, 30 undock cycles, 60min charging test if MagSafe fitted, 4h unattended *supervised* bench soak. Avoid making smart charging/ble/ANCS/Pokémon sound promises.

## Source of truth
- Current hardware: [V14 design](V14_MAGSAFE_READY_DESIGN.md), [release audit](V14_RELEASE_AUDIT.md), [mechanical manufacturing](V14_MANUFACTURING_INTERFACE.md), [electrical mapping](V14_ELECTRICAL_INTERFACE.md), [BOM](V14_PURCHASE_AND_BUDGET.md), [SOP](V14_ASSEMBLY_SOP.md).
- Firmware: [ESP-IDF console skeleton](../firmware/hmi/espidf/README.md), [native port plan](V14_FIRMWARE_ROADMAP.md), [portable C++ core](../firmware/hmi/core), [QA](V14_TEST_PROTOCOL.md).
- Demo: [V10 browser simulator](../simulator.html) is not the physical device.
- Legacy V2–V13 design, old purchase lists and portrait angle calculators are **archive reference only**.
- Do not put private birthday/date/letter/personally identifying content in public repo, images or serial diagnostics.

## Work breakdown structure (WBS)
| ID | Deliverable and owner | Input | Exit evidence | Blocker |
| --- | --- | --- | --- | --- |
| P0 | Purchase/facts freeze, owner: builder | exact SKU 33630; user 14 Pro & case | BOM vendor quote, no substitute product | wrong board variant |
| M0 | Physical measurements | physical phone/case/charger, cased HMI | filled measurement register, calibrated 1:1 mock | camera, mount insert, cable dimensions |
| E0 | Vendor electrical bring-up | source/manual, approved DC adapter | DMM polarity, screen/touch, RTC, SD, 60min operation | uncertain power polarity |
| F0 | Native IDF bootable LCD | exact Waveshare demo/IDF/BSP | clean build+flash+recover, touch four corners | no board/IDF lock |
| M1 | Passive mechanical proof | M0 + HMI+case | 65/70/75 photos and 30 one-handed insert/removes | sliding/tipping/camera interference |
| F1 | Utility-native screens | F0 + C++ StudyEngine | HOME/FOCUS/TIMER/MENU and 5 rest runs | web-only UI |
| F2 | Persistence / progress | F1 + RTC/NVS| unique session credit, power-fault injection | no transactional NVS |
| M2 | Optional MagSafe snap-on | M1 + measured puck + PD | 60min stable charging with HMI; easy removal | heat, alignment, depth |
| M3 | Manufacturing release | M1 & optionally M2 | CAD interference, prototype, drawings, 4 rubber feet | OEM fastener unknown |
| F3 | Local assets / polish | F2 + licensed assets | SD-missing fallback, night/reduced motion, safe note erase | copyright / too much RAM |
| Q0 | Gift release inspection | M3, E0, F3 | signed test logs/photos, USB rescue, 4h thermal/interactive soak | any safety/critical core fail |

**Order:** P0 → (M0, E0) in parallel → (F0, M1) → F1/F2, optional M2 → M3 + F3 → Q0. A passive first prototype is not a separate competing product: it is a prerequisite to the same charger-ready hardware. Defer M2 entirely if real desk depth/comfort is poor.

## Releases and honest status
- V10 simulator: browser UI and Node smoke tests **implemented**.
- C++ portable StudyEngine and milestone policies: **sources/tests exist**; hardware persistence **not yet bound**.
- V14 geometry: parameterized sample **not production-ready**; phone case, C-BOX mount and puck unmeasured.
- 4.3C vendor demos, native LVGL opt-in **source prototype created**, NVS backend, audio, OTA: **hardware flash, LCD touch operation and persistence not verified**. ESP-IDF 5.5 **16MB Flash/Octal PSRAM + opt-in LVGL9 source prototype** cross-compile PASS [run 39144643479](https://github.com/choiYhunn/pokedock-companion/actions/runs/39144643479); however no actual board LCD/touch test, NVS persistence or native product polish is complete.
- Don't mark any gate PASS based on a document, no-op CMake or static picture.

## Decisions without unnecessary iteration
1. Default phone: **landscape 70°**. Test 65/70/75 physically and retain whichever is best in 70° ±5° without growing depth.
2. Display: OEM 33630 casing retained, detachable nonintrusive clamp/rear insert after physical hole measurement.
3. Power: independent rated HMI DC supply + optional USB-C PD adapter, external cable clips; no self-made mains or integrated battery.
4. Manufacturing: cardboard 1:1 first, serviceable PETG prototype or laser-cut PC/acrylic where simpler; 3D printer is **not mandatory**.
5. Ship UI HOME/FOCUS/TIMER first; clock/RTC, user data, animation after actual BSP demonstrates touch. Separate C3, NFC/LED, BLE, OTA and imported audio stay beyond MVP.

## Worktree/repro
`tests/v10_navigation_smoke.cjs`, `tests/party_game_smoke.cjs`, `tests/v14_geometry_smoke.cjs`, portable `firmware/hmi/core/tests/*` should run under `scripts/test_host.sh`. This checks **host behavior only**. ESP-IDF local SDK compiler, USB board, real iPhone/case and actual charged thermal testing require bench access. Evidence template: [V14 test protocol](V14_TEST_PROTOCOL.md).
