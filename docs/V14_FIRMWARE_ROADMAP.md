# PokéDock V14 — actual ESP-IDF / LVGL delivery contract

## What is executable today
- Browser: V10 HTML/CSS/JS `simulator.html`, Node smoke tests. **Not** embeddable LVGL UI.
- Portable C++: `StudyEngine`, deterministic `commit_verified_focus` policy, reward engine, partner motion and host tests. Persistence NVS adapter and actual on-device clock/task wiring **not** implemented.
- `firmware/hmi/espidf` = **M0 console by default** plus **optional LVGL9 HOME/FOCUS/BREAK** C++ preview, compiled with Waveshare BSP 3.0.1. [Run 39144643479](https://github.com/choiYhunn/pokedock-companion/actions/runs/39144643479): ESP-IDF 5.5 + 16MB flash + Octal PSRAM + native LVGL9 compile **PASS**; physical board runtime, NVS, RTC, assets remain unverified. The earlier M0 build used wrong 2MB flash and was superseded.

## Baseline choice and version lock
1. Obtain actual 33630 board revision and compare against Waveshare first-party `examples/esp-idf/03_lcd`, `06_touch`, `02_rtc`, `05_sd`, `11_speaker_microphone`, `12_lvgl_transplant`. Record first-party SHA + exact `sdkconfig.defaults`, BSP/LVGL version and ESP-IDF tag.
2. Compile the **vendor example in its own directory first**; no updates to board-level pins until example functions. IDF >=5.3<6, managed BSP 3.0.1 is a dependency *candidate*, not guaranteed working combination. LVGL v8/v9 migration is a deliberate step.
3. USB-C debug is separate from 7–36V terminal, power/BOOT/RST sequence according to 33630 vendor docs. Save factory BIN/hash/read-back if legally/technically feasible; know reflashing before touching gifted image.
4. Log PSRAM init, display resolution/double buffering, GT911 coordinates and controller rotation. Run vendor demo 60 min.

## Native app architecture
```text
app_main:
   board_init (factory-verified HMI board abstraction)
      └─ display / GT911 touch / PCF85063 RTC / SDMMC / optional ES8311
   services:
      monotonic_clock (esp_timer)
      clock_service (RTC + NTP reconciler; trust state)
      focus_service (portable StudyEngine, no LVGL ownership)
      transactional_focus_store (versioned durable NVS candidate; not yet implemented)
      todo_store + private_note_store (NVS schema and explicit clear)
      asset_loader (SPIFFS/flash static fallback; SD optional)
      networking (optional NTP and local settings, no blocking rendering)
   LVGL UI task (exclusive owner):
      HOME  -> FOCUS -> TIMER -> MENU -> DDAY/TODO -> PARTY/DEX -> OUR_SPACE
      touch callback → app event queue
   USB rescue separate from OTA partition.
```

## Screen-by-screen, measurable milestones
| Stage | Real HW output | Design and test contract |
| --- | --- | --- |
| L0 | BSP-backed LVGL prototype (source created) | An opt-in English HOME/FOCUS/BREAK screen exists for compilation. **Display & touch response on actual 33630 not yet verified**; test four corners ×5 |
| L1 | HOME | offline-safe clock/date, Gengar fallback static, big Focus action, brightness and Settings |
| L2 | FOCUS | 15/25/45 active timer, pause/resume monotonic, 5min separate rest, Back while running, only one complete event |
| L3 | TIMER | ordinary 3/5/10/30min; none of it increases study totals; distinct alarm policy |
| L4 | Settings/local planner | NVS schema migration, Todo/D-day & private note clear; missing RTC warns unsynced and never forges dates |
| L5 | Pokémon PLAY | indexed party select/personal Gengar, bounded animation, sprites converted for LVGL v8/v9 exact decoder and SD fallback |
| L6 optional | audio / software update | test ES8311 load + mute/snooze; HTTPS OTA dual app + rollback only after binary fit and power-loss injection |

## Focus reward state invariants
- Only naturally completed **FOCUS** stage accrues 15/25/45 minutes; no generic countdown, pause, incomplete session or 5min rest credit.
- Prevent duplicates when power is interrupted at persistence boundary. For portability a **transactional store adapter must write a fully serialized record and validate it before acknowledging reward**. Do not expose reward animation before durable commit.
- Time source split: monotonic elapsed seconds for duration; RTC/NTP *trusted* local calendar day for optional daily bond. Missing time can still run Focus but reward must be pending/explicit, **never fabricated**.
- Long-lived state versioned; personal note NVS separate from app and SD artwork. Data erase must be physical-screen accessible.

## Memory/asset sizing
- Framebuffer RGB565 full frame ~800×480×2 = **768,000 bytes** (~750 KiB). Double full buffer ~1.54MB. Use PSRAM-aware vendor strategy; exact buffer size/profiling per driver.
- Bitmap 100×100 RGB565 =20KB per frame before compression; 8-frame character animation ~160KB before metadata. Convert with asset pipeline for exact LVGL version; measure PSRAM fragmentation, partial redraw, maximum touch latency.
- Built-in fallback never needs microSD or Wi-Fi. Browser remote PokeAPI GIF URLs **cannot** be blindly linked as production assets, and copyright remains a separate approval matter.

## OTA & recovery
- OTA CSV 16MiB dual 6MiB app slots is **proposal**. `idf.py size` must fit both image slots and partition offset. Then add TLS validation, board ID, rollback health gates, USB fallback and 5 forced failures. If any unresolved, ship with USB firmware update, not a misleading OTA button.
- For an iPhone user: BLE notification/ANCS and wireless charging percentages are not part of gift MVP.
- No bundled arbitrary Pokémon cries/official music/audio asset downloads in a public repo.

## Tests and evidence
See [V14 test protocol](V14_TEST_PROTOCOL.md), [official Wave demos](https://github.com/waveshareteam/ESP32-S3-Touch-LCD-4.3C), [IDF porting baseline](V10_HARDWARE_PORTING.md). Host regression and the ESP-IDF cross-build both passed; **neither proves actual LCD/touch operation, NVS durability or hardware integration**. See [full validation report](V14_VALIDATION_REPORT_20261019.md).
