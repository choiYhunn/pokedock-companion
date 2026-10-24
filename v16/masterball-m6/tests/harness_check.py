"""Cross-check the M6 harness against the vendor pin map and the firmware pin defines.
Fails if a harness wire lands on a pin whose schematic net differs, if firmware uses a pin
reserved by the board, or if a strapping pin is driven.
usage: python harness_check.py
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
h = json.loads((ROOT / "electronics" / "harness.json").read_text(encoding="utf8"))
board_h = (ROOT / "firmware" / "main" / "board.h").read_text(encoding="utf8")
fail = []
for w in h["harness"]:
    for end in (w["from"], w["to"]):
        m = re.match(r"(J\d)-(\d+)", end)
        if m:
            net = h["board_pins"][m.group(1)][m.group(2)]
            if not net.startswith(w["net"]):
                fail.append(f'{w["wire"]}: {end} is {net}, harness says {w["net"]}')
pins = {k: int(v) for k, v in re.findall(r"#define PD_PIN_(\w+) (\d+)", board_h)}
expect = {"LCD_CS": 9, "LCD_CLK": 10, "LCD_D0": 11, "LCD_D1": 12, "LCD_D2": 13, "LCD_D3": 14, "LCD_RST": 21,
          "I2C_SDA": 47, "I2C_SCL": 48, "RTC_INT": 15, "VCC_ADC": 4, "BUZZER": 16}
for k, v in expect.items():
    if pins.get(k) != v:
        fail.append(f"firmware PD_PIN_{k}={pins.get(k)} expected {v} (schematic)")
if pins.get("BUZZER") in (0, 3, 45, 46):
    fail.append("buzzer on a strapping pin")
if "IO16" != h["board_pins"]["J1"]["8"]:
    fail.append("J1-8 is not IO16")
for w in h["harness"]:
    if "VBAT" in w["to"] or w["to"] == "J1-2":
        fail.append(f'{w["wire"]} touches VBAT (no battery in M6)')
print("harness wires:", len(h["harness"]), "| firmware pins:", pins)
print("PASS" if not fail else "FAIL", fail)
sys.exit(1 if fail else 0)
