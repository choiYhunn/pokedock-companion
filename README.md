# PokéDock Companion

**V14 confirmed accessory/geometry baseline — 2026-10-18:** iPhone **14 Pro + MagSafe-compatible everyday case**, paired with cased Waveshare **4.3C-BOX SKU 33630**. Prefer **70° landscape rear slot** with **separately powered, detachable finished MagSafe charging puck**. The phone weight rests on rails/stop independent of the display. Aim for a clean ~170–180mm wide × 90–115mm deep *planning envelope* (not a verified product dimension). **MagSafe case support does not substitute for real charge/heat/fit tests.** See [V14 design](docs/V14_MAGSAFE_READY_DESIGN.md), [V14 purchasing](docs/V14_PURCHASING_BOM.md), [V14 assembly](docs/V14_ASSEMBLY_SOP.md), [V14 CAD](cad/pokedock_v14_magsafe_ready.scad) and [V14 calculator](design.html).


**Archived V13 (superseded by V14 MagSafe-ready): V13 iPhone 14 Pro COMPACT SLOT.** Use [V13 decision](docs/V13_COMPACT_IPHONE_14_PRO.md) and [V13 OpenSCAD adjustable mock](cad/pokedock_v13_compact_slot.scad). Confirmed phone is **14 Pro**; confirmed cased Waveshare 4.3C-BOX external envelope **116.3×79×18mm**. Default rear phone orientation becomes **landscape 70°**, with a **passive noncharging padded slot first** and **optional removable MagSafe only later**. This supersedes the V12 39° landscape/32° portrait prior defaults. No manufacturing clearances have been signed off.

**Latest industrial/mechanical baseline (2026-10-18): V12 QUIET DESK.** Product/UI web prototype remains V10; real board and charger have **not** been validated.

