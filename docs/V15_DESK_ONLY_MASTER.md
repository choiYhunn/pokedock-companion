# PokéDock V15 | No-phone desk companion / current decision 2026-10-20

**Canonical product:** quiet Gengar-inspired 800×480 touchscreen desk clock/Focus-timer/gift. The recipient's phone, MagSafe, Qi2 charging, separate PD supply, C3/NFC/LED and large enclosure are OUT. V14 MagSafe-ready geometry and all former phone-specific procurement lists are historical only.

## Clear go/no-go and synchronized order
1. **Can now purchase concurrently:** exact cased Waveshare **ESP32-S3-Touch-LCD-4.3C-BOX SKU 33630** and **a single unverified Rev A prototype of the V15 one-piece PETG stand**. The standalone CAD input is [cad/pokedock_v15_cradle.scad](../cad/pokedock_v15_cradle.scad); regenerate via `openscad -o PokeDock_V15_Stand_RevA.stl -D 'MODE="stand"' cad/pokedock_v15_cradle.scad`. A downloadable prebuilt STL and multi-angle CAD render are included with the 2026-10-20 conversation package, not committed as binary to this repository.
2. **Stand nominal dimensions:** 136mm width × 96mm depth × 72.8mm height; one connected solid ~98.1cm³; HMI modeled at 116.3×79×18 mm, 75° to tabletop; top of HMI ~88.3mm. The bottom is flat, two low retaining lips, two narrow rear support ribs, and a **70mm open center U-slot** for terminal/cable service. Soft pads and high-friction feet are separately acquired after fitting. The OEM rear holes are not used.
3. **Important honesty boundary:** The printed stand is **Rev A prototype, not physically qualified**. OEM case fillets, terminal protrusion/cable bend, actual FDM shrinkage, glass/bezel contact, tipping under finger presses, rubber feet adhesion and safe power harness must be checked when parts arrive. A 0.8–1.0mm removable protection pad can handle small tolerances, not major geometry errors. Buyer authorizes the possibility of a second print, not a certified finished fit.
4. **Conservative shopping:** buy exact 33630 from [Waveshare maker](https://www.waveshare.com/product/esp32-s3-touch-lcd-4.3c.htm) with **plastic case** option (family listing USD39.99–45.99; shipping/selected final price not checkout-confirmed). Printed stand can be quoted in parallel from [3DFARM](https://3dfarm.co.kr/3d-printing-service/). PETG 1 unit budget ~₩30k–50k until a real slicer quotation is returned. Plastic case and stand are separate shipped products.
5. **No required external phone charger:** HMI official DC terminal is 7–36V; certified regulated 12V2A is a candidate to buy **after physically confirming DC input polarity and appropriate insulated cable termination**. USB-C is confirmed for firmware/debug, **not assumed** to supply production power on 4.3C (4.3B specs are not proof for C). Avoid arbitrary 12V-to-USB-C adapters. See [V15 wiring](V15_SIMPLE_WIRING.md).
6. **UI and OTA:** browser V10 and host C++ tests PASS; cross-compiled ESP-IDF 5.5 opt-in LVGL9 HOME/FOCUS prototype PASS [CI](https://github.com/choiYhunn/pokedock-companion/actions/runs/39144643479), but not physically flashed, no real touch/RTC/NVS tests. USB updates first. A tested signed HTTPS OTA dual-slot+rollback can later change UI without USB; OTA is NOT implemented/accepted yet.

## Work plan after simultaneous orders
| Step | Owner | Work | PASS evidence |
| --- | --- | --- | --- |
| P0 order | user | choose With plastic case/33630 at maker, send one prototype STL to print shop (or SCAD-export yourself) | purchase invoice shows exact 33630, STL geometry and PETG quote |
| M0 unpack | user + assistant | examine 4.3C case fillet, green terminal, real port reach, actual 18mm thickness; dry fit screen in stand | no hard plastic load on glass/terminal, all connectors accessible |
| M1 stability | user + assistant | four non-slip feet, rear rib 0.8–1mm pad, lower pad, optional removable low-profile holding strips on plastic case only | one-handed 30 tap/dock cycles, no case lift/tip; abandon if unstable |
| E0 electrical | qualified checker | identify 7–36V DC VIN/GND board/terminal with OEM schematic and DMM; certified 12V2A candidate | polarity evidence, 60-min stable power; no exposed mains |
| F0 | assistant + user flashing | vendor LCD/touch/RTC/TF example then firmware console and native LVGL | four corners ×5, 15/25/45 focus with 5-min rest |
| F1 | assistant + user flashing | persistent progress NVS, RTC/NTP trusted time, offline assets, privacy-safe messages and UI | reset/incomplete progress, offline/SD missing, fallback and USB restore |
| Q0 | user | 4h supervised bench soak, no unintended alarm/heat, clean print, 30 taps/RTC retention | gift-ready after all functional gates |
| O0 optional | assistant | OTA partition table/signing/rollback | upgrade/rollback ×5 with power interruption and USB rescue |

**Simple BOM (amounts are estimates not binding quotes):** board ₩80–110k; stand print ₩30–50k; pads/rubber/optional removable strips ₩5–15k; safe regulated power/insulated lead ₩11–21k; USB/CR927/SD re-use or +₩0–25k. Working budget ~₩150–180k, broad scenario ~₩126–221k plus international freight/reprinting, and tools if absent. [V15 CSV](../procurement/v15_desk_only_bom.csv).

**Do not tell a printer to make the simulated LCD.** Only the stand geometry in the `MODE="stand"` STL must be manufactured. Alternative B and C visualization modules are non-manufacturing concepts. The design render uses an approximated black case, not a measured OEM CAD revision. 
