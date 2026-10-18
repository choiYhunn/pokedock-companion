# PokéDock CAD — active mechanical baseline V14

**Canonical 2026-10-19:** `pokedock_v14_magsafe_ready.scad` is the **visual envelope / nonstructural mock** for iPhone 14 Pro + MagSafe case in a 70° landscape rear slot. Charger holder and screen fasteners **have NOT been mechanically defined/validated**. Do not export this mock as a production STL or drill the OEM screen enclosure using its marker positions.

## Useful CAD artifacts
- [V14 design mock](pokedock_v14_magsafe_ready.scad): phone + OEM C-BOX + separable charging puck visual references, assumed geometry and 170×95mm sample bounding-box.
- [V14 cardboard templates](pokedock_v14_dryfit_templates.scad): selectable 1:1 65° / 70° / 75° side profiles, case/HMI rectangles, 100mm printer calibration rule. **Only for paper/foam mockups, not load-bearing parts**.
- [Manufacturing blockers and dimension register](../docs/V14_RELEASE_AUDIT.md): to resolve before final connectors, holes and clipping mechanisms.

## Past CAD (reference only)
- `pokedock_v13_compact_slot.scad`: passive first concept, not latest.
- `pokedock_v12_quiet_desk.scad`: prior 39°/32° A/B orientation mock, superseded.
- `pokedock_v11_fit_mock.scad`, `pokedock_v4_compact.scad`, `pokedock_v2_base.scad`: historic fit/shape studies. **Do not order Samsung EP-P2400 Qi charger** from V2; not part of V14 product.

## Actual fabrication checklist
1. Delivered HMI SKU/revision, mount hole count and centers, thread and safe depth, SD/USB/DC/reset and antenna areas measured.
2. Actual phone+case L/W/T and camera offset measured, actual finished MagSafe puck D/T/bend exit measured. No '57mm' guessed puck fixture.
3. 65/70/75° cardboard mock tested by hand with phone, 30 dock/undock and powered 60min heat when optional charger installed.
4. Parameter values and fit clearances updated; mechanical load path and phone ledge verified **without a magnet**; retaining ring two-piece, replaceable and ventilated.
5. Only then export revised manufactured part files and obtain test cut/print quote. Preserve OEM case, service access and separate certified power domains.

Waveshare official uncased PCB DXF and STEP: https://github.com/waveshareteam/ESP32-S3-Touch-LCD-4.3C/tree/main/hardware/dimensions — **not proof of the delivered cased 33630 mounting interfaces**.
