# PokéDock V14 — reproducible verification matrix and evidence template

Each test has three statuses: **PASS** only with run evidence; **FAIL** with logs/photos; **BLOCKED** if hardware/tool isn't present. Never substitute "documented" for tested. Date/repo SHA/board rev/OS/IDF/BSP and test performer must be recorded.

## Host tests — available without a board
Run `bash scripts/test_host.sh` with Node >=18, g++ C++17 and optional OpenSCAD. Includes: V10 navigation/rewards web simulation, party selection, V14 geometry 65°/70°/75° arithmetic, StudyEngine pause/stop/complete, Focus milestone 1/2/5/10/20h, RewardEngine, TrainerProgress, PartnerMotion, static ESP-IDF structure. These are *host-level tests*, **not firmware proof**.

## Board / physical stage gates
| ID | Required setup | Steps and pass criterion | Failure investigation |
| --- | --- | --- | --- |
| H01 SKU | received HMI | Photo 33630 C-BOX, board revision and 116.3×79×18 OEM outline checked | return wrong board |
| E01 isolated power | verified off-power DMM + certified 12V regulated candidate | correct terminal screw + positive/negative, insulate, load voltage stable | polarity, incorrect plug, current budget |
| E02 LCD/touch | official Waveshare demo | true panel 800×480, 4 corner touch each 5x | LCD/GT911/rotation/BSP |
| E03 RTC | CR927 fitted | 5 disconnect/reconnect tests, no unintended date/time loss | battery polarity, RTC driver |
| E04 SD | 16–32GB tested SD, FAT driver | 10 read cycles, safe missing-card behavior, no autocorrupt/format | SDMMC board pin config, filesystem |
| E05 audio conditional | confirmed matched speaker | low volume playback + mute/snooze and quiet hours | connector and impedance |
| M01 passive | actual iPhone 14 Pro+case, 65/70/75 cardboard fixture | no camera/button/cable collision, 30 one-handed cycles with stable screen and phone | redesign bottom lip and rear feet |
| M02 optional charging | real finished puck+PD on M01 fixture | iOS charging indicator for 60 min, no abnormal heat, other HMI functions normal | coil/case misalignment, thermal/vibrations |
| M03 production fit | verified OEM mount thread and camera/puck measures | final 1:1 holes fit, removable fasteners, cable routes protected, no permanent glue | remeasure, prototype iteration |
| F01 native UI | real 33630+IDF | 800×480 HOME + Focus run, touch response and 5 restarts | unsupported BSP/PSRAM/clock |
| F02 timer/ledger | real 33630 + instrumented commits | 15/25/45 once credit, break/general 0, power cut at before/after commit, no duplicates | NVS transaction migration |
| F03 offline | wifi off, SD unplugged, RTC lost | clock shows unsynced until trusted; timer works; fallback portrait/no crash | coupling to network/assets |
| Q01 stress | assembled dock, optional charged phone | 4h attended bench soak + 8h longer idle after safe thermal, no reset/heat, stable touch | mechanical thermal and power |
| Q02 recovery | USB boot recovery image | signed/offline backup of own user data; working flash recovery; private data erase on test unit | no gift ship |

## Sample evidence register (copy and fill; not proof until filled)
```yaml
test_id: "M01"
date_local: null
firmware_repo_sha: null
vendor_repo_sha: null
board_sku: "33630"
pcb_rev: null
idf_version: null
lvgl_version: null
phone: "iPhone 14 Pro"
case_model: null
mag_safe_puck_model: null
case_L_mm: null
case_W_mm: null
camera_profile_mm: null
hmi_mount_thread: null
hmi_mount_depth_mm: null
assembled_W_D_H_mm: null
supply_measured_V_A: null
ambient_c: null
hmi_surface_c: null
iphone_surface_c: null
charge_duration_min: null
dock_cycles: null
photo_refs: []
log_refs: []
status: BLOCKED
failure_notes: null
```
No private couple text in screenshots published to the repository.

## End-to-end acceptance
Minimum release requires H01,E01,E02,E03,E04,M01,M03,F01,F02,F03,Q01,Q02 PASS. M02 required **only** if giving charger. E05 can be deferred if no audio alarm promised. The user must be able to remove the phone one-handed and access USB/SD/BOOT/RST without dismantling the irreversible shell. Do not announce product-ready before all compulsory gates.
