# V16 Rev C — Design Lock Candidate and NO-GO Checkout Contract (2026-10-21)

**Decision:** Rounded hybrid Pepper's Ghost desk companion. This is a candidate product design, **not** final production validation, optical proof, checkout confirmation, or hardware-tested firmware. Do not buy a whole basket yet.

## Lockable choices
- Floating character only in the upper optical chamber; separate directly visible *rectangular* clock below. This avoids unreadable reflected time.
- Product silhouette: cream/ivory matte rounded rectangle, unlit clear cover, single quality encoder on right, restrained purple accent; no visible board, raw layer lines, phone holder or MagSafe.
- Main visual source: **Waveshare ESP32-S3-Touch-AMOLED-2.41 without case, PCB V2/Rev2.0**, 600x450, manufacturer-rated 800 cd/m², 8MB PSRAM, 16MB flash, RTC and TF/microSD, USB-C. Need vendor confirmation of exact version. No speaker onboard.
- Clock panel CHANGED: **Waveshare 2.42inch OLED Module white SSD1309**, 128x64, active **55.01x27.49mm**, PCB **61.50x39.50mm**, manufacturer USD12.99. Old 1.5inch SSD1327 was a **26.86mm square** and could not produce the wide mock clock. Factory default 4-wire SPI. Select default SPI with approved GPIO harness to avoid microscopic SMD mode-switch work, or have supplier deliver factory-configured I²C at extra cost; pin assignment awaits exact V2.
- One EC11-type push rotary encoder with a smooth rounded premium cap. Turn = select character/preset; short press = action/start; long press = settings. A real audible alarm requires separately verified active buzzer/driver; device default muted until explicit user configuration.
- Power: certified 5V USB from rear; no mains inside, no custom Li battery. RTC without verified backup loses trusted wall time after full power loss; NTP re-sync + explicit UNSET badge is mandatory, and genuine daily alarms cannot be promised offline after an outage until RTC backup is tested.
- Animations: Gengar fully featured first (idle/enter/exit/dance/hop/peek/celebrate); guest Piplup/Togekiss/Lucario/Quagsire 3–4 signature motions each. Black transparent source image with custom owned/permitted artwork. Pixel-art Showdown GIFs are reference prototypes, NOT final premium art and not licensed merely because they are on GitHub.
- OTA: user taps Settings > Update and explicitly confirms; firmware A/B rollback and asset manifest signature/atomic A/B replacement/USB recovery are required future **hardware acceptance**, not currently functional.

## Dimensioned geometric concept (not factory print fit)
Coordinate convention: front = -Y; Z up. Base **132W × 105D × 54H mm**, rounded 19mm corners, walls 3.2mm, floor 3.5mm. Clear cover **104W × 85D × 82H mm** external, target total **136mm**. Flat optical reflector **64W × 70H × 1mm**, initially 45°, but provide swappable 35° and 45° inner bracket positions after optical experiment; 30° is only a measured alternative, not presumed superior. AMOLED physical board 64x47.2x11.8mm bare; active panel ~49.65x37.22mm, screen UP in hidden base. Clock front bezel display window **56.5W × 29H mm**, OLED PCB 61.5x39.5mm behind it, not a 100mm-wide image. Encoder shaft center nominal X=47mm, Z=27mm; hole nominal 7.2mm pending encoder vendor drawing. USB rear notch 16x12mm conceptual; adjust for strain relief after real PCB orientation.

**Critical CAD boundary:** current Rev B and Rev C are single-piece, watertight *visual envelopes only*. Real PCB mounts, screw bosses, optical plate holder, hidden assembly fasteners, cable bend, air gap, cover adapter rim, tolerances, stress, electrical insulation and vendor manufacturability are NOT verified. Never place production print order from a conceptual STL.
- Use removable cover-to-base adapter ring and a replaceable reflector bracket to allow switch between stock clear enclosure and custom transparent cover vendors.
- Keep internal reflector FLAT; rounded acrylic must be outside the optical surface and not deform it.
- Prefer off-the-shelf polished transparent cover that physically fits, else outsource clear PMMA thermobending/polishing. Avoid transparent FDM as finished optical cover.
- Choose outsourced PETG matte FDM prototype first. Premium SLA/urethane smoothing or paint only after acceptance, not in revision A.

## Optical truth
Pepper's Ghost creates a **virtual 2D reflected image**, not actual volumetric holography. Nominal source luminance 800 cd/m² does NOT establish apparent image brightness, color gamut or 60cm viewing readability. Determine reflector transmission, reflectivity, wedge/double image and the viewer's seated angle using actual optics. The target apparent sprite height 35–45mm is near the physically displayed height ~37mm, not a 10cm avatar.
- Test at ~150/300/500 lux and 50/70cm, 0° and ±20°; FIXED camera exposure, no AI enhancement. Gengar eyes/mouth must be recognizable; repeat 30 continuous motions.
- A physical screen alone can be larger/brighter than its reflection. If 300lux fails facial recognition, try *one* larger/less reflective enclosure/plate combination, then exit to rounded direct AMOLED design rather than sinking money into optics.
- No claim from AI product imagery, CSS demo, or phone demo counts as physical approval.

## Minimum viable gift release
Clock (KST, NTP+RTC trust), Gengar high-quality silent motions, 4 guests, 15/25/45 focus and ordinary countdown, one alarm with user-configured mute/snooze, offline fail-safe theme, hidden birthday letter, simple Settings, physical press rotary. Prioritize clean startup, no surprise sounds/alerts, clear privacy erase.
Defer weather, music streaming, Todo, growth/gamification, second MCU, wireless charging, Bluetooth notification mirroring and environmental sensors.

## Concrete stop/go
GO to board-only test ONLY after zero-cost reflector experiment demonstrates optical promise.
GO to second-stage OLED, cable, enclosure quote ONLY after actual board reaches native 12fps and front OLED feasible.
GO to *full* checkout ONLY after all physical dimensions and at least two actual vendors quote the cover and finish, with cap confirmed by user.
Gift-ready only after 4h monitored thermal, 10 power cycles, 2 days daily use, five OTA fault/recovery tests and checked private assets.

## First-party references
- https://docs.waveshare.com/ESP32-S3-Touch-AMOLED-2.41
- https://www.waveshare.com/esp32-s3-touch-amoled-2.41.htm
- https://www.waveshare.com/wiki/2.42inch_OLED_Module
- https://www.waveshare.com/product/ai/2.42inch-oled-module.htm
- https://learn.adafruit.com/peppers-ghost-monster-eye
