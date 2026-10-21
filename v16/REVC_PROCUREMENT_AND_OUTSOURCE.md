# V16 Rev C — Shopping Decision & Outside Fabrication

**Decision status:** vendor candidates chosen, **not** current carts, not supplier-confirmed stock, not combined final checkout. Price checks 2026-10-21 ~ 2026-10-22; currency, shipping, VAT, delivery times and import duty may differ. No purchase made.

## Exact items and how to buy cheaply
| Item | Candidate / supplier | Evidence | Tentative landed KRW allowance | Gate |
|---|---|---|---:|---|
| Primary OLED animator/ESP32 | Waveshare ESP32-S3-Touch-AMOLED-2.41 **bare board, V2 Rev2.0**, https://www.waveshare.com/esp32-s3-touch-amoled-2.41.htm | manufacturer **USD49.99–53.99** across variants, no confirmed cart | 70,000–105,000 | Request PCB V2/Rev2.0, confirm shipped option, delivery+tax |
| Readable front clock | Waveshare **2.42inch OLED Module WHITE SSD1309, SKU 25742**, https://www.waveshare.com/product/ai/2.42inch-oled-module.htm | manufacturer **USD12.99** | 20,000–37,000 | Default 4-wire SPI, 61.5x39.5mm PCB / 55.01x27.49 visible |
| Domestic OLED alternative | Coupang 128x64 I2C **2.42inch**, https://www.coupang.com/vp/products/9531787503 | public listing ₩19,500 + ₩3,000 shipping (historical crawl, no verified checkout) | 22,500–30,000 | Confirm controller, PCB size, actual 4-pin I2C before substituting |
| Optical plate | 64x70mm ~0.5–1mm flat thin PET/PMMA trial plus optional 30R/70T film | not yet priced from specific compatible seller | 8,000–25,000 | Ask laser cut + reflection ratio, reflection double-image and flatness |
| Clear enclosure | Off-the-shelf transparent polished plastic cover that fits internal 104x85x82mm target; otherwise custom PMMA clean bend | NO exact matching catalog sample/quote located | 15,000–50,000 | Highest-risk price + final sizing gate; ask 2 quotes |
| Rounded ivory base | 3DFARM https://3dfarm.co.kr/3d-printing-price/ PETG one-piece ~111 cm³ nominal Rev C *shell volume* (slicer result may vary) | supplier examples: 100cm³ PLA ~₩34,000 incl base+shipping; not your exact model | 30,000–60,000 | Rev C prototype first, inspect layer lines; premium finish quote later |
| Input | EC11 press incremental encoder + smooth cap | exact seller/version/shaft length not selected | 4,000–10,000 | D-shaft/round shaft, threaded panel mount, flat mount location |
| Optional sound | 3.3V-compatible small piezo driver / active module | no verified product | 0–7,000 | silent-only unless verified |
| Wiring + rubber feet + misc | USB-C rear cable, SH1.0 original included, 7-wire OLED harness, screws, 3M feet | no verified basket | 8,000–20,000 | no bare AC, measure current |
| Optional external certified adapter | existing certified 5V USB supply reused else one KC-certified model | 5V/2A or per measured board load; not bought | 0–18,000 | supply capacity confirm |
| Branded microSD | reuse owned compatible >=8GB, else authentic 8–16GB | existing ownership unknown | 0–15,000 | offline pack drive |
| One revision contingency | printed spacer / one optical retry | internal project allowance | 15,000–30,000 | after first verification |

**Total envelope on this indicative itemized plan:** ₩170,000–₩377,000 if every upper range including optional accessories; check arithmetic before publish. Target near ₩220–250k only with combined direct factory shipment, off-the-shelf transparent cover, one FDM prototype, reused power/card and minimal audio hardware. Professional post-paint or custom clear PMMA can push it above ₩300k; do not hide that.

## Sourcing route chosen, not a false 'cheapest shop'
1. **Waveshare one basket preferred** for exact 2.41 V2 board + exact 2.42 WHITE OLED; request total including shipping and VAT. Manufacturer list vs landed Korean estimate distinct.
2. **Compare domestic I2C clock OLED** only if same active dimensions and PCB fit; saving ₩5,000 is not worth incompatible controller or rework. WaveShare's default SPI avoids resistor solder change but needs spare pins and 7-wire harness.
3. **3DFARM for base quote** after real PCB measurement; SLA/paint vendors only if matte FDM unacceptable. Published basic ₩5,000 plus material/time/processing/delivery formula. No STL-specific quote has been obtained.
4. **Cover vendor MUST be chosen after dimensions**: use stock ready polished transparent case whenever possible; no specific 104x85x82mm stock canopy has been identified and do not invent it. If customized, ask minimum one piece, polish quality, 1–2mm thickness, optical distortion, lead time and replacement.
5. **Laser cut plate**: https://makerz.kr/shop/make/ accepts DXF/SVG acrylic sheets from one piece, but optical reflection coating not implied by acrylic cutting. Ask both cut shape and optical behavior; do not pay Edmond 50×75mm 30R/70T visible coated optical plate ~₩481,400 excluding VAT, which exceeds project budget.
6. Request cross-vendor shipping and package dimensions; buy all secondary items in one bundle only once real layout is proven. No cheapest-in-market claim.

## External vendor brief (send after real module measurements)
One premium desk gadget base ~132W×105D×54H rounded 19mm corners, 3.2mm minimum wall, satin matte ivory finish, ~56.5×29mm front transparent clock window and 7.2mm tentative front/right rotary shaft location, rear USB-C cable service. Cover target 104W×85D×82H with soft outer corners, polished transparent surface. All dimensions **PRELIMINARY**. Need one replacement reflector bracket for 35°/45°, no visible glue, no rough support scars on front. Supply quote by FDM PETG / smoothing / SLA separately. **Do not manufacture from conceptual Rev C without actual hardware dry-fit.**

## Budget control rule
Stage 0 ₩0–10k trial → Stage 1 board-only <=₩105k landed after approval → Stage 2 small parts + prototype base after hardware and optical GO. If credible gift-ready total exceeds ~₩280k, redesign cover or change to rounded direct AMOLED; do not quietly increase spend.
