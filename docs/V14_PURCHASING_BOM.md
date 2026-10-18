# PokéDock V14 — confirmed-case staged order list

**As of 2026-10-18: confirmed recipient iPhone 14 Pro + MagSafe-compatible case. NOTHING HAS BEEN PURCHASED by this assistant.** The list distinguishes must-buy, conditional, and defer. Use product model names, not random copycat PCB modules.

## Phase 1: essential screen and safe test components
| Qty | Decision | Specification and checks | Expected status |
| --- | --- | --- | --- |
| 1 | BUY | **Waveshare ESP32-S3-Touch-LCD-4.3C-BOX SKU 33630** (with casing, 800×480, 16MB Flash, 8MB PSRAM). Check that box model is 33630, not 33799 bare board or 4.3B. | Check seller stock, delivery, return policy |
| 1 | BUY/REUSE | Compatible **certified regulated 12V 2A DC supply (example)** for the vendor's 7–36V DC terminal; correct insulated screw connector/pigtail. VERIFY actual terminal polarity and wiring vs schematic before connecting. | Order only known matching connector |
| 1 | REUSE | USB-C data cable to PC for flashing & factory recovery. | Test data signal, not charge-only cable |
| 1 | BUY/REUSE | CR927 RTC backup coin cell. | Check polarity, holder |
| 1 | BUY/REUSE | Good microSD 16–32GB FAT-compatible for verified manufacturer example. | Don't assume included |
| 1 | REUSE/BUY | Multimeter, screwdrivers, caliper or ruler, protractor, antistatic workspace, cardboard/foam board, removable clips, simple stand. | Prototype tools |
| set | BUY LATER | 2–3mm PC/acrylic or 4–6mm PETG first mechanical test parts, silicone contact pads, 4 rubber feet, cable clips, serviceable fasteners. | Choose thickness/hole sizes after mockup |

The manufacturer advertises Wi-Fi/BLE, RTC, SD and ES8311 codec. Whether a usable speaker is included must be verified from actual packaging, not inferred from a drawing.

## Phase 1.5: charging module after confirming physical access/space
| Qty | Decision | Product | Cost evidence |
| --- | --- | --- | --- |
| 1 | **Recommended, after quick cardboard fit check** | **Apple MagSafe Charger (1m)**, current 2025 revision A3502 from official Apple Korea store. Completely finished protected charger, iPhone 14 Pro compatible. | **₩65,000 listed**, check live seller price at checkout: https://www.apple.com/kr/shop/product/mgd74kh/a |
| 1 | REUSE/BUY | Proper 20W-or-higher USB-C **PD adapter** with compatible output for iPhone 14 Pro maximum 15W. Current MagSafe 25W marketing does not mean the iPhone 14 Pro takes 25W. | Price TBD or reuse existing |
| 1 | AFTER MEASURING | Small, removable puck holder / open-backed carrier sized for the actual Apple charger (or other verified Qi2-certified complete puck). | Custom cut/print price TBD |
| 1 | REUSE/BUY | Soft cable strain relief, no adhesive on charger charging face. | Estimate only after geometry |

If user already owns a compatible MagSafe puck + PD adapter, **reuse them and measure** before buying a new Apple unit. Qi2 / third party can be evaluated, but advertised "MagSafe compatible" alone does not guarantee the expected charge output/certification or exact puck geometry.

## Phase 2: defer until HMI clock/Focus and charging both work
**Do not purchase yet:** ESP32-C3 Dock Node, PN532 NFC, NTAG figures, BH1750 sensor, VL53L0X phone presence, WS2812B LEDs, LED shifter/regulator, fancy 3D-printed full enclosure, special Pokémon speaker/music module, secondary RTC, extra display.

## Wiring and charging safety
- **Independent certified adapters**: LCD 7–36V DC vendor terminal vs MagSafe USB-C PD. Never connect 12V supply to board USB-C, pins, Qi puck or 5V headers.
- Power off when checking screw terminals; measure supply output and terminal +/−; do not route bare AC mains or DIY power supplies inside device.
- The phone's MagSafe case supports magnetic attachment but **does not itself verify wireless charging** with a given puck; test charging on the actual iPhone.
- Do not add fixed Lightning plug into cradle, which strains port and case; phone remains removable.
- Puck at phone coil back, no metal/insulating spacer blocking, charger remains vented/replacable. No battery percentage unless verified from an authorized link; magnetic presence ≠ true charging.
- Test MagSafe while LCD on for 60min; 30 dock cycles. Stop on unusual heat, erratic charging or stand tipping.

## Working shopping budget (price separation)
- Apple OEM MagSafe 1m: ₩65,000 **listed**.
- HMI vendor USD listing: pricing varies by enclosure, source and shipping; reconfirm exact 33630 checkout rather than guessing a KRW conversion.
- USB-C PD adapter, screen DC adapter, accessory materials, postage, taxes and print shop quotes: TBD or reuse.
- Do NOT claim one all-in total before local vendor quote.

## First shopping step today
1. Look for existing certified 20W USB-C PD adapter and MagSafe puck in household.
2. Verify typical case thickness/brand (can be done after delivery of stand material).
3. Buy correct Waveshare 4.3C-BOX + matching isolated DC supply and backup cell; keep charger purchase optional until angle mock passes.
4. Test free-standing MagSafe charger on iPhone+case first; then make adjustable open carrier.
