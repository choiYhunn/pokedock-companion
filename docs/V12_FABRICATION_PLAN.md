# PokéDock V12 — Production-style build package / fabrication readiness

**Status:** concept engineered + adjustable CAD + browser geometry calculator validated; **NO physical mockup, print-ready STL, load proof, board flash or charging-test evidence** yet.

## The manufactured object is 3 mechanical assemblies (keep it clean)

### S1 · OEM front panel mount
- Buy Waveshare ESP32-S3-Touch-LCD-4.3C-BOX SKU **33630**, not 4.3B or original 4.3.
- Keep OEM case intact; don't add a new thick decorative bezel. Front angle 76° from desk (trial range 70°–80°). Display should rest above a 5mm class low-profile foot.
- Support should fasten to the OEM **75mm rear pitch** only after **actual thread, insertion depth and mount offset** are measured. Don't drill the OEM case/PCB, and don't rely on soft double-sided tape alone to carry the display.
- Conceal fasteners/struts behind the existing case, leave terminal/USB-C/SD/RTC/speaker vents accessible and do not block Wi-Fi antenna.

### S2 · Reversible phone dock
- **Choose A first for footprint:** landscape iPhone behind display, 39° above desk. The magnetic charging face is on an *open removable* receiver on the rear cradle rails; cable runs rearwards.
- **Choose B if front appearance matters more:** portrait phone, 32° above desk. Deeper base, but narrower overhang.
- A regular iPhone 14 **bare** is 146.7 × 71.5mm. Large Plus/Pro Max and thick cases require substantially wider rails.
- **Do not use the phone as a structural support** for the screen. The screen and cradle each transfer load to the desk/base independently.
- Include a low-profile soft-lined edge stop as secondary protection; MagSafe grip is primary retention, and one-handed extraction must not pull the screen forward.
- Mount a complete finished certified MagSafe puck. Do not disassemble coil electronics, glue across the charging face or trap charger heat in print.
- Preserve camera bump clearance, case button clearance and Lightning port access. Puck center and holder diameter require direct measurement and active alignment test.
- Resting angle is adjustable only while fitting; final version uses whichever tested fixed-angle cradle was accepted.

### S3 · Quiet Desk base and cable management
- One slim rounded platform: warm-ivory front case above lavender/grey chassis.
- Separate display DC cable and USB-C PD/MagSafe cable inside an aesthetic rear cable sleeve/clip only; **electrical paths remain fully independent** with each external certified adapter.
- Rear anti-tip feet/support rails sized by actual iPhone weight + one-hand removal test, not a hidden counterweight/battery.
- Four replaceable soft rubber feet and two removable silicone contact pads; open gap behind screen and magnet charger for convection.
- Hidden underside personal date/initials label is optional and should not expose private details publicly.
- Right-side NFC disc/figurine pedestal and LEDs remain **optional detachable kits**, not permanent bulky features on core product.

## Envelope/cut dimension formulas

All values below are **computed reference envelopes**, not exact material cutting dimensions.

- Bare phone: L × W; add measured case allowances cL/cW. Lc = L+cL, Wc=W+cW.
- Phone width across base = Lc landscape; = Wc portrait.
- Phone run along slope = Wc landscape; = Lc portrait.
- Angle θ above desk.
- With phone lower datum y0 and height z0:
  - rear tip Y = y0 + run × cos θ.
  - top Z = z0 + run × sin θ.
  - base width = max(OEM_case_width + 16mm, phone_across + 16mm).
  - base depth = max(81mm, rear_tip_Y + 16mm).
  - display top Z = display_low_z + OEM_case_height × sin(front_screen_tilt).
- **Reference only:** regular iPhone 14, cL=cW=6mm, case W132/H86mm, y0=42mm, z0=11mm. For A θ39° → **~169 × 118mm**, B θ32° → **~148 × 187mm**.
- Reserve extra clearance for case thickness, camera, magnet, USB, rear feet, cable bend; these are not included in the rough envelope.
- Width overhang from a centered landscape phone can be max(0,(phone_across - OEM_screen_width)/2); reference ~10.4mm each side. Evaluate from normal seated and side views.

