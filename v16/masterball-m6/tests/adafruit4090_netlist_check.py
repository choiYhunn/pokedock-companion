"""Check the harness against the Adafruit 4090 (USB-C downstream breakout, rev B) Eagle schematic:
VBUS/GND/D+/D- pad numbers and the 5.1 k sink pull-downs on BOTH CC1 and CC2.
usage: python adafruit4090_netlist_check.py "<Adafruit USB Type C Downstream Breakout rev B.sch>"
(https://github.com/adafruit/Adafruit-USB-C-Downstream-Breakout, CC BY-SA - not redistributed here)
"""
import json
import pathlib
import re
import sys

sch = open(sys.argv[1], encoding="utf8").read()
nets = {}
for m in re.finditer(r'<net name="([^"]+)"[^>]*>(.*?)</net>', sch, re.S):
    nets[m.group(1)] = set(re.findall(r'<pinref part="([^"]+)" gate="[^"]*" pin="([^"]+)"/>', m.group(2)))
values = dict(re.findall(r'<part name="(R\d)"[^>]*value="([^"]+)"', sch))
h = json.loads((pathlib.Path(__file__).resolve().parent.parent / "electronics" / "harness.json").read_text(encoding="utf8"))
fail = []
for wire, net in (("W1", "VBUS"), ("W2", "GND"), ("W3", "D+"), ("W4", "D-")):
    w = next(x for x in h["harness"] if x["wire"] == wire)
    pad = re.search(r"JP1-(\d+)", w["from"]).group(1)
    if ("JP1", pad) not in nets.get(net, set()):
        fail.append(f"{wire}: JP1-{pad} is not {net}")
for cc in ("CC1", "CC2"):
    rs = [p for p, _ in nets.get(cc, set()) if p.startswith("R")]
    if len(rs) != 1 or values.get(rs[0]) != "5.1K" or (rs[0], "1") not in nets["GND"]:
        fail.append(f"{cc} has no 5.1k pull-down to GND")
print({k: sorted(v) for k, v in nets.items() if k in ("VBUS", "D+", "D-", "CC1", "CC2")}, values)
print("PASS" if not fail else "FAIL", fail)
sys.exit(1 if fail else 0)
