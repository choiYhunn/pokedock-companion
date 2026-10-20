# V16 Animation Production Contract — visual quality before feature count

## Visual target
- Main: Gengar as resident character; Piplup, Togekiss, Lucario, Quagsire as guests. All five have accessible deterministic selection, no forced random lock/unlock.
- Nintendo-like, clean 2D/small faux-3D styling, warm edge highlights and expressive silhouette. A fuzzy/soft material LOOK is an art style option, but not physically tactile.
- An image reflected from a flat transparent plate is NOT 3D volumetric; keep eyes, mouth, feet, facial motion LARGE enough to read under real desk lighting.
- Manufacturer display pixel counts do not guarantee optical resolution or effective luminance; do the 150/300/500lux proof with neutral exposure first.

## MVP per character
1. idle (loop 3-6s, breathing/float)
2. enter (0.5-1.0s, from left/right) / exit (0.5-1.0s)
3. reaction A (Gengar laugh, Piplup hop, Togekiss glide, Lucario pose, Quagsire wiggle)
4. reaction B (dance/spin/peek/celebrate) with 2-3s sequence
5. focus/clock specific motion (subtle and not visually distracting)
6. reduced-motion idle static fallback.
START WITH GENGAR ONLY until the optics gate, then all five. Don't multiply content before image quality works.

## File and runtime rules
- Author layered/vector 2D scenes in graphics software; export transparent PNG/WebP frames with common anchor, no black opaque rectangle.
- Preview local PNG/WebP sequence in v16/simulator (select current character, choose files; sorted filenames at 12fps). No upload, no hidden collection.
- Provisional source raster: 320×320 @24fps authored; downsample/hardware image size and actual frame cadence measured. Pre-render any expensive 3D motion on PC, not live on ESP32.
- MCU RAM calculation: one raw 320×320 RGB565 frame =204800 bytes; 12 uncompressed frames ~=2.46MB. Full 600×450 RGB565 framebuffer =540000 bytes; two ~=1.08MB. A 16MB flash image cannot simply embed long sequences for every character; use microSD/offline assets and partial/prefetch decode.
- JPEG drops alpha unless separate mask; render asset decoder and transparency AFTER vendor display is proven. The 24/30fps targets are goals and must be measured on 2.41.
- Avoid OLED static unchanging composition 24/7 at high brightness; shift subtly and dim at night to mitigate aging.
- Animation update pack: individual files + reproducible manifest + Ed25519 signature with private signing key kept OFF-device / OUT of Git. v16/tools/assets.cjs provides HOST signer+verifier, **not ESP32 on-device install**.
- Any Pokémon art/video or game audio remains private, permission-cleared or creator-owned; do not commit scraped/licensed franchise assets to a public repository.
- User's personal birthday voice/text goes into local user storage, never a public asset pack or GitHub action artifact.

## Creative acceptance
- Two distinct expressions recognizable in a normal desk light at 60cm.
- Idle motion non-distracting at a glance. Character visible behind transparent cover at ±20° from target center, if optical proof permits.
- Animation transitions no visible black-background rectangle, stutter, dropped frame burst, or seam.
- Quiet at night: no surprise alarm sound; explicit physical input for volume/mute.
- Delivery scenes: first boot invitation, normal daily idle, timer completion, private birthday reveal. All must work offline after first clock provision.
