# PokéDock V12 — QUIET DESK industrial design / physical baseline

> **Engineering baseline, NOT production-approved tooling.** Case, magnet puck, iPhone with case, fastener, thermal, line-of-sight, and structural load are still unmeasured. In the CAD, every HMI/phone/puck dimension except Apple bare-phone dimensions is marked a placeholder. Never order an STL, drill the Waveshare case or apply power solely from this file.

## 1. Product design intent (2026-10-18)

**Front:** a single small warm-ivory digital picture frame on a restrained lavender-grey base. Gengar character and playful details live primarily **on the display**. No oversized plastic Poké Ball, screen-side figures, huge bezels, LED-ring eyes, external wire mesh or protruding front phone tray.

**Back:** a phone dock formed by one or two unobtrusive open support rails and a **separately purchased finished magnetic charger**. Puck has a removable mount with cooling/strain-relief space. Use the OEM screen's existing rear-mount geometry if compatible. No irreversible changes to the original screen or MagSafe charger.

**Bottom:** softly rounded small platform; two rear anti-tip feet only as far as actual tipping tests require; rubber anti-slip feet; exit two separately powered cables towards the back, clipped together for aesthetics but **electrically separate**.

### Appearance
| Element | Proposal | Reason |
| --- | --- | --- |
| Cased front HMI | keep OEM housing, matte warm ivory (#EAE6DF) *accessory* trim | least custom tooling and heat risk; do not coat vents/LCD |
| Structural stand | muted lavender-grey (#A69BB3) PETG or finished aluminium/acrylic | unobtrusive, partner-compatible |
| Protective interfaces | thin light grey replaceable silicone/TPU pads | avoid phone case scratches and rattles |
| Visible light | no always-on LED, only optional underglow after Night tests | looks like a product, not a toy PCB |
| Decorative detail | tiny embossed heart/ghost motif on underside only | keeps the outside clean and couple meaning private |
| Fasteners | rear-hidden, serviceable | screen/puck/cable replaceable |
| Shape | rounded 8–12mm radii on base edges, no sharp corners | small desk gift aesthetic |
| Exterior | NO large NFC pedestal initially | physical simplicity; detachable side NFC in Phase B |

## 2. Footprint decision: space-first default / hide-first alternative

Use [interactive desk footprint calculator](../design.html) and the [CAD envelope](../cad/pokedock_v12_quiet_desk.scad).

**Reference assumptions for comparison only:** generic 4.3C case 132 × 86 mm (NOT verified!), iPhone 14 **bare** 146.7 × 71.5 mm (Apple official), extra case allowance 6mm each dimension (NOT verified), phone lower support at y=42mm and z=11mm; display bottom at z=18mm, screen angle 76°. Base side margin 8mm; rear clearance 16mm.

| Option | Orientation, inclination from desk | Approx. base W × D | Approx. area | Important tradeoff |
| --- | --- | --- | --- | --- |
| **A / default** | Phone horizontal (landscape), 39° | **169 × 118mm** | **200 cm²** | ~10mm each side could show beyond case; landscape MagSafe, case/camera and one-hand access need testing |
| B / concealed-front | Phone vertical (portrait), 32° | **148 × 188mm** | **278 cm²** | phone width hides more easily but requires ~70mm more rear desk depth |
| C / compromise | Portrait, ~38° | ~148 × 179mm | ~265 cm² | slightly less rear depth but taller phone may overtop or show at seated viewing angle |

These are envelope calculations, not measured finished products. Using the sample assumptions A reduces projected footprint ~28% vs B. **We are not claiming it hides the phone at all seated eye angles**: side edges may be visible in landscape; the real camera bulge and puck change placement.

**Default candidate A only if** actual iPhone+case can be aligned with the selected magnetic puck in landscape, its camera cluster does not hit support, and the exposed margins remain visually acceptable. Otherwise move to B rather than adding ugly wide side wings or deep front decorations.

## 3. Physical source of truth and fastening strategy

Official manufacturer for exact board family: [Waveshare 4.3C wiki](https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3C) and [Waveshare original dimensional drawings](https://github.com/waveshareteam/ESP32-S3-Touch-LCD-4.3C/tree/main/hardware/dimensions). These include product 2D DXF/PDF and STEP for mechanical reference. **Do not confuse with 4.3B (116.3×79mm cased) or original 4.3 (106.1×67.8mm) dimensions.**

The manufacturer lists a **75mm rear mounting hole spacing** for the cased 4.3C. This is enough to explore a behind-the-screen bracket, but NOT enough to presume a VESA-standard screw thread/insert depth. Determine four relevant mounting locations, hole/thread diameter, maximum insertion depth and surface offset from actual PDF/DXF/STEP *and the shipped unit*. In CAD, \`SCREW_HOLE_D=0\` disables any drilling until verified. Attach screen to a removable rear bracket rather than clamping exposed glass. A commercial small 75mm mount is a viable **bench-only** stand if it fits the actual inserts.

## 4. Mechanical component breakdown

| ID | Part | Preliminary design method | Quantity | Prototype process / verification |
| --- | --- | --- | --- | --- |
| M01 | Cased HMI | OEM Waveshare **4.3C-BOX SKU 33630** | 1 | Keep case intact, measure mounting and every port |
| M02 | Base platform | rounded PETG 4–6mm plate or 2–3mm cut acrylic on a ribbed support | 1 | Start cardboard; load case+phone; rear depth per A/B |
| M03 | Rear HMI mount | removable frame/struts to OEM 75mm pattern | 1 | Thread and insertion depth TBD; screw spec not set |
| M04 | Phone support | two open rails + small silicone-lined lower stop; no full hot insulating cradle | 1 | mockup at A 39° or B 32°, camera clearance |
| M05 | MagSafe puck holder | replaceable open ring/clamp or rated commercial puck receiver, centered to **actual phone coil** | 1 | Puck diameter, thickness, cable exit TBD; no glue on charge face |
| M06 | Anti-tip rear feet | pair under support near rear-most point; rubber pads | 2 | choose size only after mass/dock/undock tests |
| M07 | Cable clips | rear adhesive/mechanical strain-relief, power separation | 2–3 | MagSafe USB-C remains accessible and uncut |
| M08 | Surface pads | replaceable silicone/TPU contact pads | 4–8 | adhesive compatibility, no blocked heat |
| M09 | Hidden personalization | small underside engraved plate / sticker only | 1 | optional, nonstructural |
| M10 | Detachable NFC platform | future small round pod right/left | 0 for MVP | later battery-free figurine tag read test |

**CAD files are not print-ready:** No real mounting holes, case occlusion holes, charger cradle capture geometry, heat-rating, screw-boss insert design, pull-off test or wall-stress validation is present. OpenSCAD is an adjustable **concept assembly and envelope**. Making these details up before measurements increases failure risk.

## 5. Mechanical assembly architecture

1. OEM case kept as-is. Mount back of display on measured rear pattern using actual OEM-compatible machine screws/spacers with controlled insertion length; *do not drill PCB or glass*. The rear bracket connects to the rounded base via a light braced frame.
2. Mount phone support independently to the **same base**, not as a load dangling off the LCD's case screws. A phone pull-off generates transient bending moment; dimension rear feet using load/anti-tip test.
3. Puck lives in a replaceable carrier on support at phone coil center. Charging face remains flush/exposed; rear stays ventilated. Route cord along rail to rear exit with bend radius and strain relief. Remove for service.
4. Lower phone edge touches two soft pads/low-profile stop, never a deep trapping sleeve. Side buttons/Lightning/USB and cameras remain clear.
5. The front surface reveals only the screen and very shallow mounting foot. Both charging and display power adapters are placed outside the device housing as certified, separately insulated units.
6. NFC/LED subassembly is a nonstructural, detachable later addition.

## 6. Assembly/manufacturing stages and deliverables

- **D0 geometry**: fill precise [measurement register](V12_MEASUREMENT_REGISTER.md), including phone case/coil and OEM case fastening pattern; measure target desk depth.
- **D1 ergonomic proof**: cardboard/foam 2 angle versions at eye-level / looking-down angle; insert finished MagSafe puck with removable fasteners; no permanent print.
- **D2 electrical/proof**: separate certified supply bring-up, 60min phone charging, heat, stability; record one-hand 30 cycles.
- **D3 mechanical prototype**: import OEM STEP from manufacturer to Fusion/FreeCAD, replace the rough cuboid with actual case, measure ports and bracket footprint, update SCAD parameters.
- **D4 first production-like sample**: print PETG or cut acrylic; machine holes only after certified source dimensions and measured screw specs; inspect sharp edges, strength and access.
- **D5 integrated**: run 60min LCD+phone+touch+Wi-Fi, no wobble, heat or abnormal cable strain; confirm final acceptance/photo from intended seated viewing position.

## 7. Safety and product logic

- **No shared DC positive rails.** OEM board uses documented 7–36V DC terminal (check exact PCB polarity/supply on unit); MagSafe requires separate suitable USB-C PD adapter. Do not feed phone charger through ESP32 pins.
- Display back, microSD, RTC, reset, USB, vents and antennas must remain accessible.
- Do not classify phone proximity as actual charging/battery level.
- If phone is bulky or case magnet weak, external MagSafe holder may be unsafe; change geometry/puck and re-test or omit integrated charging.
- Do not rush polishing to cover up a thermal or tip instability issue. Display useful core software offline before adding decoration/NFC.

## 8. Source & references
- [Waveshare product 4.3C cased](https://www.waveshare.com/product/esp32-s3-touch-lcd-4.3c.htm)
- [OEM 4.3C mechanical reference directory](https://github.com/waveshareteam/ESP32-S3-Touch-LCD-4.3C/tree/main/hardware/dimensions)
- [Apple iPhone 14](https://support.apple.com/ko-kr/111850), [Pro](https://support.apple.com/ko-kr/111849), [Plus](https://support.apple.com/ko-kr/111854), [Pro Max](https://support.apple.com/ko-kr/111846)
- [Official MagSafe charger](https://www.apple.com/kr/shop/product/mgd74kh/a)
