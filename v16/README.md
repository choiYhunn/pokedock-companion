# V16 Ghost Companion — WORK IN PROGRESS
**Decision date: 2026-10-20.** User selected option B: a *rounded hybrid Pepper's Ghost clock*.
This branch establishes the new design target; **V15 remains the last prior manufacturing plan, not an approved V16 hardware build**.

## What's actually delivered in this branch
- [Product & engineering contract](PRODUCT_AND_ENGINEERING.md): exact user-facing UX, character motion policy, proposed MCU, independent clock, acceptance gates.
- [Optics and finishing](OPTICS_AND_ACCEPTANCE.md): honest 2D reflection limitations and contrast/viewing tests.
- [Browser simulator](simulator/index.html): interactive rounded product appearance, five placeholder characters, animation reactions, KST clock, monotonic focus presets, a daily alarm, theme toggles. Does **not** model real optical luminance or include Pokémon assets.
- [Pure JS simulator engine](simulator/engine.js), [Node tests](tests/engine.test.cjs).
- [Portable C++ engine](firmware/ghost_core.h), [tests](firmware/ghost_core_test.cpp) for independent time and alarm behavior.
- [CAD concept](cad/ghost_v16_concept.scad), MODE=base exports a SINGLE prototype base model only; dimensions, ports and mounts are unverified.
- [ESP-IDF console-only skeleton](firmware/idf): not an AMOLED/OLED board port.
- [OTA safety and asset plan](OTA_MANUAL.md): disabled-by-default HTTPS OTA reference module, 16MiB **proposal** partition table, external ED25519 [asset signer/verifier](tools/assets.cjs) and tests. No on-device OTA, signed media install, or network updater is claimed.
- [Cost envelope](BOM_PLANNING.csv). Price estimates not current shop orders.

## Run locally
From this repository: bash v16/scripts/test_host.sh
Or directly open v16/simulator/index.html in a browser. Online fonts may be requested; system font fallbacks work offline.
ESP-IDF requires a supported toolchain and source board driver. Do not flash before electrical and optical gates.

## Next HARD blockers
Real optical visibility at 150/300/500lux; sourced display active size and pinout; verified clock OLED and RTC; clean 3D print tolerances; licensed/private high quality animation pack; ESP-IDF AMOLED driver + actual 24fps profiling; signed OTA release and rollback testing.
No part has been bought or validated in this branch. Do not interpret SOURCE CREATED as GIFT-READY.

## Why the design changed
V15 solved a 4.3-inch HMI mechanical problem but still looked too much like a generic panel. V16 uses the electronics to create the EXPERIENCE: characters appear and move inside a transparent optical volume while the clock remains readable on its own display. A rounded shell and one knob are planned, without an industrial touch tablet aesthetic.
