# PokéDock Mobile v1 — 2026-10-23 continuation / asset provenance

**Two projects are now explicitly separate:**
1. **V16 hardware gift**: rounded Pepper's Ghost clock (2.41in V2 AMOLED + front 2.42in SSD1309), custom optical reflector, alarm/focus, user-triggered OTA. Still NOT physically ready to purchase as one fully validated kit.
2. **PokéDock Mobile**: installable PWA, adapting the earlier liked V15 UI experience to a phone-first 2D game/cartoon aesthetic. NOT Android APK / iOS App Store app, not directly paired to a physical V16 board.

**ChatGPT conversation deliverable (2026-10-23)**: local working folder `PokeDock_Mobile_20261023/`, user-downloadable compressed ZIP `PokeDock_Mobile_PWA_2D_Styles_And_V16_BOM_20261023.zip` (~7.7MB), includes app/ + tests/ + quoted vs estimated shopping .xlsx + 15-style contact sheet + 3-style Gengar-like ghost animation GIF + detailed deployment/purchase notes. **The full ZIP and binary assets were NOT committed into this GitHub repository.** Do not claim a live deployed URL without verifying Pages configuration. A copy of this handoff doc is stored for state continuity only.

**Actual PWA source (contained in delivered ZIP):** vanilla JS/ES modules, HTML/CSS, PWA manifest/service-worker, offline cache, Android/iOS responsive, Home / Friends / Focus / Settings, 15/25/45min persistent epoch-based focus timer, foreground daily alarm and sound OFF by default, private local message, opt-in notification permission, reduced motion, 5-character selection, user-provided PNG/GIF/WebP imported into IndexedDB, three styles of authored placeholder animation, optional externally loaded PokeAPI battle GIF (network-required/reference only). **No licensed original Pokémon art bundled** and not authorized for redistributing franchise sprites. Private import is local-only.

**Executed tests:** node time-core PASS, node VM fake-DOM UI test PASS (selection/style/focus/alarm/save), Python Pillow animated WebP test PASS (5 characters × 3 styles × 48 frames = 720 frames and 15 animation files, 6.145MB), PWA cache list 22 files all present, JS parse PASS. **Real Chromium navigation/E2E is blocked by local administrator networking policy; no live Android/iOS install passed.**

**Updated purchase reference (2026-10-23):**
- Waveshare ESP32-S3-Touch-AMOLED-2.41 bare PCB `V2 / Rev2.0`, official list USD49.99-53.99 selectable, https://www.waveshare.com/esp32-s3-touch-amoled-2.41.htm
- Waveshare WHITE SSD1309 2.42inch OLED 128x64, factory default **SPI**, 61.50×39.50mm board, visible 55.01×27.49mm, USD12.99 official or KRW30,690 incl. VAT at https://eleparts.co.kr/goods/view?no=13415253
- ARTSIGN #4360 100×100×100×3mm 5-sided acrylic cover is **KRW12,900 free shipping listed** at https://www.gongumall.kr/home/product/detail2.php?prdcode=G0000080208 ; internal dimension assumption ~94mm (not 96mm). 82mm reflector + rails may not fit at corners.
- Optical 82×88mm beam splitter (45°/T70-R30 desired), custom 3D mounting, connector clearances, and native V2 board full firmware remain **unquoted/unverified**. $49.99+$12.99 translated at 1324.6 KRW/USD is about KRW83,423 excluding shipping/taxes. Together with box listed KRW12,900 ~KRW96,323, not final one-stop checkout.
- Planning scenario low/upper mixed known prices+estimates KRW176,323 to KRW414,323, not competitive verified landed quotations.

**DO NOT claim:** that real 3D volumetric holography is achieved; that host codec tests prove 24fps on ESP32; that PWA alarms run while phone locked; that device OTA is tested; that one-shot hardware kit is confirmed compatible.

**Next technical dependencies:** (a) V2 board exact pin header footprint and source firmware port, (b) single-piece optical 82x88mm confirmed coating with quote, (c) 100mm ARTSIGN transparent cover real internal tolerances or alternative, (d) final PCB screw boss/USB/rotary cable design and outsourced prototype quote, (e) hardware optics 150/300/500lux and actual full system tests, (f) HTTPS PWA site deployment and real Android/Safari tests, (g) non-infringing high-quality sprite/animation art for any public release.

**User direction:** wants polished 2D Nintendo/game-like character motion, not hyperrealistic 3D; smartphone app should be split from hardware gift.
