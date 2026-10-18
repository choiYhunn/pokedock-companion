# PokéDock V14 — assembly and measurements SOP

## 0. Record hard facts first
- iPhone 14 Pro + MagSafe compatible case **CONFIRMED**.
- iPhone case make/model and actual dimensions, which side the camera should be on, coil center in case, real puck diameter/thickness and lead bend **NOT YET MEASURED**.
- Waveshare C-BOX outer dimensions published 116.3×79×18mm; delivered PCB revision/ports, rear mounting insert size/thread/depth **NOT YET MEASURED**.

Create a local measurement sheet (mm): phone_L____ phone_H____ maxT/camera____ centerCoil_from_lower____; MagSafe_D____ T____ exit____; HMI rear holes centers____ diam____ safe_depth____; desk free depth____; expected assembly W____ D____.
Do not push screw/rail against camera module or lower Lightning port.

## 1. Separate supplier/factory electrical tests
1. Purchase/receive exact cased Waveshare SKU 33630 and a **manufacturer-compatible regulated power supply**, not a random 5V old 4.3 unit. Confirm safe DC terminal polarity against silkscreen+vendor.
2. Prepare manufacturer ESP-IDF factory firmware recovery. Verify LCD/touch, RTC coin backup, microSD and audio connector/codec.
3. Keep HMI alone on desk until 60 minute bench run passes; never build the charging circuit into MCU wiring.
4. On PC, install official ESP-IDF example first, **not** web simulator HTML. Separate native LVGL port is later.

## 2. Low-cost mechanical experiment BEFORE printer
1. Cut iPhone 14 Pro paper silhouette 147.5×71.5mm and exact real phone+case outline; cut front Waveshare case silhouette 116.3×79mm. Tape only cardboard on support, not against battery.
2. Make three stable rear stands at 65°, 70°, 75° from horizontal. In landscape put lower long-edge onto a silicone-lined 8–10mm-deep **provisional** lower stop; rear structural rail holds the phone independently from the MagSafe puck.
3. Put real phone with case into passive rear stand and place Waveshare display in front at about 76°. Mark how much is seen at seated eye-level and capture top/rear desk depth.
4. Check one-hand pickup, fingers reaching side edges, no rattles, no collision with phone buttons or rear camera or HMI ports. Run 30 cycles before declaring success.
5. Now place a finished MagSafe charger on phone's MagSafe case back using just its magnet — record the **true charging center**, cable direction and whether the camera bump affects docking. Never rely on "center of drawing" alone.
6. Temporarily clamp/tape the charger to the **carrier/support only**, not to the charging surface/cable joint. Ensure flush direct charge face-to-case alignment; add a removable 2-piece ring only after measuring puck.
7. Power the MagSafe via its own USB-C PD adapter, not from HMI. Verify phone's actual charging indicator, sustained charge, and heat for >=60 min, with LCD also powered. Pause/stop if charger/phone runs abnormally hot.
8. Confirm removing puck leaves a stable useful plain rear slot; HMI remains stable if phone removed.

## 3. CAD and manufacturing
- Update real measurements in [V14 OpenSCAD mock](../cad/pokedock_v14_magsafe_ready.scad).
- Choose 70° only after confirming 65/70/75 ergonomics. Early geometry target 170–180mm W / 90–115mm D; not a tolerance or final print size.
- Base: small rounded main screen foot + narrow rear anti-tip brace. No front protrusion, no big Poké Ball decoration.
- HMI: reversible rear adapter with manufacturer 75mm pitch **only after** verified true hole thread and safe insert depth. No drilling Waveshare PCB/case. Keep reset, SD, DC terminal, USB and airflow clear.
- Phone: rounded passive bottom ledge and two side locators lined with 0.8–1.5mm **trial pads**, final after case fit. No forced Lightning plug.
- Puck: split back-open two-piece holder. Do not glue the factory charger to a PCB or fully embed coil. Verify mechanical retention doesn't dislodge puck under magnet pull or phone removal.
- 4 replaceable non-slip base feet, tiny underside personalized symbol. Separate power cables clipped together externally for tidiness, not joined electrically.
- PETG prototype if 3D printed: choose appropriate wall strength and support, inspect creep/warp under real charging warmth. Actual assembly should be fully replaceable with basic tools.

## 4. Firmware / Gift MVP
- Build native LVGL HOME / clock / 15–25–45min Focus then 5min break / generic timer / clear Back on real display.
- RTC + NTP reconciliation; meaningful offline fallback; NVS private dates/letter/todos and settings in a versioned store.
- Static Gengar fallback, mild animations stopped in Focus/Night, sideload local licensed/user-provided sprite assets later.
- No real battery/charge percent from MagSafe alone; prefer no charge indicator, or clearly say "폰 거치" only if a verified presence sensor exists.
- Test 5 restarts and 60 min runtime. OTA is proposed, USB recovery mandatory; iOS ANCS alerts and NFC accessories remain later options.

## 5. Release gates (pass/fail)
| Gate | Test | Criteria |
| --- | --- | --- |
| Mechanical | Eye-level/side appearance | Neat Gengar screen, symmetric rear phone overhang accepted, no sharp material |
| Stability | 30 one-hand phone dock/remove | Screen stable, neither phone nor support tips or slips |
| Power | Exact manufacturer HMI supply | Polarity/voltage validated, no exposed AC, no unexpected heat |
| Charge | MagSafe iPhone+case 60min | Real charging stable, alignment reproducible, non-excessive heat |
| Access | SD/USB/DC/reset/charger replacement | All accessible without permanently tearing enclosure |
| Utility | RTC/timer/Focus/LVGL on device | Clock/Focus work without Wi-Fi, buttons don't misfire, no overcount |
| Privacy | Couple data | Erasable, not in public repo/serial logs |
| Fail-safe | SD missing, MagSafe unplugged, Wi-Fi off | Clock/Focus continue and screen is useful |
| OTA (optional) | Bad image/power loss | Prior image boots; if unverified, use USB only |
