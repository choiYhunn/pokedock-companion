# PokéDock V14 — MagSafe-ready compact industrial design (2026-10-18)

## Confirmed facts vs assumptions
| Fact | Status | Source |
| --- | --- | --- |
| Recipient phone | **iPhone 14 Pro** | User confirmed |
| Daily phone case | **MagSafe compatible** | User confirmed (exact case brand/model and thickness remain unknown) |
| iPhone body | **147.5×71.5×7.85mm, 206g** | [Apple specs](https://support.apple.com/ko-kr/111849) |
| Phone charge ceiling | **up to 15W MagSafe** (7.5W generic Qi) | [Apple specs](https://support.apple.com/ko-kr/111849) |
| Display | **Waveshare ESP32-S3-Touch-LCD-4.3C-BOX, SKU 33630** | [Waveshare official](https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3C) |
| C-BOX external envelope | **116.3×79×18mm** published casing diagram | [Waveshare official](https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3C) |
| Physical phone+case size, puck diameter, mount threads, stand desk clearance | **TBD — MUST MEASURE** | No physical prototype yet |

## Product choice
**V14 base product:** a modest 4.3-inch screen in front + independent narrow *landscape* iPhone 14 Pro support behind the screen at approximately **70° to desktop**. A fully enclosed, verified MagSafe charger sits on a **removable, open-backed adjustable puck carrier** attached to the rear support. The baseline product still stands perfectly well with the puck removed; phone lower lip supports weight even without magnetic grip.

This is **one product** with optional charger, not a deep portrait ramp / front phone tray / a thick custom enclosure. The front screen retains its OEM enclosure and its own structural support. All Gengar play stays on the LCD, no oversized external Pokémon plastic decoration. Need nothing taller than the 4.3-inch screen except perhaps a small portion of the iPhone/case at actual viewing angle.

### Eye-level visibility truth
A centered landscape iPhone bare body is 147.5mm long across desk vs 116.3mm screen → **15.6mm overhang on each side**. A sample +6mm total case allowance means 153.5mm and **18.6mm each side**. This is NOT invisible: accept neat symmetric wings of phone, avoid large cosmetic fake side walls that make overall width worse. Place the smartphone centered; do not promise perfectly hidden from every seated eye line. Puck must be positioned at the actual phone's magnet center while case is on.

### Structural stack, front→rear (not to scale)
\`\`\`text
                      VIEWER / FRONT
  [116.3 wide HMI case, tilt about 76°]
          ║ OEM mechanical rear attachment ║
          ║ (free space: DC/USB/SD/airflow) ║
       [open adjustable puck carrier]  ← charger face points toward phone back
           ⭕ protected MagSafe puck      ← its USB-C cord exits rear/down
       [iPhone 14 Pro + MagSafe case]   ← phone rear contacts puck
           ╲ 70° from tabletop
      [soft lower lip, two side locators]
       [rear rail/foot supports ≥206g+case]
                     BACK / CABLE EXIT
\`\`\`

Phone is neither an HMI prop nor a built-in charging transmitter. Phone screen facing toward the rear is expected. Rearward pickup is by grasping the two exposed phone edges; the hardware must resist being tugged over during one-handed removal.

### Reference geometry — sample only
The bare phone's **short edge 71.5mm** is its slope length in landscape. With a fictitious case total +6mm (77.5mm), 70° tilt, lower support Y=42mm Z=7mm:
- horizontal projection 77.5×cos70° = **26.5mm**;
- vertical projection 77.5×sin70° = **72.8mm**;
- tip Y=68.5mm, Z=79.8mm.
The C-BOX reference front with bottom Z=12mm, tilted 76°, gives top Z≈88.7mm. **This only compares vertical coordinates, not optical hiding.**
- bare handset + sample case across the desk: 153.5mm.
- support envelope min width if adding 8mm per side = **169.5mm**.
- with mechanical support, USB-C bend relief, cable route and anti-tip margins, **target full desktop envelope about 170–180mm wide and 90–115mm deep**. It is a design target, NOT a CAD-cut spec or promised manufacturing size.
- Real physical size may exceed it, in which case increase tolerance or **omit charger**, not squeeze cables/case.

### Key component split
| Code | Qty | Item | Prototype structure | Hard constraint |
| --- | --- | --- | --- | --- |
| P01 | 1 | OEM 4.3C-BOX | Unmodified existing enclosure | 7–36V input, USB/debug/RTC/SD accessible |
| M01 | 1 | Front support / rear adapter | Bolt into verified OEM 75mm-pattern inserts only AFTER measuring hole/thread/depth | never drill PCB or use guessed screw length |
| M02 | 1 | Slim anti-tip base | PETG plate ~4–6mm as prototype, or PC/acrylic supported plate | rounded edges, rubber feet, no rocking |
| M03 | 1 | Landscape phone ledge | open soft-lined lip + two end stops, ~70° | handles phone without magnet, no Lightning button/camera clash |
| M04 | 1 | **Adjustable MagSafe puck saddle** | 2-piece removable open ring / compatible commercial puck holder, slotted adjustment | coil contact must be flush; vented, no glue/metal covering charging face |
| M05 | 2 | Rear strength ribs | connected to base on actual rear load path | no wobble/tipping under one-hand extraction |
| M06 | 4+ | Silicone/TPU pads and 4 desk feet | replaceable, non-scuff | don’t press camera bump or cover puck contact |
| M07 | 2 | Cable clips / strain relief | rear low-voltage cords only, separate power supplies | don't crimp fixed MagSafe cable |
| M08 | optional | Small underside personal marking | engraving or removable adhesive motif | no private data in public CAD |

### Adjustable MagSafe construction (do not lock before measurement)
- Use **the charger itself as a real fit gauge**. Current official Apple 1m MagSafe charger (SKU/current listing A3502, 2025 device revision) is a complete finished puck, not a bare wireless coil. Do **not** hardcode a 57mm diameter as its real dimension; previous SCAD 57/6 was a sample.
- The puck's charging face and the iPhone's case back must contact. The CAD holder must retain only the housing perimeter/back, NOT cover the front face or press its cable joint.
- Set initial adjustable carrier travel ~4–8mm **as a prototyping design allowance**, not a permanent fit tolerance; adjust normal offset and vertical coil position from a marked physical alignment test. Final travel/ring width are measured.
- Include underside/rear path for cable exit with bend-relief from the *actual* puck. Neither the phone nor board supplies the puck's USB-PD power.
- Place MagSafe so the iPhone 14 Pro camera island clears all brackets/rails in either landscape orientation; choose which side camera rests on by actual phone placement.
- Airflow behind the OEM screen and around puck must remain unobstructed. Mount charger and screen as separately replaceable items.

### Design language
Front: matte warm ivory accent (#EAE6DF), quiet lavender-gray structural rear (#A69BB3), discreet Gengar only on screen. Small flat foot silhouette; avoid front-projecting catch tray, full-width shell, side ornament, glowing halo, exposed MCU/sensors. Back: two tidy independent exits (HMI regulated DC & USB-C PD puck); they may share an outer cable sleeve but NOT electrically connect.

## Physical verification gates
1. **Fit** — exact MagSafe case, real charger/cable, OEM screen and current desk. Build card/foam trial **65° / 70° / 75°** and photograph front/side/top at actual seated viewpoint.
2. **Alignment** — real phone visually charges at chosen orientation; cable does not pull puck off contact; camera doesn't ride on rail.
3. **Ergonomics** — 30 attach/remove cycles one hand, no tipping, no screen shift/accidental touches; alignment still good.
4. **Thermal/power** — 60min phone charging with screen powered, no overheating, enclosure vents unobstructed and no unexpected LCD/Wi-Fi problems. Stop on heat/error rather than inventing an allowed case temperature.
5. **Access** — can reach microSD, DC power terminal, USB debug/recovery, reset, speaker, MagSafe cord without opening sealed chassis.
6. **Repeatability** — detach charger and phone, keep screen useful, then reattach puck and repeat charging proof.

## Final CAD sign-off is BLOCKED until
actual iPhone+case L/W/T, camera bump and coil center, OEM case ports/75mm screw thread/depth, actual complete MagSafe puck size and strain relief, cable route, screen-stand and phone-stand connection loads, print/process strength, and actual physical trial results. Do not label present OpenSCAD as ready STL.

References:
- Apple 14 Pro: https://support.apple.com/ko-kr/111849
- Apple MagSafe store (1m): https://www.apple.com/kr/shop/product/mgd74kh/a
- Apple charger guidance: https://support.apple.com/ko-kr/105047
- Waveshare: https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3C
