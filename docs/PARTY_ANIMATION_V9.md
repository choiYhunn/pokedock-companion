# PokéDock V9 — Party Select and living character UX

## Goal
Move beyond one generic float animation. Every partner has a game-like identity and feedback, while the HOME clock and one-tap Focus remain stable, simple and practical.

## Live browser UX
- On HOME or Trainer choose **파트너 선택**.
- A new full-screen **PARTY SELECT** panel opens within the 800×480 device screen.
- Left side: numbered, scrollable party roster with selection arrow, party icons and active-partner heart.
- Right side: colored 2D game stage, animated pixel sprite, larger subdued illustration, glow, ground shadow, gentle sparkles and original dialogue.
- Eight selectable companions in user preference order.
- Each new preview has an entrance, animated idle/personal motion and description.
- Confirm triggers small win animation, then updates HOME / saves partner to browser storage.
- Controls: touch, Up/Down/Left/Right, Enter, Esc, close; **♪ optional synthesized sound is off until enabled**.
- On HOME an independent walking pixel buddy appears alongside the larger companion artwork. Pet tap produces heart/star feedback.
- Reduced-motion requests suppress animations and particles.

## Character differentiation

| Pokémon | Stage motion | HOME behavior | Feeling |
| --- | --- | --- | --- |
| Gengar / 94 | sneaks, peeks, flips direction | mischievous haunt / walks | playful secret partner |
| Piplup / 393 | double hops | hop | cute and lively |
| Togekiss / 468 | glides | gentle glide | calm |
| Lucario / 448 | stance, step, recover | focused stance | disciplined |
| Quagsire / 195 | slow wobble/squash | sway | relaxed |
| Togepi / 175 | generic bob | quiet | warm |
| Pachirisu / 417 | generic bob | quick | energetic |
| Jirachi / 385 | generic bob | slow | special day |

The pixel graphics are existing sprite resources for a noncommercial personal gift prototype, not original Pokémon graphics and not an indication of brand affiliation. Do not redistribute proprietary art without appropriate rights.

## Web vs physical device
**Web prototype implemented:** CSS stages, remote GIF pixel animations, gestures, party roster, persistence, optional synthesized SFX. These are browser features.

**Device portable policy implemented:** `partner_motion.h` provides motion cues (mode/duration/travel/frame budget) for five favorites and reduced-motion/focus/night suppression. A host C++ test verifies mapping.

**Device not implemented:** real ESP-IDF LVGL renderer, sprite assets packed for SD/PSRAM, sound codec control, real 4.3-inch touch QA, and OTA network update.

## LVGL port

1. Start from vendor LCD/touch BSP. Render HOME/clock/timer first.
2. Convert appropriate animated sprite frames into bounded frame sequences, rather than using browser CSS/GIF APIs on MCU.
3. Allocate image buffers carefully in PSRAM / SD; test double-buffer and DMA integration on actual board.
4. Animations should run only when idle, in character preview or after a user gesture. During Focus and Night remain static/very low activity.
5. Cap frame budget (4–8 key frames per gesture in portable motion policy), avoid continuous large GIF decode, test touch-to-response latency.
6. Keep a small static fallback per character. No Wi-Fi should be required for regular operation.
7. Make motion disableable from Settings; optional sounds remain silent by default.
8. Bench profile CPU use, heap low-watermark, SD access, audio glitches and thermal behavior over one hour.

## OTA

Refer to [proposed OTA architecture](../firmware/hmi/ota/README.md). The firmware would update app code/LVGL via dual OTA slots; future asset packs could change appearance without reflashing app, but only after atomic validation/swap is built. Neither path is implemented end to end yet.
