# PokéDock V14 — 2026-10-19 engineering validation report

## Proven source / build results

| Test | Run/command | Actual result | Scope |
| --- | --- | --- | --- |
| Original Node V10 navigation & party | [GitHub Actions 39143866759](https://github.com/choiYhunn/pokedock-companion/actions/runs/39143866759), `bash scripts/test_host.sh` | PASS | Browser JS with simulated DOM, NOT real 800x480 touch |
| StudyEngine + time edge cases | same | PASS | 15/25/45 Focus, invalid duration rejection, pause/resume rollback guard, countdown no study credit |
| Deterministic Focus milestones | same | PASS | 1,2,5,10,20h thresholds with C++ host inputs |
| Portable two-slot FocusLedger | same | PASS | fault injection, restart, dupe detection, corrupted slots; **not connected to NVS** |
| V14 angle/sample geometry | same | PASS | 65°,70°,75° arithmetic only; not tested for overturning / heat |
| OpenSCAD V14 1:1 profile and mock | same | PASS | parsing/export, not DFM or print strength |
| ESP-IDF 5.5 M0 console app | [GitHub Actions 39143977602](https://github.com/choiYhunn/pokedock-companion/actions/runs/39143977602) | PASS | initial cross-build, but default 2MB flash wrongly configured. Corrected afterward |
| ESP-IDF 5.5 + Waveshare BSP 3.0.1 + **native LVGL9 prototype** | [GitHub Actions 39144643479](https://github.com/choiYhunn/pokedock-companion/actions/runs/39144643479) | **PASS**, built `pokedock_hmi_bringup.bin` (0xa33c0 bytes ≈653 KiB), **16MB flash**, Octal PSRAM, binary size check & app partition headroom ~56% | Firmware/toolchain/source compile only; no actual panel, power, runtime or physical IO tested |

The second CI build explicitly added `CONFIG_POKEDOCK_HMI_START=y` to a **temporary CI copy** of sdkconfig.defaults. The repository's default is still opt-in **OFF**. This ensures the `pokedock_lvgl_demo.cpp` source compiles but **does not** claim a stable, flashed, customer-ready native app.

Source-level LVGL functions use board-managed BSP and create English placeholder/controls: HOME label, 15/25/45min Focus presets, START/PAUSE/STOP, 5-minute separate countdown with zero focus credits. Important missing features: real RTC/NTP time, NVS store adapter, safe versioned private notes, font assets/Hangul, Gengar sprites, audio wiring, comprehensive UX, OTA and explicit error screens. Built != flashed != functional on real display.

## Corrections from initial tests
1. C++ host fake-storage warning `-Werror=misleading-indentation` corrected; test then PASSED.
2. Existing V14 OpenSCAD contained a literal escaped newline `\\n` inside `assert`, blocking real parse/export. Fixed in CAD and confirmed by actual OpenSCAD CI.
3. `StudyEngine` now disallows 0/invalid Focus duration, rejects backward monotonic resume, updates pause UI snapshot.
4. Initial IDF skeleton built with ESP-IDF default **2MB** flash, unsafe mismatch for 33630. `sdkconfig.defaults` now uses manufacturer-derived **16MB flash + Octal PSRAM**, checked in new successful CI build.
5. Native UI is **off by default** until actual board is bench-verified. USB factory image recovery remains necessary.

## Still not executed — required to change status to PASS

| Domain | Actual blocker |
| --- | --- |
| Purchased products | The recipient's daily case not caliper measured; exact Waveshare 33630 HMI and finished MagSafe puck not verified as purchased/received |
| Power and electronics | No verified physical +/− terminal polarity, no DMM electrical measurement, no 60-min actual HMI running |
| Native display | No physical 33630 LCD image, GT911 touch corner coordinates, RTC/SD codec functional tests; bundled display boot issue still possible despite compiled BSP |
| Durable study credit | Host 2-slot journal proves abstract logic only; actual NVS adapter, atomic NVS commits, brownout/battery removed injection untested |
| Case/structure | No real mount-hole centers/thread/depth, camera clearance, magnet force, measured physical 170mm×95mm footprint, anti-tip/touch-force test, no final manufacturable STL |
| Wireless power | Apple or Qi2 finished puck not thermally/charging verified with actual iPhone 14 Pro and MagSafe case |
| Gift release | Night dimming, local offline sprites, iPhone personal note secure erasure, OTA/USB recoveries and 4h stress test not executed |

**Do not call the product complete.** The next engineering stop is physical receipt/measurement and the OEM vendor LCD/touch/RTC example test. The current result is a working source-level research/manufacturing baseline with independently verifiable C++/JS/CAD and ESP-IDF cross-compilation.
