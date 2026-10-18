# V14 구매 의사결정·가격·호환성 정본 (2026-10-19)

**Never interpret a budget interval as a live binding price.** The maintained machine-readable order list is [procurement/v14_bom.csv](../procurement/v14_bom.csv). Only order after the **gate** column is satisfied. Prior [V10](V10_BOM_AND_PURCHASE.md) / [V14 short list](V14_PURCHASING_BOM.md) are historical/contextual, not a checkout cart.

## Source-based current market anchor
| Product | Qty | Observed reference | Status |
| --- | ---: | --- | --- |
| Waveshare ESP32-S3-Touch-LCD-4.3C-**BOX** SKU 33630 | 1 | Waveshare *family* US$39.99–45.99, needs with-plastic-case selection, local shipping/tax unknown; **landed budget ₩80k–110k is only an estimate** | Purchase first; avoid case-less SKU 33799 |
| KC 12V/2A DC adapter | 1 | Candidate ODYSSEY/SZH-PSU03 ₩8,800 at Eduino; `12V 2A` alone is not connector/polarity verification | Inspect C-BOX DC terminal and adapter before purchase |
| 3V **CR927** coin cell | 1 | Domestic ₩1,210 for 5 cells or ₩3,140 single listing; one needed; inspect included contents | Conditional |
| genuine 32GB microSD | 1 | ~₩10k–20k allocation, not confirmed checkout price | Reuse if possible; correct FAT/SDMMC test |
| Apple original MagSafe 1m A3502 / MGD74KH/A | 1 | **₩65,000 official Apple Korea**, fully finished puck compatible with iPhone 14 Pro | Optional, use existing first |
| Samsung USB-C PD 25W EP-T2510 | 1 | ₩25,300 Samsung official black cable-less, online price comparisons ~₩15k–21k | Optional, reuse any suitable 20W+ PD first |
| Small mechanical structure / high-friction feet / pads / bolts | one set | Maker fabrication allowance only (~₩25k–75k) | No supplier quote until measurement |

References checked 2026-10-19: [Waveshare 4.3C](https://www.waveshare.com/product/esp32-s3-touch-lcd-4.3c.htm); [SKU evidence](https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3C); [unrelated **case-less** Eleparts listing — DO NOT ORDER](https://eleparts.co.kr/goods/view?no=18220907); [Apple original MagSafe](https://www.apple.com/kr/shop/product/mgd74kh/a); [Samsung official EP-T2510](https://www.samsung.com/sec/mobile-accessories/25-w-pd-charger-power-saving-type/EP-T2510NBKGKR/); [Korean online price comparison](https://prod.danawa.com/info/?pcode=28885547). **No confirmed domestic ready-stock listing for exactly 33630 was found**; contact seller showing photographed part number before payment. A listed domestic '4.3B', '4.3' or '4.3C without case' is NOT interchangeable.

## Phase-dependent expected outlay (KRW)
Computed from the 17-row CSV planning inputs (12 basic items + 3 B add-ons + 2 deferred/excluded), assume all tools reusable and no returned/failed manufacturing. All figures are **scenario estimates** not vendor quotations:
- Basic A (screen+DC+RTC+SD+USB+mock+soft pads+feet+structure+fasteners+clips): **~₩129,000–243,500**.
- B charges: A + Apple original ₩65k + PD ~₩15k–25k + fitted holder ~₩4k–15k = **~₩213,030–348,800**.
- Reusing existing genuine puck & PD adapter can remove ~₩80k–90k of incremental spend. A small unplanned reprint is **not** included.
- Final local order price must include freight, taxes, whether connector/pigtail is included and actual print-shop quote; avoid rounded false precision.

## Purchase checkpoints
**P0 free:** measure cased iPhone+camera, photograph MagSafe case, inspect known power supplies, make cardboard angle trial; compare commercial compact phone supports with custom printed rail.

**P1 authorized essential:** exact Waveshare **33630** and appropriate power solution (certified supply after terminal verification), CR927 and microSD only if not included, use PC data cable from home. Keep packaging and snapshot the supplier item/options.

**P2 optional:** buy/borrow complete MagSafe and PD adapter only after rear 70° human-factors trial fits desk. An iPhone 14 Pro uses **up to 15W**, even if the puck box advertises 25W for newer phones. Confirm actual charge on phone and sustained temperature; no charge status shown in MCU without verified external telemetry.

**P3 after dimensions:** choose **one** of 3D PETG brackets or PC/acrylic cutting; do not buy both unless prototype dictates. OEM adapter hole thread, lip/pad spacing, fitted adjustable puck holder, rear foot, service ports, cables and replacement parts must be in fabrication drawing.

**P4 deferred:** ESP32-C3, PN532/NFC, BH1750, ToF, addressable LEDs, arbitrary battery, secondary RTC, external amplifier, separate wireless power PCB and full custom enclosure are not needed to make the gift.

## Material quality
Warm ivory and muted lavender/grey, matte edges; no stickers/gloss on phone contact surfaces. Rounded screw heads, anti-slip desk feet, no excessive logo/LED toys. Gift presentation is inspected only after all power/thermal/phone tests.

## Safety purchasing caveats
- Power domains remain isolated: **7–36V HMI DC terminal** vs **USB-C PD factory charger**. A 12V2A candidate **never goes to USB-C**. Do not run exposed bare AC inside gift.
- For audio, ES8311 codec and MX1.25 2-pin port are supported *in documentation*, but included speaker and impedance must be verified on the delivered board.
- No literal `magsafe-compatible case` claim guarantees sufficient magnet holding force or thermals; physical test is compulsory.
