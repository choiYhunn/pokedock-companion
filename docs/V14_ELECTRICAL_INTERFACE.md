# PokéDock V14 — Electrical interface map and isolation checklist (2026-10-19)

> [NEW: practical two-domain wiring diagram](../hardware/v14_wiring_topology.svg) · [harness connection table, safe terminal inspection and power-up SOP](V14_WIRING_HARNESS_BUILD.md). Do not infer physical +/− terminal number from a conceptual block diagram.

> Reference-level signal map from **Waveshare 4.3C** official wiki and first-party `examples/esp-idf/05_sd`. **Do not solder by this document alone.** Exact delivered C-BOX PCB/schematic and factory-driver versions win over a copied table. No wire connected or flash executed yet.

## Stage A: entirely separate low-voltage supplies

```text
Approved isolated regulated DC adapter, 12V/2A candidate
    ↓ power OFF during termination / DMM verify polarity & actual board terminal
Waveshare 4.3C-BOX SKU 33630 : dedicated 7-36V DC input
    ├─ onboard power, ESP32-S3, 800x480 LCD, touch, RTC, TF, audio
    └─ USB-C to PC = USB/debug/recovery, NOT a 12V input

Independent USB-C PD >=20W adapter (if charging is selected)
    ↓ factory-installed USB-C cable
Finished Apple MagSafe A3502 puck (or measured, fully certified equivalent)
    ↓ magnetically aligned with real iPhone 14 Pro + its case
iPhone 14 Pro: up to 15W MagSafe (NOT 25W on this phone)

Optional ESP32-C3 and NFC/LED later:
    another verified regulated low-voltage source to C3 power input
    ↔ HMI over ESP-NOW; no hardwired power/signal join with HMI by default
```

Do **not** use MCU battery-management interface, exposed mains AC, Qi bare coils or a user-built Li-ion bank in this MVP. Product's 7–36V rating does not license arbitrary non-isolated wiring. A certified DC adapter must have **matching connector, verified polarities, sufficient current, strain relief and mechanically protected terminal access**.

## 4.3C manufacturer interfaces (signal labels refer to *board*, not free pins)

| Domain | Board signal | Published/sampled GPIO | Implementation |
| --- | --- | --- | --- |
| Shared I2C | SDA / SCL | **8 / 9** | Already used by GT911 touch, PCF85063 RTC, ES8311 control & IO expander. Scan addresses only after factory baseline. Never reassign for a new device. |
| Touch | INT and reset | GPIO4 interrupt, **EXIO1** reset | BSP/vendor touch component owns lifecycle; verify orientation 800×480 |
| USB-C | D- / D+ | **19 / 20** | USB/JTAG/serial recovery. Must stay physically accessible |
| TF (1-bit SDMMC in first-party 05_sd example) | CLK / CMD / D0 | **12 / 11 / 13** | Factory `sd.c` uses `SDMMC_HOST_DEFAULT`, `slot.width=1`. Board wiki calls these SCK/MOSI/MISO in a generic physical table; **do not reinterpret as arbitrary SPI bus assignments** |
| Audio I2S | MCLK / LRCK / BCLK | **6 / 16 / 44** | Vendor codec driver only after verified physical speaker |
| Audio I2S | DSDIN / ASDOUT | **15 / 43** | Vendor code & actual data direction verification required |
| Audio enable | PA_CTRL | IO expansion control (**wiki: EXIO4**) | Wiki also lists EXIO4 for SD_CS in generic table. Avoid direct toggling; resolve named expander protocol and hardware revision from schematic + official examples |
| Display RGB | multiple GPIO + IO extension | See official wiki full table | No 'free GPIO' assumed: LCD uses many ESP pins; don't attach side modules here |
| HMI RTC coin backup | PCF85063 and CR927 | Onboard holder | Coin polarity/RTC retention test; no second RTC necessary |
| Power | DC terminal 7~36V | not GPIO | Regulated 12V2A candidate; verify supply/polarity connector before turn-on |
| MagSafe | USB-C PD input on factory puck | **zero HMI GPIO** | no battery %, Qi telemetry, charging-state field or phone power from magnetic presence |
| C3 wireless link | ESP-NOW / 2.4GHz | board-specific separate | only after base unit passes, match radio channel, nonblocking queues |

Official source: https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3C . SDMMC example: https://github.com/waveshareteam/ESP32-S3-Touch-LCD-4.3C/blob/main/examples/esp-idf/05_sd/components/sd/sd.c and `sd.h`.

## Speaker and audio acceptance (NOT OPTIONAL TO VERIFY IF FITTED)

1. Inspect delivered 33630: whether speaker is bundled, loudspeaker connector part number/polarity, amplifier connection and recommended speaker impedance/power in **schematic and vendor example**.
2. No direct speaker on ESP GPIO or random 5V amp until electrical diagram is verified.
3. Run first-party `11_speaker_microphone` demo after screen/RTC pass. Check low volume, mute, no unexpectedly loud wake alarm. For the gift a silent visual alarm is an acceptable M1 fallback if audio path unproven.
4. Future import only user-provided PCM WAV, validated headers/length/size/path and optional conversion pipeline. No public Pokémon cry/music bundle without appropriate authorization.

## Peripheral extension policy (nothing to order now)

- Optional ESP32-C3: choose specific board and its **strapping pins + regulator + logic level** before pin assignment. Never assume all C3 GPIO are safe to use.
- C3 PN532: I2C vs SPI chosen only after selected module schematic. Determine pullup rail voltages and addresses on **C3-side independent bus**. Keep antenna physically separated from MagSafe charger and prove scanning with charger on.
- C3 BH1750, VL53L0X: unnecessary for primary function; ToF proximity cannot prove charging.
- LED 5V WS2812B: separate supply budget, 3.3-to-5V data translator, data series resistance, power decoupling, brightness caps, no unmeasured HMI rail extraction.
- ESP-NOW event handler on callback task only enqueues data; LVGL task alone performs widget calls. HMI Wi-Fi STA channel cannot be assumed fixed.

## Bench sign-off record

| Test | Required evidence | Fail condition |
| --- | --- | --- |
| DC polarity (power OFF to connect) | photograph actual terminal + meter polarity reading | unreadable polarity/uninsulated leads |
| DC voltage stability | unloaded/loaded volt and sustained 60min screen run | unwanted reboot, overcurrent or abnormal heat |
| Touch + I2C | five corner input locations and detected peripherals | swapped axis, reset loop, I2C device conflict |
| RTC holdover | CR927 installation + five unplug/replug cycles | time loss without intended reset |
| TF 1-bit SDMMC | mount/read/unmount x10 (do not autoformat on missing SD) | corrupted card contents / locked UI |
| Speaker (if connected) | manufacturer sample, recorded volume/mute | unsuitable load / audible distortion / unexpectedly loud sound |
| MagSafe (optional) | separate adapter and 60min real charging | failed alignment, unexpected heat, unstable charging |
| Recovery | USB BOOT+RST and saved factory bin | can't restore factory image |

**Do not label any test PASS until actual measurements/logs have been recorded.**
