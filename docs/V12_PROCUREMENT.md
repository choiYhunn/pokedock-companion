> **V13 purchase change:** do NOT treat MagSafe and a second PD adapter as Phase A essentials. First make **passive landscape 70° slot** for confirmed iPhone 14 Pro, then optionally add a protected removable MagSafe module after a fit/heat/space test. See [V13 decision](V13_COMPACT_IPHONE_14_PRO.md). Earlier table below is preserved as V12 history.

# PokéDock V12 — phased sourcing with price confidence (2026-10-18)

Only **Phase A** is recommended now and even that remains pending user purchase authorization. Do not interpret a BOM as an order. Confirm iPhone variant/case and existing household USB-C adapter inventory first.

## A0 minimum shopping decision: what to buy, what to reuse

| Qty | Component | Selection standard | Evidence / approximate price basis |
| --- | --- | --- | --- |
| 1 | **Waveshare ESP32-S3-Touch-LCD-4.3C-BOX (SKU 33630)** | cased 800×480; flash/PSRAM, RTC, SD, codec; not 4.3B | vendor listing; family pages show ~US$39.99–45.99 depending on casing/option (verify exact checkout, shipping and VAT) |
| 1 | Compatible **certified regulated DC power supply** | vendor **4.3C** 7–36V DC input; suggested regulated 12V/2A where confirmed safe; correct terminal +/− | confirm with vendor/manual and delivered case, no DIY mains supply |
| 1 | USB-C **data** cable | flash/debug, USB port enumeration | reusable if already owned |
| 1 | CR927 cell | RTC backup | verify case holder/polarity |
| 1 | Reputable microSD 16–32GB | offline sprites/test files | FAT according to manufacturer example |
| 1 | Finished Apple MagSafe 1m puck or quality protected Qi2 equivalent | iPhone 14-family alignment, detachable and vented | Apple KR 1m: **₩65,000** listed, check actual date/seller |
| 1 | **20W+ USB-C PD adapter** with required output compatible with chosen puck | dedicated phone charging, never from Waveshare header | Apple 20W: **₩28,000** listed, may be reused if already present |
| 1 | Adjustable/reusable tabletop phone stand, cardboard/foam sheet, rubber pad, double-sided *temporary* mounting tape, cable clips | A/B physical form validation | do not buy 3D-print permanent shell before prototype |
| 1 | Multimeter + insulated correctly rated terminal connector/pigtail + screwdriver | verify board power/polarity and ensure safe service | reuse equipment if already available |

**Known partial Apple cost if buying both new:** ₩93,000 (puck ₩65,000 + adapter ₩28,000); Waveshare board is USD listing and local DC supply/stand/printing/SD shipping are unpriced. **Do not sum KRW and USD into a fake converted total.**

## A1 after receiving hardware
- If the actual OEM 75mm rear mount is usable, evaluate a small compatible 75mm desk bracket as an inexpensive *temporary test fixture* before printing a custom adapter. Screw pitch may be 75mm but thread and insertion depth must be measured.
- Decide A landscape (space priority) vs B portrait (concealment priority) from [design calculator](../design.html).
- Acquire PETG/PC sheet, fasteners and a puck carrier **only** from these dimensions. Avoid anonymous heat-generating integrated Qi transmitter boards.
- Build front/base/puck in **serviceable separable components**. If the manufacturer case blocks use of OEM mount, redesign the bracket based on actual STEP rather than trimming the case.

## B optional features after actual native HMI works
- ESP32-C3, properly leveled PN532/NTAG, maybe ambient sensor, optional 4–8 LEDs. Do not buy ToF merely to display a fake charging status.
- No custom battery or high-voltage PCB. ANCS and fancy audio are software-first investigations, not BOM stage blockers.
- Speaker: only source exact load/connector-compatible part after checking what the ordered C-BOX package includes.

## Phase-A purchase gate
- [ ] Confirm iPhone exact model and everyday case/MagSafe support.
- [ ] Confirm Waveshare exact **33630** variant and power terminal connector.
- [ ] Confirm seller prices/shipping for actual purchase.
- [ ] Confirm suitable PD adapter and multimeter already owned or buy.
- [ ] Define working desk depth, available power sockets and cable routes.
- [ ] Agree that custom 3D printing and NFC/LED remain deferred.

## Sources
- Waveshare official: https://www.waveshare.com/product/esp32-s3-touch-lcd-4.3c.htm
- Product docs: https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3C
- Apple MagSafe 1m https://www.apple.com/kr/shop/product/mgd74kh/a
- Apple accessories KR https://www.apple.com/kr/shop/accessories/all/made-by-apple/iphone-14
- iPhone 14 specifications https://support.apple.com/ko-kr/111850
