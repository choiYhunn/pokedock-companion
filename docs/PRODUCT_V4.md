# PokéDock V4 — compact study companion

## Decision locked on 2026-10-05

PokéDock is a **compact daily study/desk companion**, not a wide charging tray.

### Physical layout
- **No front projection.** The base front edge ends almost flush with the display housing.
- The 4.3-inch HMI remains the visual center.
- The phone sits **behind the HMI on a simple sloped support**, not in a deep slot or pocket.
- A protected Qi charger/puck is mounted behind or inside that rear slope so the phone charges while parked out of sight.
- NFC/figure interaction moves to a **small side pod**, not the front.
- The side pod is parameterized for left/right placement; default is **right side**.
- Ambient LED is underside-only and subtle.

### Why this layout
1. Reduces desk depth.
2. Keeps the phone out of the direct line of sight during study.
3. Keeps the front visually clean so the screen/companion character is the focal point.
4. Physically separates the NFC antenna from the Qi coil.
5. Makes the NFC/figure interaction feel like an optional side accessory instead of a permanent control surface.

## Approximate mechanical targets

These are design targets, not machining dimensions.

- HMI visible width: around the actual 4.3C-BOX width; verify after the unit arrives.
- Main base width: HMI width + 4–10 mm margin.
- Main base depth: target **70–85 mm**.
- Front projection beyond display foot: target **0–8 mm**.
- Rear phone support angle: target **65–75° from horizontal**.
- Rear support thickness: 3–5 mm if printed/acrylic.
- Side NFC pod: target **35–45 mm wide × 45–60 mm deep**.
- Side pod front edge: no further forward than the main base front.
- NFC antenna center: as far from the Qi coil as the enclosure allows.

## Phone parking model
The phone is deliberately parked behind the display. It may protrude slightly above the display so it can be removed with one hand, but most of its screen is hidden.

The device UI is responsible for surfacing:
- incoming call indicator,
- user-allowed priority alert,
- next calendar reminder,
- charging / connection state.

Normal chat/social notifications should remain hidden in Focus mode.

## Charging
Qi is electrically independent from the ESP32 boards. PokéDock does not build the RF charging stage.

The rear slope should hold a removable protected Qi/Qi2 pad or charging puck. Exact coil position is tuned to the actual target phone before final mechanical assembly.

## NFC side pod
Default: right side.

The pod contains:
- NFC antenna / PN532,
- optional figure landing mark,
- optional status LED,
- Dock Node nearby if packaging is convenient.

It may be mirrored to the left in CAD without firmware changes.

## Product hierarchy
1. HMI screen / study functions
2. hidden phone parking + charging
3. side NFC/figure interaction
4. ambient light

The front face is intentionally clean.
