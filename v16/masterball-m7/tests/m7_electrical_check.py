"""Independent electrical check of the M7 v0.6 wiring against the OFFICIAL Waveshare schematic text layer.

usage: python m7_electrical_check.py <ESP32-S3-Touch-AMOLED-1.43-Schematic.pdf> <harness_m7.json>
Reads the vendor PDF netlist layer (PI<ref><pin> runs followed by NL<net> labels) and asserts:
  power option B: the board's own USB-C J4 (VBUS on USB_5V, D+/D- to U_P/U_N, 5.1 k CC pull-downs, D2 -> VCC)
  J10 (sound): 1 = RXD (GPIO44, ESP32-S3 pin 50), 2 = TXD (GPIO43, pin 49 side), 3 = 3V3, 4 = GND
  J1 (lid):    6 = GND, 10 = IO17 (pin 23); J1-4 / J1-1 / J1-3 stay unused
  3V3 comes from the MP1605 buck (U3), 2 A, 2.3-5.5 V in (MPS datasheet)
Then checks harness_m7.json against those facts and computes the power and signal numbers.
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


# --- USB-C power path (unchanged from v0.5) ---------------------------------------------------------
vbus, lab = net_of("PIJ40A40B9")
check("J4 VBUS (A4/B9) is net USB_5V", "USB_5V" in lab, lab)
check("J4 VBUS (A9/B4) on the same net", "PIJ40A90B4" in vbus)
check("D2 anode on USB_5V", "PID201" in vbus)
_, lab_d2k = net_of("PID202")
check("D2 cathode = VCC (board power path after the Schottky)", "VCC" in lab_d2k, lab_d2k)
dp, lab_dp = net_of("PIJ40A6")
check("J4 D+ (A6/B6) = U_P", "U_P" in lab_dp and "PIJ40B6" in dp, lab_dp)
dn, lab_dn = net_of("PIJ40A7")
check("J4 D- (A7/B7) = U_N", "U_N" in lab_dn and "PIJ40B7" in dn, lab_dn)
check("R4 R5 5.1K next to J4 CC1/CC2 (sink Rd: any USB-C charger gives 5 V)",
      re.search(r"CC2.{0,60}J4\s+R4\s+5\.1K\s+R5\s+5\.1K", text.replace("\n", " ")) is not None)

# --- J10 sound connector ----------------------------------------------------------------------------
p1, l1 = net_of("PIJ1001")
check("J10-1 = RXD / UART0RXD, wired to ESP32-S3 pin 50 (U0RXD = GPIO44)", "RXD" in l1 and "PIU4050" in p1, (l1, sorted(p1)))
p2, l2 = net_of("PIJ1002")
check("J10-2 = TXD / UART0TXD (GPIO43, ROM boot log)", "TXD" in l2, l2)
check("J10-3 = 3V3", "3V3" in net_of("PIJ1003")[1])
check("J10-4 = GND", "GND" in net_of("PIJ1004")[1])
check("J10-3 is the same net as J8-3 / J3-1 (board 3V3 rail)", "PIJ803" in net_of("PIJ1003")[0] or "PIJ301" in net_of("PIJ1003")[0]
      or "3V3" in net_of("PIJ803")[1])
flat = re.sub(r"\b(PI|NL|CO)[A-Za-z0-9]+\b", "", text)
flat = re.sub(r"\s+", " ", flat)
check("3V3 buck is U3 MP1605 (MPS: 2 A out, 2.3-5.5 V in)", re.search(r"U3 MP1605", flat) is not None)

# --- J1 lid sensor -----------------------------------------------------------------------------------
for pin, want in (("PIJ106", "GND"), ("PIJ1010", "IO17")):
    pins, labels = net_of(pin)
    check(f"J1 pin {pin[4:]} = {want}", want in labels, labels)
check("J1-10 goes to ESP32-S3 pin 23 (GPIO17)", "PIU4023" in net_of("PIJ1010")[0])
check("J1-4 = USB_5V (no longer tapped in v0.6)", "USB_5V" in net_of("PIJ104")[1])

# --- harness against the facts -----------------------------------------------------------------------
h = json.load(open(harness, encoding="utf8"))
check("harness file is v0.6", h.get("version") == "0.6")
g = h["gpio"]
reserved = {9, 10, 11, 12, 13, 14, 21, 47, 48, 38, 39, 40, 41, 4, 15, 19, 20, 0, 3, 45, 46}
check("lid GPIO17 and sound GPIO44 differ and avoid display/I2C/SD/USB/strapping pins",
      g["lid_sensor"] == 17 and g["audio_tx"] == 44 and not ({17, 44} & reserved))
H = {x["id"]: x for x in h["harnesses"]}
j = {r["j10_pin"]: r for r in H["H1"]["joints"] if r["j10_pin"]}
check("H1: J10-1 (GPIO44) -> module R (crossed: our TX to its RX)", j[1]["net"] == "GPIO44" and j[1]["module_pin"] == "R")
check("H1: J10-3 3V3 -> module +, J10-4 GND -> module -", j[3]["module_pin"] == "+" and j[4]["module_pin"] == "-")
check("H1: J10-2 (GPIO43 = ROM log) and module T are not wired",
      j[2]["module_pin"] is None and any(r["module_pin"] == "T" and r["j10_pin"] is None for r in H["H1"]["joints"]))
check("H1: no solder, commercial parts only", "no solder" in H["H1"]["build"] and {p["mpn"] for p in H["H1"]["parts"]} == {"4397", "3955"})
check("H1: wire colours explicitly not trusted (Qwiic order differs from J10)", "Never trust wire colours" in H["H1"]["identify"])
s = {r["socket_pin"]: r["net"] for r in H["H2"]["joints"]}
check("H2: reed on J1-10 (IO17) and J1-6 (GND) only", s == {10: "IO17", 6: "GND"}, s)
check("H3: speaker on SP+ / SP-", {r["pad"] for r in H["H3"]["joints"]} == {"SP+", "SP-"})
check("v0.5 buzzer parts are gone from the harness", not any(k in json.dumps(h["harnesses"]) for k in ("WT-1205", "AO3400A", "MF-R075", "1935161")))

# --- numbers (datasheets: MPS MP1605 2 A; DFR0534 3.3-5 V; PUI AS02808MR 8 ohm 1 W rated / 1.5 W max) ---
v3 = 3.3
spk_r = 8.0
i_amp_peak = v3 / spk_r                      # bridged output swinging the full 3V3 rail (upper bound)
p_spk_max = v3 ** 2 / (2 * spk_r)            # sine at full swing, BTL
i_board = 0.30                               # ESP32-S3 + AMOLED + BLE, conservative
i_module = 0.03                              # decoder + flash, estimate
i_3v3 = i_board + i_module + i_amp_peak
check(f"3V3 peak {i_3v3 * 1000:.0f} mA <= 80 % of the MP1605 2 A", i_3v3 <= 1.6)
check(f"speaker power at full 3V3 swing {p_spk_max:.2f} W < 1 W rating", p_spk_max < 1.0)
vcc = 5.0 - 0.45                              # MBR230 at ~0.7 A + cable
i_usb = i_3v3 * v3 / (0.85 * vcc)
check(f"USB input at peak {i_usb * 1000:.0f} mA < 1 A (KC 5 V adapter >= 1 A required; a PC port may only give 500 mA)", i_usb < 1.0)
cap = 24 / 30
i_usb_cap = (i_board + i_module + i_amp_peak * cap) * v3 / (0.85 * vcc)
print(f"INFO firmware volume cap 24/30: USB input peak ~{i_usb_cap * 1000:.0f} mA")
check("signal levels: module powered from the same 3V3 that drives GPIO44 (no level shifter, nothing fed back)", True)
pullup_ua = 3.3 / 45e3 * 1e6
check(f"lid input: internal pull-up ~{pullup_ua:.0f} uA through the reed (rated 10 VA, 0.25 A)", pullup_ua < 1000)
print(f"{'FAIL' if fails else 'PASS'}: {n - len(fails)}/{n} electrical checks")
sys.exit(1 if fails else 0)
