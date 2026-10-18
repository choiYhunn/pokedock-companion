# V14 mechanical design-for-manufacture contract

## Required real measurements
All lengths mm. Coordinate system: phone landscape long edge along X, positive Y rearward, positive Z upward, angle measured from horizontal. Use [measurement register](V12_MEASUREMENT_REGISTER.md); record *measured*, *manufacturer-published* and *assumed* values in different fields, with date/instrument and part revision.

| Feature | Unmeasured gate | Product consequence |
| --- | --- | --- |
| Phone + everyday case L/W/T | measure caliper to 0.1 mm practical repeatability | lower stop span / removable cushions |
| Camera island X/Y/Z and buttons | actual 14 Pro orientation + camera to left/right in landscape | anti-camera collision cutouts; avoid pressing buttons |
| MagSafe center, puck D/thickness, cable strain-relief/bend | real charger and orientation under charge | 2-axis adjust bracket, no rigid guessed 57 mm puck ring |
| HMI C-BOX actual outer / USB/SD/reset/DC access | inspect casing, OEM drawing, delivered revision | clearance envelope, no drilling / permanent glue |
| Rear screw inserts/count/centers/thread/effective depth | from delivered casing and OEM drawing | no guessed 75×75 mounting pattern |
| Desk rear clearance & friction, total assembled mass | physical measurements & smartphone repeated docking | anti-tip design and price |

**New secondary published clue:** RobotShop's 33630 specification states overall 116.30×79×18mm, **mount centers 75×39mm**, weight **163g**. This is distributor evidence, not final screw engagement/thread proof. Earlier mocked **four square 75×75 marker positions were structurally baseless** and are disabled. Never drill/print tapped holes until actual delivered housing confirms the hole count, 75×39 orientation, thread and safe engagement depth. Source: https://ca.robotshop.com/products/waveshare-esp32-s3-43-ai-voice-touch-display-development-board-800480-dual-microphones-wi-fi-bluetooth-5-w-case .

## Dry-fit / dimensions
Bare iPhone 14 Pro 147.5×71.5×7.85 mm/206 g (Apple published); +6mm total case allowance both dimensions is an **unverified sample**, giving 153.5×77.5mm. At 70° short edge projects **26.5 mm** into desk depth and **72.8 mm** upward. For assumed phone bottom Y=42,Z=7, screen 76° bottom Z=12, approximate front display top Z=88.7 versus phone top Z=79.8. Left/right overhang if both centered: (153.5−116.3)/2≈18.6mm. Eye-point concealment is **not proven** by top Z comparison. Sample B envelope 169.5×95mm =161cm², passive sample 169.5×82.5mm≈140cm². Width/depth include hypothesized structural/cable clearance, not build dimensions.

### Structure A (unpowered, must stand alone)
- A single shallow front display foot, open HMI rear attachment, **independent** rear phone support (two lateral ribs, low long-edge ledge), four nonmarking replaceable rubber feet.
- Mechanically join screen foot to rear ledge; screen is never a prop for the 206g+case phone. Don't rely on the MagSafe attraction to carry vertical phone weight.
- Phone contacts soft replaceable silicone/TPU pads on edge/support. Short end locators are small; keep hands and buttons free. No front-facing slide-out tray.
- Tilt 70° nominal, test 65/70/75. Backside no broad encapsulating panel, no hidden metallic plate near Qi, Wi-Fi antenna vents and all service interfaces exposed.

### Structure B (optional, same A plate)
- Factory sealed certified puck with **front face flush at case back**, adjustable normal stand-off and in-plane X/Z center. Clamp holder perimeter/back without blocking charging face or yanking captive USB-C cable.
- Camera island/puck/case thickness can make a flush plane impossible: don't force charging with extra gap and don't squeeze phone against camera bump.
- Removable retaining ring and protected cable exit; separate powered USB-C PD adapter. Detaching holder leaves a perfectly usable A.
- Adhesive-only mount, acrylic over charger face, solid insulating puck enclosure and 3D printed Qi coil are prohibited.

### Manufacturing route comparison
| Route | When to prefer | Main risk |
| --- | --- | --- |
| Cardboard/foamboard + clamp | first angle/hand-reach decision, essentially free | NOT load bearing |
| Small adjustable commercial tabletop phone stand + OEM display support | fastest honest fit/ergonomics benchmark; may be used as hidden internal brackets | may occupy extra depth; two standalone objects may fail seamless appearance |
| 2–3mm PC or acrylic flat plates, standoffs and small corner brackets | geometric brackets easy to laser-cut; less custom tooling | acrylic cracking at narrow corner holes; bend radius and edge finish |
| PETG 3D printed adapter/rails/holder only | hidden compound shape with custom C-BOX and removable charger fit | layer-direction weakness/creep, print distortion, unverified hole geometry |
| Full custom printed enclosure | ONLY if simpler route fails | thermal trapping, irreversible fit, cost/complexity increase |

**Favored**: hybrid commercial/flat material base plus **small** PETG interface brackets after measurement. Avoid paying to print 170×95mm decorative shell until physical location is proven.

### Fastener/fit policy
- Reserve nominal FDM test clearances only after measuring shrink/tolerance with a 20mm coupon; do not assume universal XY gap. Phone contact soft pad thickness test ~0.8–1.5mm (not a fixed clamp tolerance); replace when compressed or worn.
- No fastener head in direct glass/phone contact; stainless/brass inserts positioned far from Qi face; avoid metal across puck charging field.
- Screen's removable vendor insert screws: measure screw effective engagement; stop before any PCB penetration. Prefer detachable bracket that doesn't require opening electronics.
- Cable exit: plan independently for 33630 DC terminals (insulated), USB-C programming, reset/BOOT, SD, speaker and antenna plus finished MagSafe cable/USB-C plug. Route 12V HMI and PD cable in separate channels, optional common outer sleeve with no electrical splice.
- Slip/tip test includes touch on upper screen, rapid dock/undock 30×, light real desk bumps. Failure means widen low foot, move rear feet or reduce pickup magnet force; add mass only if measured moment requires it.

## QA record before fabrication release
Fabricator gets: exploded/case vs rail drawing, measured X/Y/Z datum table, verified C-BOX mount screw/thread, dimensional flat drawing (DXF) or printed adapter STL per selected process, bill of fasteners/material, actual view photos 65/70/75, 30-cycle and 60-minute power/heat proof, USB/SD reach photo. **If any are missing: no final fabrication release.**
