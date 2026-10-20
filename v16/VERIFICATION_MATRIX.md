# V16 End-to-End Preorder Audit Matrix
Checked: 2026-10-21. The words PASS are reserved for executed tests with evidence; source-created != product-ready.
| Stage | Acceptance | Evidence or blocker | Status |
|---|---|---|---|
| Requirements | Round gift-grade B, five characters, clock/focus/alarm, manual update | User decision; V16 source main | DESIGN PASS |
| Gift industrial appearance | OFF-state attractive from front/side/rear, small desk footprint | Browser concept only, finish/canopy vendor missing | BLOCKED |
| CAD bounding | 2.41 bare PCB 47.2x64x11.8, active 37.22x49.65, front OLED 44.5x37 | Rev B 132x105x54 shell, 104x85x82 chamber, flat 64x70 reflector mock | HOST GEOMETRY PASS / FIT UNVERIFIED |
| Reflector geometry | plate entirely inside outer volume and does not block screen | parametric 45deg envelope; bench optical ray tracing and seam alignment missing | CONCEPT ONLY |
| Optical visual | Ghost facial expression readable at 60cm, 150/300/500lux, multiple sight angles | Hardware absent; commercial screenshot not evidence | BLOCKED |
| Character inventory | Gengar/Piplup/Togekiss/Lucario/Quagsire | PokeAPI GIF + artwork links verified in Git tree; NOT licensed for redistribution | REFERENCE FOUND / RIGHTS BLOCKED |
| Animation assets | 5*idle/enter/exit/two actions, consistent style | Authoring/final premium sprite master not done | BLOCKED |
| Offline codecs | transparent RGB565 compressed frames with bounds checking | ghf_codec.py and ghf_decoder.h with local roundtrip and C++ ASAN/UBSAN tests; input fixtures generic | HOST PASS, DEVICE NOT TESTED |
| ESP-IDF toolchain | actual 2.41 V2 BSP display/RTC/SD/button compiled & flashed | V16 IDF is console-only; no board/toolchain in session | BLOCKED |
| Timer semantics | 15/25/45 monotonic pause/resume, one-shot completion | portable C++ host compiled and exercised locally; JS runtime checks executed | HOST PASS |
| Alarm persistence | KST/NTP/RTC, schedule retention, snooze/mute, no repeats across power cycle | Daily in-memory alarm logic only; NVS and speaker unimplemented | BLOCKED |
| Electrical | verified 5V current, 3.3V I2C level, OLED SPI-to-I2C mode, V2 pin mapping | Maker V2 docs and GPIO47/48 I2C; external OLED wiring not physically tested | PARTIAL DOCS |
| Media runtime | SD FATFS mount, render 12/24fps, 256x256 PSRAM cache, no dropped frames | GHF1 decoder portable source; driver/render loop absent | BLOCKED |
| Optical/animation synchronization | mirror orientation and scene anchors correct | local browser sim isn't calibrated for optics | BLOCKED |
| Firmware OTA | physical confirmation, signed update, two app slots, rollback/USB rescue | disabled reference only, 16MB partition PROPOSAL; real signing/checks absent | BLOCKED |
| Asset-only update | manifest signature, complete staging, atomic A/B switch, fallback | offline Ed25519 sign/verify; ESP32 updater/atomic swap unimplemented | HOST SIGNER ONLY |
| Packaging and safety | finished clear chamber, clean wiring, no thermal concern, 4h bench | physical parts absent | BLOCKED |
| Supplier checkout | exact 2.41 V2 / exact OLED mode, freight, tax, lead time | manufacturer list and indexed domestic prices, not cart checkout | NO BUY |
| Security/IP | private letters local; copyrighted Pokémon assets outside public repo | source inventory metadata only | POLICY PARTIAL |

### Build blockers to remove in order
1. 1:1 bench optical model using a phone first. A shallow 30deg reflector may work better at normal seated desk eye height than 45deg; choose after measurement.
2. Buy only a vendor-confirmed PCB version after satisfactory sample; document revision/serial, run official V2 demos separately.
3. Physically measure PCB, OLED, USB clearance and reflector after the module works; revise CAD. Do not send placeholder Rev B base as production file.
4. Obtain permitted production animation assets and validate GHF1 on actual 2.41 using PSRAM.
5. Integrate front clock, encoder/button, WiFi/NTP->RTC time, sound optional and NVS.
6. Build and fault-inject signed opt-in OTA + on-device A/B signed media installer; check rollback 5 times.
7. 4h thermal soak, 10 cold boots, 2 days daily-use practice and presentation/packaging.
