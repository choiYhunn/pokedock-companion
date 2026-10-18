> **ARCHIVED V13 — superseded by [V14 MagSafe-ready design](V14_MAGSAFE_READY_DESIGN.md). Latest confirmed iPhone is 14 Pro with MagSafe case, and V14 includes optional removable puck from the start. This file explains historical space-first reasoning, not build-ready dimensions.**

# PokéDock V13 — iPhone 14 Pro compact slot decision (2026-10-18)

## Decision: SPACE FIRST, CHARGING OPTIONAL

Recipient phone is confirmed **iPhone 14 Pro**, not generic iPhone 14. Keep the useful 4.3C LCD and Pokémon software. **Retire the long 25–39° portrait rear charging ramp as the default.**

**Preferred geometry:** a narrow, *landscape phone*, almost-vertical **65–75° slot immediately behind the existing screen**. Test 70° first, in real case. A gently tapered rear T-support gives room for the phone ends without a wide decorative front base. No forward tray, no bulky NFC podium. Use phone only as a removable guest in a separate structurally stable dock; its weight must not balance the screen.

**Product variant A (make FIRST): PASSIVE SLOT.** Simple padded open rear rails + shallow stop. No Qi electronics, no hot puck or second PD adapter, no untested "charging" indicator. A normal user-supplied Lightning cable can be connected by hand at the exposed landscape side if desired; don't hard-mount the Lightning plug.

**Product variant B (optional plug-in kit): REMOVABLE MAGSAFE CARRIER.** Attach an unopened reputable finished MagSafe puck to a measured open, vented carrier facing the **back** of the iPhone. Separate approved USB-C PD adapter. Do not bury puck behind a thick panel or metal plate. Leave rear access to remove/replace puck and reach phone. Test case compatibility/camera bump and heat. Keep base/rails identical to A if possible, so adding charging does not force a redesign.

## Verified outside dimensions
- iPhone **14 Pro bare**: **147.5mm L × 71.5mm W × 7.85mm thick, 206g**; MagSafe max 15W / standard Qi max 7.5W, Apple official: https://support.apple.com/ko-kr/111849
- Waveshare **4.3C-BOX SKU 33630 cased** official dimension diagram: **116.30mm wide × 79.00mm high × 18.00mm thick**; cased rear body back height ~74mm with 75mm mounting pitch. Manufacturer image: https://docs.waveshare.com/assets/images/Product-Example-4-34b9e7e7862afd8b0058300abaec3a00.webp and https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3C
- These values supersede V12 placeholder case W=132,H=86 and earlier false claims that 116.3×79 belongs only to the B version. C and B happen to have superficially similar external width/height; electrical design/SKU remains different.

## Geometry from the actual 14 Pro bare dimensions

For a landscape phone standing at angle θ above the desk, the phone's short side (71.5mm) determines height/rearward projection.

| Tilt | Vertical projection short side | Rear horizontal projection | Judgment |
| --- | --- | --- | --- |
| 60° | 61.9mm | 35.8mm | lower top, slightly more rear depth |
| **70°** | **67.2mm** | **24.5mm** | best first prototype |
| 75° | 69.1mm | 18.5mm | shallowest; needs stable magnet/stop/pickup testing |
| portrait at 32° | 78.2mm (using full 147.5mm long side) | 125.1mm | hidden-height comparison differs, **much deeper** in Y |
| portrait at 70° | 138.6mm | 50.5mm | narrow footprint but phone sticks way above screen |

Phone width across the desk landscape: **147.5mm bare** vs display **116.3mm** → **31.2mm greater width**, or **15.6mm per side** if centered. With case the protrusion grows. No flat rotation can magically hide the whole phone behind a smaller 116×79mm screen; concealment is a deliberate trade-off. Do not add oversized fake game-console side wings to pretend otherwise.

## Sample (NOT manufacturing) envelope

Assume **only for visualization:** iPhone case adds 6mm to BOTH length/width (so 153.5×77.5mm); rear lower phone edge Y=40mm from front reference and Z=7mm; screen bottom Z=12mm, screen tilt 76°; allow 8mm each side for wider rear padded arm and 12mm beyond rear tip.

- Landscape θ=70°: phone top height Z≈79.8mm, rear tip Y≈66.5mm. Screen top Z≈88.7mm.
- Width estimate max(116.3+16,153.5+16) = **169.5mm**.
- Rear-depth estimate max(70,40+77.5 cos70°+12)=**~78.5mm**, area **~133cm²**.
- These omit puck clearance, OEM rear terminal, support stiffness, cable bending, eye-angle/optical visibility, camera bump and anti-tip foot. **80–100mm overall depth is a planning target, not a guaranteed finished size.**
- A tapered front base can visually remain close to 125–135mm wide, while rear arm follows actual case width. The *bounding-box* desk footprint still counts the rear support and phone ends.

Prior V12 39° landscape sample ~169×118mm used wrong/unmeasured case dimensions and angle; V13 70° sample is estimated **~33% less plan area** than that reference, not proven in physical measurement.

## Internal spatial packaging
\`\`\`text
FRONT (user)
 [ 4.3C-BOX: 116.3 x 79 x 18 ]  <-- upright UI, clock/Pokemon
        | vent/access gap |
        | optional removable MagSafe puck facing rear |
   [ iPhone 14 Pro landscape ]     <-- ~154mm with sample case
      padded OPEN bottom stop
      wider rear tapered foot
BACK (cable exit)
\`\`\`

The phone back faces forward towards the charging puck; the iPhone display faces backwards. Confirm this is an acceptable docking action and that the camera area clears the front chassis/charger.

## Structural rules
1. Independent HMI and phone support; **never use the 206g phone or puck to prop up the HMI**.
2. Rear bottom lip should support weight when the magnet is absent; clamp/pinch-resistant soft pads, no forced Lightning plug.
3. Reversible MagSafe carrier clips into the same chassis only after the correct charger's diameter/cable exit and iPhone case are measured. Minimum air gap and no metallic obstruction per charger instructions; actual electromagnetic/thermal tests.
4. Keep USB-C debug, DC screw terminals, RTC holder, microSD and reset accessible; these are near back/bottom/side of the C-BOX. Never drill/alter OEM electrical enclosure without schematic/approval.
5. Validate side overhang, reachability, phone one-hand insertion/removal, tipping, and charge/heat with real phone + case at 65/70/75° and a seated viewpoint. Check 30 repeat cycles and 60min thermal charging.
6. **Decision to omit Qi is valid** if the slot is frequently used but charging is seldom needed or makes the rear cable too awkward. Core product remains a valuable clock/Focus/Pokémon desk companion without charging.

## Purchasing delta: DO NOT PRE-BUY CHARGER
- Phase 0: verify whether intended iPhone 14 Pro case is MagSafe-compatible and measure dimensions.
- Phase 1: HMI + correct power, cardboard 65/70/75° landscape slot; no MagSafe cost needed.
- Phase 2 optional: borrow/reuse Apple charger for 60min test, buy only if fit/temperature/space pass.
- Phase 3 (future): NFC and LED remain lower priority.

This is a revised engineering hypothesis, not a production sign-off, a working charging dock, or a promise that the iPhone will be completely invisible.
