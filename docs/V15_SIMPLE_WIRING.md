# V15 wire and safety: phone charging eliminated

This is **one externally powered C-BOX HMI only**. 4.3C factory board contains LCD, capacitive touch, RTC, TF and codec. **No MagSafe/PD charger, extra C3, phone, LED or battery is required.**

```text
Korean 220V AC outlet -> certified isolated regulated AC/DC adapter
                            (candidate output DC 12V 2A)
                  -> insulated measured + and - DC wire termination
                  -> Waveshare 4.3C-BOX 33630 7–36V DC input (not all 16 pins!)

Windows PC -- USB-C data cable --> OEM USB-C debugging/flashing only
```

- **Never input 12V into USB-C, GPIO, 5V OUT, I2C, audio or DI/DO.** Do not connect bare 220V within the stand. Do not guess physical terminal pin numbers from the similarly-looking 4.3B pinout.
- Photograph actual delivered plastic casing, PCB revision, 16-way terminal and OEM marked VIN/GND. Check the manufacturer's 4.3C schematics and pin legend. Verify adapter output/polarity with a DMM and turn AC supply OFF before fastening insulated conductors. If novice, order a pre-terminated OEM-compatible power lead or ask a competent technician to terminate it.
- USB-C production **5V power** on this exact 4.3C version is not independently verified; its documented USB download/debug function does not prove 24/7 supply. **Do not substitute 4.3B's USB 5V documentation**.
- Do not insert USB-C and DC supplies together without manufacturer verification of allowed source/power-path behavior.
- U-shaped rear cutout on stand offers access for central bottom/rear terminal and cable, but actual connector height & bend are not CAD-verified. Route cable without bearing the 163g module weight.

Manufacturer official docs: https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3C
