# PokéDock Companion

A compact Pokémon-themed **study / desk companion** built around a 4.3-inch ESP32-S3 touch HMI.

## Live UI Lab

**https://choiyhunn.github.io/pokedock-companion/**

The Pages site is not just a landing page. It is the current visual review environment:
- coded V4 product visualization,
- coded V4 structure poster,
- interactive 800×480 device mock,
- 15 complete screen concepts,
- working Focus / Timer / Stopwatch simulation,
- phone parked / priority alert / Night / NFC / Birthday state simulation.

### Screen inventory
HOME · FOCUS · TIMER · STOPWATCH · TODAY · STATS · DEX · NFC · WEATHER · ALARM · PHONE · LIGHT · SETTINGS · BIRTHDAY · NIGHT

## V4 physical direction

- no front charging tray,
- no unnecessary forward projection,
- 4.3-inch HMI is the product's visual center,
- phone parks behind the display on a simple sloped support,
- protected Qi pad/puck mounts at that rear support,
- NFC / figure interaction lives on a small side pod,
- side pod defaults to the right but is mechanically mirrorable,
- subtle underside ambient light,
- 3D printing remains optional.

The screen is the product; charging and NFC are supporting interactions.

## Daily functions

### Offline core
- clock / RTC
- alarm
- Pomodoro / Focus
- countdown timer
- stopwatch + lap
- study-session log
- daily / weekly totals and streak
- D-day / small todo list
- NFC / Dex
- ambient / Night mode

### Wi-Fi enhancement
- NTP
- weather
- local phone web settings
- OTA

### Optional phone bridge
- rear-phone parked/charging status
- priority call / calendar / selected-contact summaries
- message body hidden and never persisted by default
- platform adapter keeps Android/iOS integration out of core V1

## Hardware

- **HMI:** Waveshare ESP32-S3-Touch-LCD-4.3C-BOX, SKU 33630
- **Dock:** ESP32-C3
- **NFC:** PN532 on Dock Node
- **Phone presence:** VL53L0X
- **Room light:** BH1750
- **Ambient light:** WS2812B/SK6812
- **Charging:** independent protected Qi/Qi2 charger
- **HMI ↔ Dock:** ESP-NOW

## Engineering structure

```text
site/                       GitHub Pages UI Lab
docs/                       product / UI / build specifications
firmware/hmi/core/          portable timing, study, policy models
firmware/hmi/ui/            screen IDs, view-models, design tokens
firmware/hmi/web/           phone browser settings UI
firmware/shared/            HMI ↔ Dock protocol
firmware/dock_node/         ESP32-C3 scaffold
config/                     product/user configuration
cad/                        optional compact enclosure source
```

Portable core logic is kept separate from LVGL/BSP adapters. Focus/timer/stopwatch logic is host-testable without the physical board.

## Read first

1. `docs/PRODUCT_V4.md`
2. `docs/PHYSICAL_LAYOUT_V4.md`
3. `docs/UI_SCREEN_SPEC.md`
4. `firmware/hmi/ui/SCREEN_BUILD_PLAN.md`
5. `docs/PHONE_LINK.md`
6. `docs/PURCHASE_NOW.md`
7. `docs/BUILD_DAY.md`
8. `docs/TEST_MATRIX.md`

## IP note

Personal, non-commercial fan project. Pokémon names/characters/artwork belong to their respective rights holders. Artwork is not committed as a redistributable asset pack; the browser prototype uses PokeAPI-hosted reference images for private design review.
