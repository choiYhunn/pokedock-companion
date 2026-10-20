# V16 Purchase Gate & Supplier Comparison — 2026-10-21
**STATUS: NO FINAL PURCHASE AUTHORIZATION.** User wants to buy only after the full work is researched. This sheet differentiates vendor LIST prices, domestic listing prices, planning allowances and checkout-verified prices. NONE are checkout-verified.
## Hard blockers before spending all at once
1. Optics: no physical beam splitter/luminance/viewing-angle data; 800 cd/m2 panel rating DOES NOT imply apparent reflected luminance.
2. Manufacturer must confirm **PCB V2 / Rev2.0** for selected board; V1 and V2 firmware and some pins differ.
3. Actual final glass/acrylic canopy and reflector process, sample finish and quote unverified. An industrial 50x75mm 30R/70T visible beam splitter costs 481,400 KRW **before VAT** at Edmund Optics; not a rational fit for this gift.
4. SSD1327 Waveshare 1.5in module defaults to 4-wire SPI; using I2C requires vendor-specified BS resistor/solder configuration. **Request ready-I2C configuration from seller** or budget a technician. The included PH2.0-7pin cable does not mate directly to the 2.41's SH1.0-4pin cable. DO NOT assume plug-and-play.
5. Input encoder and speaker require spare, PCB-version-specific GPIO; no speaker on main board. Finish may be silent-only if alarm hardware not verified.
6. Proper desk-height view angle may be closer to 30deg than 45deg; source-to-reflector ray geometry must pass before final cut.

## Verified listings (prices as displayed 2026-10-21, options/freight/FX can differ)
| Part | Source / link | Observed price | Selection | Confidence |
|---|---|---|---|---|
| ESP32-S3-Touch-AMOLED-2.41 **without case** | https://www.waveshare.com/esp32-s3-touch-amoled-2.41.htm | USD 49.99-53.99 across case options | candidate bare board; confirm EXACT option and **V2** with seller | manufacturer list, no cart/landed quote |
| Waveshare SSD1327 1.5in OLED Module SKU 13992 | https://www.waveshare.com/product/displays/oled/1.5inch-oled-module.htm | USD 12.99 (one unit) | front readable 26.86mm square active / 44.5x37mm board; SPI default | manufacturer list |
| Same SSD1327 OLED domestic | https://www.navimro.com/ (search exact Waveshare 1.5inch OLED Module) | KRW 35,189 via product search | alternative when local shipping is cheaper than consolidated import | search index not checkout |
| KY-040 rotary encoder | https://www.coupang.com (search exact KY-040 rotary encoder) | KRW 4,550 observed listing | prototype only; final shaft/knob mechanical quality may require premium encoder | third-party search price |
| 5V 2A certified supply + USB cable | https://www.coupang.com/vp/products/7645587133 | KRW 18,810 listing | candidate; total draw, KC and connector must be verified | public listing, not checkout |
| 3DFARM service | https://3dfarm.co.kr/3d-printing-price/ | basic service KRW 5,000 + printing + delivery | initial inspection print **after** CAD measured; PETG material factor published | no STL-specific quote |
| 50x75mm visible plate beam splitter | https://www.edmundoptics.co.kr/p/50-x-75mm-30-70rt-vis-plate-beamsplitter/37192/ | KRW 481,400 excl VAT | **REJECT** (higher than project ceiling) | vendor catalog |
| Cheap trial reflector | transparent PET sheet/clear acrylic sample cut from existing material | unquoted, cannot claim best price | FIRST test on phone before panel; edge reflections expected | sample grade unknown |
| Final clean clear canopy | transparent PMMA / premade rounded clear box + a flat inner optical plate | quote only | custom optical shape to be approved after G1 | no confirmed supplier |
| TF/microSD | branded >=8GB card, SD-compatible with exact board | planning only | assets stored offline; microSD slot existing on main board | benchmark only |
| USB/power cabling | USB-C 1m power lead; SH1.0 4pin included ~100mm; custom 3.3V OLED harness target 100-150mm | lengths are routing PLANNING only | verify actual PCB, PH2.0 I2C mode and connectors | not cut-to-length approved |

**Minimize shipping:** compare Waveshare board + OLED consolidated into a single manufacturer's order against Waveshare board separately + Korean OLED, using FINAL checkout landed totals. No domestic 2.41 SKU 30563 exact Rev2.0 in-stock checkout was verified from sources. Do not assert any marketplace is categorically cheapest.

## Whole-device budget (KRW planning only)
Board landed 70k-105k; OLED 20k-40k; trial/final reflector 8k-45k; printed base+professional finish 40k-100k; clear chamber 20k-65k; encoder/button 4k-12k; power/cable 10k-22k; wiring/feet/fasteners 7k-20k; microSD 0k (reuse) to 15k; prototype contingency 20k-50k. **Approx 199k-474k** worst-case envelope including all uncertainty; no confirmed checkout. To target ~20만원, reduce chamber/print finishing by finding a finished transparent stock case, reuse 5V charger/SD, and omit sound; do NOT cut electrical safety or optical gate.

## Two-checkpoint buy strategy, not a full basket
G0 free: smartphone + rigid transparent scrap plate + black background/representative image, desk tests at 150/300/500 lux and +/-20deg; record photo/video without exposure boosting. 
G1: ONLY after optical feasibility, vendor-confirm 2.41 board Rev2.0; initial board-only landed checkout and compatibility acceptance. Avoid ordering custom case/reflector/OLED at this point if uncertain.
G2: after received board sample and front clock fit, finalize measured geometry and quotes; buy exact OLED+encoder+loom+print+cover simultaneously.
G3: after full physical fit, temperature, code and update test, gift release.
