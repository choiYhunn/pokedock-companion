# Rev D optical engineering overlay — 2026-10-22

This directory supersedes Rev C as the current optical feasibility design, NOT as a verified manufacturable gift. Local host checks were executed in the current ChatGPT container; original vendor hardware was NOT present. Vendor prices are list prices, not landed shopping-cart totals.

Changes:
- Reflector 82 x 88 x nominal 1 mm, flat 45 degrees and shifted 7 mm toward front. Target canopy adjusted to 104 x 91 x 82 mm to provide front clearance for rail structure. Base unchanged 132 x 105 x 54 mm.
- 3D analytical ray tracing at distances 500/700 mm, seated eye heights 240/300/360 mm, yaw -10/0/+10 degrees (18 cases, 121 source pixels each) yields Rev C mean coverage ~56.5%, Rev D ~84.9%. This is geometric coverage ONLY: no luminance, coating, eye optics or image-quality certification. Worst sampled Rev D ~54.5%. A single front 600 mm/300 mm sample ~90.9%.
- The corrected canopy has simulated plate envelope clearance front 7.39 mm, back 21.39, top 10.89, bottom 8.89 and left/right 11 mm BEFORE material wall/rails tolerance. This does not prove fit.
- Rev D host CAD base STL is watertight and 132 x 105 x 54 mm, approximate shell volume 110.89cm3. Separate rails watertight. Not final PCB screw mounts, optical coating or cable strain relief.
- Portable C++ host runtime checks focus/pause/countdown/alarm repeat/5min snooze across month boundary, overlapping timer+alarm, manual-update gating, 5-character switching. SSD1309 128x64 clock framebuffer writes exactly 1024 bytes to a FAKE SPI sink. NO native RM690B0 firmware/hardware build.
- Synthetic 5-avatar/180-frame RGB565+alpha compression trial total ~0.54MiB, 2 decoded 256x256 frames use 384KiB. Premium real Pokémon assets, licensing, SD DMA and stable 12/24fps NOT demonstrated.
- Waveshare V2 exact demo: https://github.com/waveshareteam/ESP32-S3-Touch-AMOLED-2.41-V2/tree/main/02_Example/Arduino/09_LVGL_Test . QSPI 9/10/11/12/13/14, touch I2C 47/48, IRQ 3. Extra SSD1309 GPIO38-42/encoder GPIO1,7,8 are PROPOSED, not circuit verified. GPIO43 candidate buzzer conflicts with UART0 TX.
- Default OLED SSD1309 initial reference has NO forced 0x8D charge-pump change; panel power/reset sequence and SPI module actual handling still requires first-party electrical verification.
- Main first-stage supplier waveshare.com ESP32-S3-Touch-AMOLED-2.41 bare V2 Rev2.0; OLED white Waveshare SKU25742 2.42inch SPI. No clear canopy supplier has quoted exact 104x91x82mm yet; 30R70T optical plate still requires a one-piece quote.
- Bill-of-materials now conservatively estimates ~234,000-483,000 KRW including printed finish, one revision and unquoted optical/custom parts, NOT a checkout claim. Reuse components and simple finish to lower budget, never remove safety/optical gates.

Gate: NO one-shot purchase authorization before exact PCB V2/headers, coated reflector and custom canopy price, final mounting/USB harness, ability to see face at normal indoor lighting, and stable device firmware with signed update/USB rollback plan. The current one-shot bundle remains a tested host engineering handoff, not a gift-ready full-stack program.
