# PokéDock V10 — historical purchase checklist / BOM (2026-10-18)

> **ARCHIVED; DO NOT ORDER FROM THIS FILE.** Current phone is **iPhone 14 Pro + MagSafe case**, and purchase gate is [V14 BOM](V14_PURCHASING_BOM.md) plus [release audit](V14_RELEASE_AUDIT.md).

## Buy in phases. No speculative large shopping cart.

### Phase A — buy/prepare first
| Qty | Exact item | Why | Notes |
| --- | --- | --- | --- |
| 1 | Waveshare **ESP32-S3-Touch-LCD-4.3C-BOX SKU 33630** (cased) | 800×480 touch ESP32-S3 HMI, RTC, Wi-Fi, audio interface, microSD | Confirm suffix C and SKU 33630; NOT 4.3 old or 4.3B. Official Waveshare family listing US$39.99–45.99 by case option, before shipping/taxes. |
| 1 | **Manufacturer-compatible certified regulated DC 12V 2A supply** (example 24W) and insulated terminal wiring | Official 4.3C DC terminal accepts **7–36V** | Check actual board/schematic terminal location and polarity before any connection. DO NOT supply 12V to USB-C, GPIO or 5V pins. |
| 1 | Data-capable USB-C cable | Flash / serial monitor / recover firmware | Check how the delivered board is powered during flashing; USB-C is documented for programming/debugging and is not the 7–36V DC terminal. |
| 1 | CR927 coin cell | Onboard PCF85063 RTC power-off time retention | Check polarity. |
| 1 | Branded microSD 16–32GB | Offline image/animation assets later | Factory SD example must pass before use. |
| 1 | **Protected finished MagSafe charger** (Apple 1m or reputable certified equivalent) | iPhone 14-family rear magnetic alignment | Current Apple Korea 1m listing was ₩65,000; not ordered. Requires exact phone/case fit check. |
| 1 | Compatible certified **USB-C PD >=20W adapter** for iPhone 14 up to 15W MagSafe | **Independent** phone charger power | Do not draw MagSafe power from Waveshare 5V board output. For newest MagSafe model see Apple's matching adapter specifications; newer phones support different rates. |
| set | Adjustable mini stand / 2–3mm acrylic or PC, small bottom stop, non-slip pad, cable clips and removable mounts | Temporary rear sloping phone stand | Print or cut permanent enclosure only after phone + camera bump + case + charger size measured. |
| set | Multimeter, correct insulated wiring/connector, screwdriver | Polarity and continuity checks | No DIY mains power supply or exposed AC contacts. |

Vendor source: https://www.waveshare.com/product/esp32-s3-touch-lcd-4.3c.htm
Board wiki: https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3C
Apple 14: https://support.apple.com/ko-kr/111850
Apple MagSafe: https://support.apple.com/ko-kr/105047
Apple charger listing: https://www.apple.com/kr/shop/product/mgd74kh/a

### Phase B — defer until A works on the bench
| Qty | Optional item | Qualification |
| --- | --- | --- |
| 1 | ESP32-C3 small dev board | Dock node; test HMI ESP-NOW interaction first. |
| 1 | PN532 NFC breakout and NTAG cards/labels | Confirm I2C interface, electrical levels and antenna interference; locate on right side. |
| 1 | BH1750 ambient sensor | Only if auto-brightness matters after manual night dim works. |
| 1 | VL53L0X ToF | Phone presence only, NOT Qi charging state or battery percentage. Consider omitting. |
| 1 | 4–8 WS2812B/SK6812 addressable LEDs | Subtle underside ambient; 3.3V->5V level shifting, 330 ohm signal resistor, 470–1000uF supply decoupling, compatible regulated supply and current budget. |
| as needed | 3.3V/5V regulator, small PCB/connectors, speaker with suitable ES8311 header | Confirm actual board extras and electrical requirements first. |

### Do not buy yet
Extra RTC, duplicate display, random bare Qi coils/driver, custom Li-ion battery system, oversized RGB, servo, microphone array or dedicated Bluetooth notification dongle.

### Mechanical and power isolation
- Board 4.3C-BOX DC input is a different power domain than standalone USB-C MagSafe puck. Use independent **certified** adapters at first. Don't tie positive rails together.
- Phone stand is a simple sloping rear support, no protruding front tray. Phone must be removable with one hand; anti-slip ledge and camera bump clearance are non-negotiable.
- Antenna, reset, USB, SD and ventilation stay accessible. Side NFC pod does not protrude beyond the front edge.
- Confirm exact **iPhone 14 vs 14 Pro/Plus/Pro Max** model and everyday case before making final mechanical parts.
- Measure iPhone/puck temperature and stable charging over 60 minutes; repeat docking 30 cycles.
- Do not claim phone is charging from a proximity sensor. Only a verified status API/power measurement can establish active charging.

### Purchase decisions and cost
Confirmed listings: Waveshare 4.3C family **US$39.99–45.99** depending on variant; Apple MagSafe 1m **₩65,000** (check again before payment). Other components, shipping, customs and local availability are NOT priced/verified; ask seller for a quote rather than inventing a total. The user has not authorized payment or placed an order.

### Stage gates
A0 exact board SKU and terminal verified. A1 exact phone/case confirmed. A2 LCD/touch/RTC/SD factory tests pass. A3 MagSafe independent 60-minute charge test. A4 temporary stand/fit test. Only then buy B or 3D-print final enclosure.
