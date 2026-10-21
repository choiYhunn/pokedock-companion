# V16 Rev C Audit: critical defects and remaining hard blockers

## Important corrections from V16 Rev B
1. **Clock window fiction fixed**: Rev B used a square 1.5in SSD1327, 26.86mm active area, but B marketing mock showed ~100mm wide rectangular time. Rev C selects 2.42in SSD1309 55.01×27.49mm visible and cuts 56.5×29mm nominal hole. A cosmetic black surround can be wider, but the lit digits CANNOT span it.
2. **OLED electrical default fixed**: Rev B contemplated 1.5in default-SPI OLED and I²C resistor rework. Rev C chooses the 2.42in WHITE SSD1309 in default SPI mode with a 7-wire harness and exact GPIO assignment after V2 schematic/board. Simpler for no-microsolder DIY.
3. **CAD Rev B is not a final manufacturing specification.** V16 Rev C STL is a watertight single shell with accurate clock rectangular aperture *envelope*; microSD access, PCB mount bosses, encoder pocket, reflector slot and USB strain relief remain unbuilt.
4. **Optical transparency**: no AI-generated image certifies luminance or the 30° vs 45° acceptance. Real image height limited to physical screen active height (~37mm), view angle and contrast unproven.
5. **BOM claims**: USD catalog is not KRW landed cost; domestic OLED marketplace listings may have different controller and PCB size. Ignore claims of universal lowest price.
6. **Artwork quality**: downloaded Pokémon Showdown GIFs are pixel-art references, not coherent premium motions nor licensed to be repackaged. Private gift should not cause publishing franchise assets into a public repo or OTA releases.
7. **GHF1 decoder alpha issue**: current portable decoder uses RGB565 0 as transparency *sentinel*. An opaque pure black pixel may be lost if renderer interprets 0 as transparent. Do NOT ship high quality sprites until mask-aware decoder or GHF2 alpha format is tested on panel. RGB565 alone cannot preserve alpha.
8. **OTA**: docs and disabled prototype only. No real V2 board build/firmware A/B, no signed device manifest verification or on-device atomic asset pack swap. Release update button must remain disabled until fault-injection verification.
9. **Audible alarm**: 2.41 main board has no speaker; sound requires verified external module and specific GPIO. Default muted.
10. **Time trust after power removal**: clock hardware has RTC but backup supply and retention must be physically verified. No invented accurate alarm after prolonged power-off without NTP/re-sync.

## Genuine test observations (this turn)
- Rev C candidate OpenSCAD export in working container was watertight single shell, outer dimensions **132×105×54mm**, volume ~111.11 cm³ *shell geometry*, but lacks actual fasteners. Only geometric build, not factory mechanical pass.
- JavaScript engine state/clock/UI syntax confirmed at prior audit, but native 2.41 display integration STILL NOT BUILT.
- Native ESP32 programming and oscilloscope optical tests cannot run without actual connected hardware; remote CYH-NOTEBOOK offline as previously observed.
- GIF indices inventoried by path; GIF animation frame quality, licensed production assets and real streaming not validated.
- Expert factory feasibility and optics still BLOCKED; **NOT SAFE to pay for whole basket**.

## Non-negotiable validation checklist
- Real V2 board identity/datasheet, 5V/3.3V wiring, GPIO free and total current.
- Native display init, 12fps actual frames, clock OLED actual rendering, RTC/NTP trust, 60min soak, no OTA writes.
- Reflected face/eyes visible 60cm at 150/300/500lux, normal seated viewing angle, multiple movements.
- Production parts fit and USB-C accessible with strain relief.
- Never accept a vendor proof by AI render or a browser-only mock.
- Test physical power loss at: clock set, active timer, asset download, firmware OTA inactive slot, first boot rollback and device recovery.
