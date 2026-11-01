"""Independent electrical check of the M7 wiring against the OFFICIAL Waveshare schematic text layer.

usage: python m7_electrical_check.py <ESP32-S3-Touch-AMOLED-1.43-Schematic.pdf> <harness_m7.json>
Reads the vendor PDF netlist layer (PI<ref><pin> runs followed by NL<net> labels) and asserts:
  power option B: the board's own USB-C J4 VBUS pins sit on USB_5V together with J1-4 (buzzer 5 V tap),
                  J4 D+/D- reach U_P/U_N, J4 has 5.1 k CC pull-downs (R4/R5 to GND), D2 feeds VCC from USB_5V
  J1 pins used by M7: 4 USB_5V, 6 GND, 8 IO16 (buzzer), 10 IO17 (lid sensor)
  GPIO rules: IO16 / IO17 are not used by the board (display, I2C, SD, ADC, strapping) and differ
Then checks harness_m7.json against those facts and computes the buzzer / sensor electrical numbers.
"""
import json
import re
import sys

import fitz  # PyMuPDF

pdf, harness = sys.argv[1:3]
text = fitz.open(pdf)[0].get_text()
toks = re.findall(r"\b(PI[A-Za-z0-9]+|NL[A-Za-z0-9]+)\b", text)
fails, n = [], 0


def check(name, cond, detail=""):
    global n
    n += 1
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  {detail}"))
    if not cond:
        fails.append(name)


def net_of(pin):
    i = len(toks) - 1 - toks[::-1].index(pin)
    j = i
    while j > 0 and not toks[j - 1].startswith("NL"):
        j -= 1
    k = i
    while k < len(toks) and not toks[k].startswith("NL"):
        k += 1
    labels = []
    while k < len(toks) and toks[k].startswith("NL"):
        labels.append(toks[k][2:].replace("0", "_"))
        k += 1
    return set(t for t in toks[j:k] if t.startswith("PI")), labels


vbus, lab = net_of("PIJ40A40B9")
check("J4 VBUS (A4/B9) is net USB_5V", "USB_5V" in lab, lab)
check("J4 VBUS (A9/B4) on the same net", "PIJ40A90B4" in vbus)
check("J1-4 is on USB_5V with J4 VBUS (buzzer 5 V tap = board USB input)", "PIJ104" in vbus)
check("D2 anode on USB_5V", "PID201" in vbus)
_, lab_d2k = net_of("PID202")
check("D2 cathode = VCC (board power path after the Schottky)", "VCC" in lab_d2k, lab_d2k)
dp, lab_dp = net_of("PIJ40A6")
check("J4 D+ (A6/B6) = U_P = J1-1", "U_P" in lab_dp and "PIJ101" in dp and "PIJ40B6" in dp, lab_dp)
dn, lab_dn = net_of("PIJ40A7")
check("J4 D- (A7/B7) = U_N = J1-3", "U_N" in lab_dn and "PIJ103" in dn and "PIJ40B7" in dn, lab_dn)
check("R4 / R5 one end on GND", "GND" in net_of("PIR402")[1] and "GND" in net_of("PIR502")[1])
check("R4 R5 5.1K printed next to J4 CC1/CC2 (sink Rd: any USB-C charger gives 5 V)",
      re.search(r"CC2.{0,60}J4\s+R4\s+5\.1K\s+R5\s+5\.1K", text.replace("\n", " ")) is not None)
for pin, want in (("PIJ104", "USB_5V"), ("PIJ106", "GND"), ("PIJ108", "IO16"), ("PIJ1010", "IO17")):
    pins, labels = net_of(pin)
    check(f"J1 pin {pin[4:]} = {want}", want in labels, labels)

h = json.load(open(harness, encoding="utf8"))
reserved = {9, 10, 11, 12, 13, 14, 21, 47, 48, 38, 39, 40, 41, 4, 15, 8, 0, 3, 45, 46}
used = h["gpio"]
check("buzzer GPIO 16 and lid GPIO 17 are different", used["buzzer"] != used["lid_sensor"])
check("neither GPIO is used by the board or a strapping pin", not ({used["buzzer"], used["lid_sensor"]} & reserved))
pins = {w["to_pin"]: w["net"] for w in h["harness"] if w.get("to_pin", "").startswith("J1-")}
check("harness: J1-4 USB_5V, J1-6 GND, J1-8 IO16, J1-10 IO17",
      pins.get("J1-4") == "USB_5V" and pins.get("J1-6") == "GND" and pins.get("J1-8") == "IO16" and pins.get("J1-10") == "IO17", pins)
check("harness: nothing on J1-1 / J1-3 (USB data stays on the board's own USB-C)", "J1-1" not in pins and "J1-3" not in pins)
check("harness: PTC in series with the buzzer 5 V tap", any("PTC" in w.get("via", "") for w in h["harness"] if w["net"] == "USB_5V"))

# numbers (datasheet values, see docs/04_ELECTRONICS_KO.md)
coil = (40.0, 54.0)                      # WT-1205 coil resistance range
i_peak = 5.25 / coil[0]
i_board = 0.30                            # ESP32-S3 + AMOLED, conservative (Wi-Fi off, BLE on)
i_total = i_board + i_peak
check(f"buzzer peak {i_peak * 1000:.0f} mA < AO3400A 5.8 A and 1N4148 300 mA (flyback)", i_peak < 0.3)
check(f"USB budget {i_total * 1000:.0f} mA < 500 mA (USB 2.0 port) and < MF-R075 hold 0.75 A", i_total < 0.5)
pullup_ua = 3.3 / 45e3 * 1e6               # ESP32-S3 internal pull-up ~45 kohm
check(f"lid input: internal pull-up ~{pullup_ua:.0f} uA through the reed (rated 10 W / 0.5 A class)", pullup_ua < 1000)
print(f"{'FAIL' if fails else 'PASS'}: {n - len(fails)}/{n} electrical checks")
sys.exit(1 if fails else 0)
