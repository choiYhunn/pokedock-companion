"""One buzzer, one driver, one voltage everywhere (BOM, harness, CAD, firmware), and a driver that is
switched fully on by datasheet guarantees - not by a small-signal hFE estimate.

Datasheet values used (sources in docs/REV_C_FINAL_KO.md):
  Soberton WT-1205 : 5 Vo-p rated (4-6), coil 47 +/-7 ohm, 50 mA max mean, 2400 Hz, d12.0 x 9.5 +/-0.5
  AO3400A (AOS)    : VGS(th) max 1.45 V; RDS(on) < 48 mohm at VGS 2.5 V; VDS 30 V; VGS +/-12 V; RthJA 125 C/W
  ESP32-S3 GPIO    : VOH >= 0.8 x VDD (2.64 V at 3.3 V)
  1N4148           : IF 200 mA continuous
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

BZ = {"part": "WT-1205", "v_min": 4.0, "v_max": 6.0, "d": 12.0, "h": 9.5, "tol": 0.5, "coil_min": 40.0}
FET = {"part": "AO3400A", "vgs_th_max": 1.45, "rds_vgs": 2.5, "rds_max": 0.048, "vds": 30.0, "vgs_abs": 12.0, "rth": 125.0}
VOH_MIN = 0.8 * 3.3
VBUS_MAX = 5.25
fail = []

bom = list(csv.DictReader(open(ROOT / "procurement" / "BOM_M6.csv", encoding="utf8")))
text = " ".join(r["item"] + " " + r["exact_part_or_spec"] for r in bom)
if BZ["part"] not in text or FET["part"] not in text:
    fail.append("BOM lacks WT-1205 or AO3400A")
if "2N3904" in text:
    fail.append("BOM still lists 2N3904")
h = json.loads((ROOT / "electronics" / "harness.json").read_text(encoding="utf8"))
drv = h["buzzer_driver"]
if BZ["part"] not in drv["BZ"] or FET["part"] not in drv["Q1"] or "1N4148" not in drv["D1"]:
    fail.append("harness driver parts differ from WT-1205 / AO3400A / 1N4148")
if not any(w["net"] == "USB_5V" and "buzzer +" in w["to"] for w in h["harness"]):
    fail.append("buzzer + is not fed from USB_5V")
svg = (ROOT / "electronics" / "wiring_m6.svg").read_text(encoding="utf8")
if FET["part"] not in svg or "2N3904" in svg:
    fail.append("wiring diagram not updated to AO3400A")
if not (BZ["v_min"] <= P.BUZZER_RAIL_V <= BZ["v_max"]) or BZ["part"] not in P.BUZZER_PART:
    fail.append("CAD buzzer part / rail mismatch")
if P.BUZ_D != BZ["d"] or P.BUZ_H != BZ["h"] or P.BUZ_TOL < BZ["tol"]:
    fail.append("CAD buzzer envelope differs from datasheet")

# electrical guarantees
i_peak = VBUS_MAX / BZ["coil_min"]                         # coil current if the PWM half period saturates
if VOH_MIN < FET["rds_vgs"]:
    fail.append("GPIO high level below the VGS at which RDS(on) is guaranteed")
if FET["vgs_th_max"] >= VOH_MIN - 0.5:
    fail.append("threshold too close to the GPIO high level")
v_ds_on = i_peak * FET["rds_max"]
p_fet = (i_peak ** 2) * FET["rds_max"] * 0.5               # 1/2 duty, worst case DC-limited current
t_rise = p_fet * FET["rth"]
if v_ds_on > 0.1 or t_rise > 5:
    fail.append(f"MOSFET on-state {v_ds_on:.3f} V / +{t_rise:.2f} C too high")
if VBUS_MAX + 1.0 > FET["vds"] or 3.3 > FET["vgs_abs"]:
    fail.append("MOSFET voltage ratings insufficient")
if i_peak > 0.200:
    fail.append("flyback diode 1N4148 continuous rating exceeded")
r1 = int(re.search(r"(\d+) ohm", drv["R1"]).group(1))
r2 = int(re.search(r"(\d+) kohm", drv["R2"]).group(1)) * 1000
if not (47 <= r1 <= 470) or r2 < 10000:
    fail.append("gate resistor / pull-down out of range")

fw = (ROOT / "firmware" / "main" / "board_io.c").read_text(encoding="utf8")
notes = [int(x) for x in re.findall(r"\{(\d{3,4}), \d+\}", fw)]
if not notes or min(notes) < 1500 or max(notes) > 3200:
    fail.append("firmware tones far from the WT-1205 2.4 kHz rating")
if "512" not in fw or "LEDC_TIMER_10_BIT" not in fw or "AO3400A" not in fw:
    fail.append("firmware is not a 1/2-duty square wave on the AO3400A driver")
board_h = (ROOT / "firmware" / "main" / "board.h").read_text(encoding="utf8")
if "AO3400A" not in board_h or "USB_5V" not in board_h:
    fail.append("board.h buzzer comment not updated")
print(f"peak coil {i_peak * 1e3:.0f} mA, VDS(on) <= {v_ds_on * 1e3:.1f} mV, FET loss {p_fet * 1e3:.2f} mW (+{t_rise:.2f} C), "
      f"VOH min {VOH_MIN:.2f} V vs RDS spec at {FET['rds_vgs']} V; tones {min(notes)}-{max(notes)} Hz")
print("PASS" if not fail else "FAIL", fail)
sys.exit(1 if fail else 0)
