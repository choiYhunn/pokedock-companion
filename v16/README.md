# V16 Ghost Companion — WORK IN PROGRESS

**New 2026-10-23:** [Host-tested GHF1 RGB565+alpha optical compositor](runtime/README.md) / [mirror-X renderer](runtime/frame_player.h) / [regression test](runtime/test_frame.cpp). This is an intermediate renderer and must be integrated into verified V2 RM690B0 QSPI driver; no hardware FPS or physical optics certification.


> **CURRENT OPTICAL PROTOTYPE: Rev D (2026-10-22)** — [Optical engineer report](revD/VERIFICATION_REPORT.md), [Rev D CAD](revD/revD_envelope.scad), [one-round purchasing checklist](revD/ONE_SHOT_BOM.csv), [host runtime](revD/ghost_runtime.h) and [SSD1309 clock test source](revD/ssd1309_portable.h). The Rev C 64x70mm beam splitter has been superseded by 82x88mm geometric optimization; **no real-optical or physical assembly approval and NO FULL-BASKET PURCHASE**. Current Rev D independent testing bundle also exists in the originating ChatGPT conversation.\n\n> **CURRENT DESIGN: Rev C (2026-10-21)** — [Final candidate design](REVC_DESIGN_LOCK.md) · [Supplier/outsource selection](REVC_PROCUREMENT_AND_OUTSOURCE.md) · [Audit](REVC_CRITICAL_AUDIT.md) · [Dimensioned CAD](cad/ghost_v16_revC_envelope.scad). Earlier Rev B dimensions and square-clock choices below are historical only. **Do not purchase complete basket** before optics and fit proof.\n\n
**Decision date: 2026-10-20.** User selected option B: a *rounded hybrid Pepper's Ghost clock*.
This branch establishes the new design target; **V15 remains the last prior manufacturing plan, not an approved V16 hardware build**.

## What's actually delivered in this branch
- [Product & engineering contract](PRODUCT_AND_ENGINEERING.md): exact user-facing UX, character motion policy, proposed MCU, independent clock, acceptance gates.
- [Optics and finishing](OPTICS_AND_ACCEPTANCE.md): honest 2D reflection limitations and contrast/viewing tests.
- [Phone-based optical pretest](bench/optical_test.html): BLACK background + moving synthetic ghost silhouette, color contrast/clock/flip/size test. No paid hardware or Pokémon sprites required.
- [Electrical interface](ELECTRICAL_AND_POWER.md): 2.41 V1/V2 revision, front OLED I2C, 5V USB, optional buzzer, RTC backup risks.
- [Animation production](ANIMATION_PIPELINE.md): five characters, motion states, memory budget and user-owned 12fps local frame imports.
- [Assembly and vendor workflow](BUILD_AND_FABRICATION.md): optical gate, measured CAD, print finishing and gift acceptance.
- [Browser simulator](simulator/index.html): interactive rounded product appearance, five placeholder characters, animation reactions, KST clock, monotonic focus presets, a daily alarm, theme toggles. Does **not** model real optical luminance or include Pokémon assets.
- [Pure JS simulator engine](simulator/engine.js), [Node tests](tests/engine.test.cjs).
- [Portable C++ engine](firmware/ghost_core.h), [tests](firmware/ghost_core_test.cpp) for independent time and alarm behavior.
- [CAD concept](cad/ghost_v16_concept.scad), MODE=base exports a SINGLE prototype base model only; dimensions, ports and mounts are unverified.
- [ESP-IDF console-only skeleton](firmware/idf): not an AMOLED/OLED board port.
- [OTA safety and asset plan](OTA_MANUAL.md): disabled-by-default HTTPS OTA reference module, 16MiB **proposal** partition table, external ED25519 [asset signer/verifier](tools/assets.cjs) and tests. No on-device OTA, signed media install, or network updater is claimed.
- [Cost envelope](BOM_PLANNING.csv) and [supplier links/checkout rules](PROCUREMENT_CURRENT.md). No purchase approved.
- [Preorder verification matrix](VERIFICATION_MATRIX.md): host-passed versus physical/unavailable work.
- [Rev B measured-envelope CAD](cad/ghost_v16_revB_envelope.scad) supersedes generic Rev A dimensions only as a geometric concept.
- [Artwork reference inventory](assets/asset_sources.json) and [rights review](assets/SOURCE_AND_LICENSE_AUDIT.md).
- [GHF1 animation converter](tools/ghf_codec.py) / [bounded C++ decoder](firmware/ghf_decoder.h) and host test script (run `bash v16/scripts/test_host_codec.sh`).

## Run locally
From this repository: bash v16/scripts/test_host.sh
Or directly open v16/simulator/index.html in a browser. Online fonts may be requested; system font fallbacks work offline.
ESP-IDF requires a supported toolchain and source board driver. Do not flash before electrical and optical gates.

## Next HARD blockers
Real optical visibility at 150/300/500lux; sourced 2.41in AMOLED (800nit nominal) panel active size, V1/V2 PCB revision and pinout; verified clock OLED and RTC; clean 3D print tolerances; licensed/private high quality animation pack; ESP-IDF AMOLED driver + actual 24fps profiling; signed OTA release and rollback testing.
No part has been bought or validated in this branch. Do not interpret SOURCE CREATED as GIFT-READY.

## Why the design changed
V15 solved a 4.3-inch HMI mechanical problem but still looked too much like a generic panel. V16 uses the electronics to create the EXPERIENCE: characters appear and move inside a transparent optical volume while the clock remains readable on its own display. A rounded shell and one knob are planned, without an industrial touch tablet aesthetic.