**[Open V12 live design calculator](https://choiyhunn.github.io/pokedock-companion/design.html)** · **[Interact with V10 device UI](https://choiyhunn.github.io/pokedock-companion/simulator.html?v=10)**

The product is intentionally a clean front-facing Gengar/clock picture-frame with **a separate rear MagSafe phone support**, no front phone tray and no bulky integrated NFC platform. A/B mechanical decision is now explicit: **A horizontal/landscape phone for desk-space efficiency**, vs **B portrait low-angle phone for better concealed front**; choose after physically testing exact iPhone model/case/puck and 4.3C-BOX mounting case.

### V12 physical source of truth
1. [Industrial design form/space comparison](docs/V12_INDUSTRIAL_DESIGN.md), including reference envelope ~169×118mm A vs ~148×187mm B using **unverified sample case/case allowance dimensions**.
2. [Interactive dimensional review lab](design.html) — user can adjust iPhone 14 variant, case allowance, screen housing dimensions, angle.
3. [V12 configurable OpenSCAD mock](cad/pokedock_v12_quiet_desk.scad) — layout choices and dimensions; **not print-ready/structurally validated**.
4. [Actual measurement register](docs/V12_MEASUREMENT_REGISTER.md) — required OEM rear mount/bolt/puck/camera/cable inputs.
5. [Fabrication & industrial finishing plan](docs/V12_FABRICATION_PLAN.md) — modular OEM screen bracket, removable phone rails, separate base and hidden cable runs.
6. [Phase A/B procurement](docs/V12_PROCUREMENT.md) — exact screen SKU, separate certified screen and MagSafe supplies, deferred C3/NFC/LED.
7. [Day-of-assembly SOP](docs/V11_ASSEMBLY_SOP.md) and [electrical isolation](docs/V11_ELECTRICAL_WIRING.md), plus [ESP-IDF/LVGL bring-up](docs/V10_HARDWARE_PORTING.md).
8. [Cumulative study-to-Pokémon core policy](docs/V11_STUDY_POKEMON_PROGRESS.md).

**Mechanical source:** manufacturer's official [4.3C hardware/dimensions](https://github.com/waveshareteam/ESP32-S3-Touch-LCD-4.3C/tree/main/hardware/dimensions) includes DXF/PDF/STEP. C-BOX mounting pitch noted as 75mm; bolt size/depth not yet established.

## Archive: earlier V11 and implementation references

1. **[V11 master execution index](docs/V11_EXECUTION_INDEX.md)** — single handoff and stage gates.
2. **[V11 mechanical calculations + measurement worksheet](docs/V11_MECHANICAL_DESIGN.md)** — corrected rear phone geometry and fit options.
3. **[V11 electrical/wiring](docs/V11_ELECTRICAL_WIRING.md)** — exact 4.3C board vs MagSafe separate supplies, future NFC/LED, audio path.
4. **[V10 staged procurement BOM](docs/V10_BOM_AND_PURCHASE.md)** — what to buy first vs postpone.
5. **[V11 assembly SOP](docs/V11_ASSEMBLY_SOP.md)** — inspection, power-up, temporary jig, MagSafe, LVGL, final tests.
6. **[V10 ESP-IDF/LVGL port plan](docs/V10_HARDWARE_PORTING.md)** — vendor examples to actual HMI firmware.
7. **[V11 cumulative study/Pokémon rules](docs/V11_STUDY_POKEMON_PROGRESS.md)** — 1h/2h/5h/10h milestones; prototype policy, not wired to real firmware.
8. **[V10 test and readiness gates](docs/V10_TEST_ACCEPTANCE.md)**.
9. **[Proposed HTTPS OTA / dual-app slots](firmware/hmi/ota/README.md)** — design only, not deployed.

Older CAD archive:
- [V11 parameterized fit mock](cad/pokedock_v11_fit_mock.scad) — **unmeasured samples; DO NOT PRINT AS PRODUCTION ENCLOSURE**.
- [Old V4 sketch](cad/pokedock_v4_compact.scad) — historical conceptual sketch with incompatible assumptions, superseded for fit.
- [Official Waveshare 4.3C 2D DXF and 3D STEP reference](https://github.com/waveshareteam/ESP32-S3-Touch-LCD-4.3C/tree/main/hardware/dimensions) — manufacturer PCB/display model; plastic **C-BOX** case must still be physically verified.

## Exact hardware scope

| Domain | Baseline | Status |
| --- | --- | --- |
| HMI | Waveshare **ESP32-S3-Touch-LCD-4.3C-BOX**, **SKU 33630**; 800×480, 16MB flash/8MB PSRAM, RTC, microSD, audio codec | Chosen, **not physically purchased/flashed here** |
| Phone | iPhone **14-family** (exact model/case not confirmed), finished MagSafe puck with separate certified compatible USB-C PD adapter | Geometry/charging unverified |
| Power | 4.3C **7–36V DC terminal**; example regulated 12V supply *only after actual connector + polarity verification* | Unwired |
| Dock v1.1 | Optional ESP32-C3 + PN532 NFC + lux/ToF + subtle LED, ESP-NOW | Deferred |
| Music/alarms | Codec + matching speaker, user-imported audio via future microSD / local web workflow | Planned; not implemented |
| OTA | ESP-IDF HTTPS firmware dual-partition + rollback, optional future atomic SD asset bundles | Proposed, **not flashed or tested** |

## Product experience

**HOME → Focus directly**, and a central Poké Ball menu with **매일 쓰는 도구 / 포켓몬 놀이** plus tucked-away settings.

- Focus: 15/25/45 minutes, then 5-minute rest; completed study gets rewards; plain countdown does not.
- To-do/D-day and personal note/anniversary are editable *in the browser simulator* and saved in same-profile localStorage (unencrypted and not synced to board).
- Party select animates Gengar (clear favorite), Piplup, Togekiss, Lucario and Quagsire. Browser sprites load over network; an actual standalone device needs locally prepared appropriate artwork.
- Browser reward: **도감에 기록** actually adds the encountered Pokémon; **나중에** defers.
- A proposed nonintrusive progression policy counts *verified total completed Focus minutes*: 60min Gengar reaction/star, 120min Piplup postcard, 300min egg, 600min badge, 1200min room background. Host C++ policy exists but is **not integrated in V10 simulator or device**.

## Repo layout

\`\`\`text
simulator.html                       clickable 800x480 web UI (V10)
ui/party-game.js + party-game.css    game-like choice and animation (browser)
docs/                               product, BOM, dimensions, electrical, build, QA
cad/pokedock_v11_fit_mock.scad       parameterized reference geometry
firmware/hmi/core/                   portable C++ study/reward/motion policy
firmware/hmi/ui/                     LVGL porting screen IDs/view models (not complete native app)
firmware/hmi/ota/                    proposed dual-slot OTA configuration
firmware/dock_node/                  unverified ESP32-C3 scaffold (optional)
firmware/shared/                     HMI/Dock protocol contract
config/                              catalogs and features
\`\`\`

## Honest readiness

**Implemented:** browser simulator interaction and test scripts; C++ portable engine/policy source and host tests; detailed V11 design/measurement/assembly documents.

**Not yet implemented/proven:** assembled unit, verified 4.3C-BOX power wiring, actual iPhone fit/temperature, native LVGL HOME/Focus, on-device NVS, audio playback/import, NFC operation, iOS ANCS notification forwarding, device OTA / rollback. GitHub Pages deployment success is not a physical hardware test.

## Sources and rights

[Official Waveshare documentation](https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3C) · [Waveshare manufacturer files](https://github.com/waveshareteam/ESP32-S3-Touch-LCD-4.3C) · [Apple iPhone 14 dimensions](https://support.apple.com/ko-kr/111850) · [Apple MagSafe support](https://support.apple.com/ko-kr/105047).

This is a personal, noncommercial fan gift, not an official Pokémon product. Pokémon character artwork and cries remain rights-holder content; web art references do not authorize repackaging or distributing a device asset bundle.
