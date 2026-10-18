# PokéDock V11 — Dimensioned mechanical engineering process

## Critical contradiction to resolve before paying for printing
Original V4 CAD hardcoded BASE_D=78mm and PHONE_SUPPORT_H=82mm, while even the bare regular iPhone 14 is **146.7mm tall / 71.5mm wide / 7.80mm thick** (Apple: https://support.apple.com/ko-kr/111850).
An upright phone tilted **65° from horizontal** has projected height ~133mm, meaning it will visibly rise above a typical 4.3" display body. Tilting to 25–30° reduces height to ~62–73mm but extends phone depth rearwards ~127–133mm, *plus bottom offset, case and stand*. Thus "mostly hidden behind screen" and "base overall depth 78mm" cannot both be assumed true. Front tray still unnecessary; rear desk depth must be measured.

## Coordinate convention and sketch

- X = left/right across desk, Y = from front toward rear, Z = upward.
- Display is in front, facing viewer; rear phone's **back** rests against a rear-facing MagSafe puck held on a sloped open support.
- Phone must not be covered by the display's back plate at the charging coil/camera bump; MagSafe ventilation stays open.

\`\`\`text
SIDE (not to scale)                   front / user ←             → rear
                         display
                           /
 desk  __________________/_____(front base)_________________________
                                \\ phone at angle 25–35 degrees
                                 \\   MagSafe puck faces phone back
                                  \\________________(rear leg/foot)
          NO forward-extending phone tray. Rear cradle is removable.
\`\`\`

## Engineering math — first estimates, then physical mockup
Let H be phone length **including case**, θ the tilt **above desk plane**, and y₀,z₀ the lower support position.
- approximate phone tip height z_tip = z₀ + H sin θ.
- approximate tip rear location y_tip = y₀ + H cos θ.
- actual overall rear footprint also includes support feet and charger cable strain relief.
- require tip height not exceeding front case obscuring height if truly hidden, or consciously accept a visible strip.
- tilt too low makes the phone awkward to reach; tilt too high exposes it. Test 25°, 30°, 35° on folded cardboard.
Example using **bare iPhone 14** H=146.7mm (exclude case): 25°→62.0mm high / 133.0mm rear extent; 30°→73.4mm / 127.0mm; 65°→133.0mm / 62.0mm. This is only a projection, not enclosure dimensions.

## Actual measurement form — fill in before fabrication

| Input variable | How to obtain | Measured (mm) |
| --- | --- | --- |
| \`CASE_W\` / \`CASE_H\` / \`CASE_D\` | Physical Waveshare 4.3C-BOX including bezel/case; caliper 3 times | TBD |
| Screen bezel viewable W/H | measure active display opening without counting rounded corners | TBD |
| Display lower edge/tilt + button/port exit | measure from desk datum | TBD |
| \`PHONE_W\` / \`PHONE_H\` / \`PHONE_T\` | Real phone WITH normal MagSafe case and thickest camera protrusion | TBD |
| Exact iPhone model and case SKU | Settings → General → About; read case label if available | TBD |
| \`CHARGER_D\` / \`CHARGER_T\` | Actual protected MagSafe puck including charging face and cable bend relief | TBD |
| Phone coil center-to-bottom | align actual puck against phone and mark center before cutting | TBD |
| NFC card read offset | test PN532 while MagSafe actively charging (phase B) | TBD |
| DC terminal, USB, RTC, microSD and speaker/case exits | check delivered PCB revision and enclosure access | TBD |
| Desk depth/width limit | measure target desk and cable clearance | TBD |

Tolerances for first **removable prototype**, not molded shell: start around +1–2mm clearance at nonprecision locations, soft pads for gap stack-up. Do not invent screw-hole centers or force-fit MagSafe; fit is accepted only after repeated physical docking.

## Mechanical configurations to prototype
A. **Portrait low angle (preferred first trial):** 25–35° from desk. Compact height but long rear projection; keep cable and air channel open.
B. **Landscape phone behind screen:** may reduce required vertical height, but 146.7mm long phone may exceed front screen/case width; MagSafe alignment and pickup ergonomics differ. Test with actual iPhone and case.
C. **Partly visible portrait:** higher angle, less rear depth; explicit compromise if unobtrusive hidden design is not ergonomic.
Reject any option where camera bump loads the puck, charging falls out with a desk bump, or phone cannot be pulled off with one hand.

## First physical mock: 90 minutes, no 3D printing
1. Place real 4.3C-BOX case against an adjustable desk stand.
2. Cut cardboard/PVC foam core test ramps at 25/30/35°, tape **only to supports, never directly onto a phone battery or exposed charger wiring**.
3. Attach a *commercial, fully enclosed* MagSafe puck with removable fastener and measure actual magnetic alignment.
4. Put iPhone in ordinary case, position on ramp, test USB/puck cable paths, camera clearance, touching panel while removing phone.
5. Photograph profile at eye level; measure rear depth and phone overhang/visibility.
6. Dock/undock 30 times, tap desk lightly, check slips; collect thermal temperature after 60min charging in a ventilated environment.
7. Mark chosen dimensions on paper; verify case terminal/reset/SD remain accessible.
8. Only now update \`cad/pokedock_v11_fit_mock.scad\` with measured variables, generate 3D preview, and commission acrylic/printing.

## Manufacturing proposal after fit verification
- Build removable **front screen holder** for the purchased plastic-case 4.3C unit; no raw LCD adhesive/pressure.
- Rear support: two rounded nonconductive rails/spine, rubber-lined lower stop, open center for finished puck, rear counter-foot sized from tipping test.
- Base: 2–3mm prototype acrylic/PC or 3D printed PETG; rubber feet, rounded accessible edges, no finger pinch/trapped cable.
- Use screws/inserts only in the *new support*, not drilling the Waveshare PCB/enclosure unless explicitly approved by drawing.
- Keep charger removable for replacement/heat.
- Any printed part near charging coil must respect charger manufacturer's heat/airflow instructions.
- NFC side pod is a detachable optional upgrade; prototype the right-side placement after NFC and MagSafe interference testing.

## Fit CAD status
\`cad/pokedock_v11_fit_mock.scad\` is **not print-ready**. Its CASE/PHONE/CHARGER values are explicit SAMPLE placeholders. It computes rear projection and displays conservative geometry; no holes, cable relief, structural strength or actual Qi pocket has been validated. Old V4 SCAD is deprecated as a concept-only sketch.

## Physical acceptance
Pass only after no dangerous wobble, no slip through thirty attach/removals, 60 minutes stable power/thermal behaviour, actual eye-level hidden/visible phone appearance accepted, night screen view comfortable, wires accessible and recoverable.
