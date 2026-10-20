# V16 Build and Fabrication Plan — NO ORDER without G1 optical sign-off

## Conceptual envelope (NOT fit-verified)
- Base envelope 132x97x47mm with 20mm-radius outer corners (ivory matte). CAD mock: cad/ghost_v16_concept.scad.
- Chamber target outer envelope ~103x77x82mm; internal reflector FLAT ~45deg; corner radius is on the transparent dust cover, not the image reflector.
- Target assembled height ~129mm (may grow after actual board mechanical dimensions). **DO NOT PRINT CONCEPT AS A FINAL ENCLOSURE.**
- Accessible rear USB-C, non-slip silicone feet, serviceable hidden screws, one pressable encoder, dark hidden optical cavity, white/cream front clock window.
- Whole device should look intentional even when OFF: no bare dev board, 3D print layer lines, visible tape, uncovered LEDs or wires.

## Gate-driven assembly order
P0 Zero-spend optical bench: phone screen with solid black background, character silhouette/clock test image, flat PET/acrylic 45deg sample; control viewing distance 50cm/70cm and 150/300/500lux. Document exposure and 3 observing angles. DO NOT simulate this in software and call it proven.
P1 Measure: buy optical board ONLY if P0 acceptable, record board active panel/case/PCB revision and required mounting clearances; test vendor example before any custom electronics.
P2 Digital model Rev B: replace generic chamber, screen, USB and OLED placeholder volumes with *measured* dimensions + actual mounting approach; confirm beam splitter view cone and no edge distortion.
P3 Outsourced prototype: ask printer for one base in smooth matte finish (SLA resin or professionally finished FDM), separate optical plate/canopy made to fit. Request sample photos, finish quote, tolerances, vendor-required file and one replacement policy.
P4 Dry fit: no glue on optical face; disassemble/reassemble 10x; check clock face visible at 60cm in normal light, power cable strain relief and full-foot stability.
P5 Electrical: certified 5V USB supply; no 220V mains inside; verify regulator, GPIO, SSD1327 serial-mode switch, physical button, power consumption.
P6 Firmware: boot scene, clock read from verified trusted RTC/NTP, face and motion, focus state/mute/alarm, offline fallback, data clear and no automatic OTA.
P7 Gift finish: labels hidden on rear; dedicated packaging, private letter stored locally (no public logs), thermal 4h supervised, power-cycle x10, daily-use x2 days, strong safety checklist.
P8 Update verification: user taps update, release metadata/signature, inactive app slot, boot health check/rollback and USB rescue; pack switching uses A/B assets. Five interrupted/failed upgrade cases must pass before enabling update UI.

## Outsource brief (to quote only, not send blindly)
One rounded desk-object housing, 132x97x47mm *preliminary* base, neutral matte ivory, no visible strata, flush 1.5in front window, hidden rear USB access, one side/top encoder, internal opaque optical-light cavity and flat clear reflector support. Manufacturing file and contact surfaces remain pending physical measurements, so request feasibility and expected finishing cost only; do not promise a final STL.

## Stop conditions
Reject if 2.41 projected image still too dull at 300-500lux, external panel makes it look like table-order equipment, front clock too small, enclosure requires unshielded power wiring, BOM exceeds user-approved budget, or secure OTA cannot be proven. Existing V14/V15 effort does not change these gates.
