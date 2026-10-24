"""One buzzer, one voltage everywhere: BOM, harness/circuit, CAD and firmware must agree on
Soberton WT-1205 (5 V passive magnetic, 47 ohm, 2.4 kHz, d12.0 x 9.5 +/-0.5, 50 mA max mean).
usage: python buzzer_consistency_check.py
"""
import csv
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "cad"))
import m6_params as P  # noqa: E402

DS = {"part": "WT-1205", "v_min": 4.0, "v_max": 6.0, "d": 12.0, "h": 9.5, "tol": 0.5, "coil_ohm": 47, "f_hz": 2400}
fail = []
bom = list(csv.DictReader(open(ROOT / "procurement" / "BOM_M6.csv", encoding="utf8")))
rows = [r for r in bom if "buzzer" in r["item"].lower()]
if not rows or DS["part"] not in rows[0]["exact_part_or_spec"] or "5 V" not in rows[0]["exact_part_or_spec"]:
    fail.append("BOM buzzer row is not WT-1205 / 5 V")
h = json.loads((ROOT / "electronics" / "harness.json").read_text(encoding="utf8"))
bz = h["buzzer_driver"]["BZ"]
if DS["part"] not in bz or "5 V" not in bz:
    fail.append("harness buzzer is not WT-1205 on 5 V")
if not any(w["net"] == "USB_5V" and "buzzer +" in w["to"] for w in h["harness"]):
    fail.append("buzzer + is not fed from USB_5V")
if not (DS["v_min"] <= P.BUZZER_RAIL_V <= DS["v_max"]) or DS["part"] not in P.BUZZER_PART:
    fail.append("CAD buzzer part / rail mismatch")
if P.BUZ_D != DS["d"] or P.BUZ_H != DS["h"] or P.BUZ_TOL < DS["tol"]:
    fail.append("CAD buzzer envelope differs from datasheet")
if P.BUZ_FIT < DS["tol"] / 2 + 0.25 + 0.05:
    fail.append(f"pocket radial fit {P.BUZ_FIT} too small for d{DS['d']}+{DS['tol']} part in an undersized FDM hole")
# 2N3904 base drive: (3.3 - 0.75) / R1 must exceed Ic/beta_min (beta_min 30 at 100 mA) for the DC coil current
r1 = int(re.search(r"(\d+) ohm", h["buzzer_driver"]["R1"]).group(1))
ib = (3.3 - 0.75) / r1
ic_dc = P.BUZZER_RAIL_V / DS["coil_ohm"]
if ib < ic_dc / 30:
    fail.append(f"base current {ib * 1e3:.2f} mA cannot saturate {ic_dc * 1e3:.0f} mA")
fw = (ROOT / "firmware" / "main" / "board_io.c").read_text(encoding="utf8")
notes = [int(x) for x in re.findall(r"\{(\d{3,4}), \d+\}", fw)]
if not notes or min(notes) < 1500 or max(notes) > 3200:
    fail.append(f"firmware tones {min(notes)}-{max(notes)} Hz far from WT-1205 2.4 kHz")
if "512" not in fw or "LEDC_TIMER_10_BIT" not in fw:
    fail.append("firmware is not driving a 1/2-duty square wave")
board_h = (ROOT / "firmware" / "main" / "board.h").read_text(encoding="utf8")
if "USB_5V" not in board_h or "passive buzzer" not in board_h:
    fail.append("board.h buzzer comment does not state passive / USB_5V")
print(f"base drive {ib * 1e3:.2f} mA vs needed {ic_dc / 30 * 1e3:.2f} mA; tones {min(notes)}-{max(notes)} Hz")
print("PASS" if not fail else "FAIL", fail)
sys.exit(1 if fail else 0)