## Prototype cut/build specification (only AFTER measuring parts)

| Item | Planned stock / process | What final cut/drill file must contain |
| --- | --- | --- |
| Base plate | PETG 4–6mm test print **or** cut PC/acrylic 2–3mm plus support ribs | measured W/D/radius, rear relief, anti-tip structure, screw bosses; no hidden unventilated pocket |
| OEM rear adapter | PETG/bracket/aluminium plate as needed | exact 75mm pattern, hole diameter, safe screw length, surface offsets, terminal clearance |
| Phone rail and edge stop | PETG, surface silicone | measured phone case size, angle and camera clearance, bending stiffness/tipping proof |
| Charger holder | removable commercial holder or a measured open ring | exact puck diameter/thickness, cable-exit free bend, changeable fasteners, charge face not obstructed |
| Feet/contact pads | silicone/TPU adhesive/repositionable | pads at stable support polygon, phone/desk materials compatible |
| Cable guides | replaceable clips/sleeves, low-voltage only | rear port, separate power runs, strain relief, no pinched wires |
| Optional cosmetic label | small underside engraving/sticker | decorative only, no structural hole, no user secrets in shared CAD |

**FDM prototyping suggestions, not strength certification:** PETG with ~0.2mm layer heights, 3–4 perimeters, ~25–35% infill for a first *test part*; increase wall/gusset and reprint if flex/cracking appears. Avoid assuming PLA is suitable near a warm MagSafe puck. Test real heat exposure and plastic softening, never permanently embed the finished Qi transmitter.

## Assembly sequence on desk (production-like but reversible)
1. Manufacturer CAD: obtain original [4.3C 2D DXF/PDF and STEP](https://github.com/waveshareteam/ESP32-S3-Touch-LCD-4.3C/tree/main/hardware/dimensions) and compare to delivered C-BOX; measure screw types and ports.
2. Make **paper/cardboard shapes** for two orientations with real iPhone/case and the exact MagSafe. Record max rear depth, top concealment, side overhang, retrieval comfort.
3. Verify display factory firmware/RTC/SD with properly rated *separate* regulated board power and USB debug cable. Do NOT energize improvised electronics inside 3D print.
4. Build a simple adjustable screw-clamped jig or off-the-shelf small desk mount for trial, not a pretty one-piece monolith.
5. Run charger from its own certified PD adapter; 60min charge + 30 attach/detach cycles, tilt/tip and thermal check. Stop if phone or puck gets abnormally hot.
6. Confirm front-view shape is attractive from actual seated perspective, not just CAD orbit view. Choose A or B **only now**.
7. Freeze measured CAD, create split print parts/actual drilling templates with the OEM thread/hole and measured puck. Print test parts, clean edges, add rubber/silicone.
8. Mount display to OEM pattern, mount cradle load path independently to base, fit puck without glue onto coil face, route two cables out back, inspect ventilation/service access.
9. Power the Waveshare LVGL app and MagSafe simultaneously for >=60min; check Wi-Fi/RTC/screen touch while docking; accept only after post-assembly tests.
10. Only then add customized exterior surface/engraving; no bulky appendages.

## Pre-production exit checklist
- [ ] Actual screen C-BOX shape and rear screws measured against OEM STEP/2D.
- [ ] Actual iPhone variant, case and coil position measured.
- [ ] 39° landscape vs 32° portrait test with eye-level photos and footprint measurement.
- [ ] Phone stays attached after 30 one-handed cycles; does not tip/slide or snag buttons.
- [ ] 60min MagSafe+powered display heat/EMI/touch tests passed.
- [ ] USB, DC, SD, reset, RTC and speaker access preserved; no cable pinch.
- [ ] Screw lengths safe; no damage to OEM board/case/glass.
- [ ] CAD driven by measured parts, not sample numbers. Render + test print successful.
- [ ] Native device UI/clock/timer on actual board independently accepted.
- [ ] Battery/mains/electrical safety unmodified: only finished power adapters/puck.
