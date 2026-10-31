"""Independent check of the M6 harness against the OFFICIAL Waveshare schematic PDF netlist.

The vendor PDF (Altium export) carries a text layer with pin designators (PI<ref><pin>) grouped
per net and followed by net labels (NL<name>, '_' encoded as '0'). This script reads that layer
directly — it does not trust harness.json — and asserts every board-side pin M6 uses.
usage: python schematic_netlist_check.py <ESP32-S3-Touch-AMOLED-1.43-Schematic.pdf>
(download: https://files.waveshare.com/wiki/ESP32-S3-Touch-AMOLED-1.43/ESP32-S3-Touch-AMOLED-1.43-Schematic.pdf)
"""
import re
import sys

import fitz  # PyMuPDF

text = fitz.open(sys.argv[1])[0].get_text()
toks = re.findall(r"\b(PI[A-Za-z0-9]+|NL[A-Za-z0-9]+)\b", text)


def run_around(pin):
    """Net run containing the LAST occurrence of `pin` (the netlist section): pins + labels."""
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
    return set(toks[j:i + 1] + toks[i:k]), labels


EXPECT = [  # (pin token, required net label, other pins that must share the net, meaning)
    ("PIJ104", "USB_5V", {"PIJ40A40B9", "PIJ40A90B4", "PIU601"}, "J1-4 = USB_5V = Type-C VBUS = ETA6098 VIN"),
    ("PIJ106", "GND", set(), "J1-6 = GND"),
    ("PIJ101", "U_P", {"PIJ40A6", "PIJ40B6", "PIR1902"}, "J1-1 = U_P = Type-C DP1/DP2, before 22R R19"),
    ("PIJ103", "U_N", {"PIJ40A7", "PIJ40B7", "PIR1802"}, "J1-3 = U_N = Type-C DN1/DN2, before 22R R18"),
    ("PIJ108", "IO16", {"PIU4022"}, "J1-8 = GPIO16 (ESP32-S3R8 pin 22)"),
    ("PIJ102", "VBAT", {"PIJ701"}, "J1-2 = VBAT (must stay unconnected in M6)"),
    ("PIJ202", "GND", set(), "J2-2 = GND"),
    ("PIJ701", "VBAT", set(), "J7-1 = VBAT (battery header, empty in M6)"),
]
fail = []
for pin, label, mates, why in EXPECT:
    run, labels = run_around(pin)
    ok = label in labels and mates <= run
    print(("PASS " if ok else "FAIL ") + f"{why}: labels={labels} mates_ok={mates <= run}")
    if not ok:
        fail.append(why)
# J2-1 (RTC backup) is an unnamed net: require D1 cathode (pin 2) and PCF85063 VDD (pin 10) in its run
run, labels = run_around("PIJ201")
ok = {"PID102", "PIU2010"} <= run and "3V3" not in labels and "VBAT" not in labels
print(("PASS " if ok else "FAIL ") + "J2-1 = PCF85063 VDD = cathode of D1 (charged from 3V3 through B5819)")
if not ok:
    fail.append("J2-1")
print("PASS" if not fail else "FAIL", fail)
sys.exit(1 if fail else 0)
