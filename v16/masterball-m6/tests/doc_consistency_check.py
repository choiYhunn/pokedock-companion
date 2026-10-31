"""Cross-document consistency for the Rev C release candidate.

Facts are taken from the machine-readable sources (harness.json, m6_params.py, BOM) and every
current user-facing document must agree with them. Historical documents (REV_B review, the audit)
are allowed to mention superseded parts only inside a marked "superseded" note.
usage: python doc_consistency_check.py
"""
import csv
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "cad"))
import m6_params as P  # noqa: E402

h = json.loads((ROOT / "electronics" / "harness.json").read_text(encoding="utf8"))
bom = list(csv.DictReader(open(ROOT / "procurement" / "BOM_M6.csv", encoding="utf8")))
CURRENT = ["README_KO.md", "docs/REV_C_FINAL_KO.md", "docs/G1_START_HERE_KO.md", "docs/G1_G2_INSPECTION_KO.md",
           "electronics/wiring_m6.svg", "procurement/BOM_M6.csv", "mobile/README_KO.md"]
text = {f: (ROOT / f).read_text(encoding="utf8") for f in CURRENT}
fail = []


def need(doc, *frags):
    for fr in frags:
        if fr not in text[doc]:
            fail.append(f"{doc}: missing '{fr}'")


def forbid(doc, pattern, why):
    for m in re.finditer(pattern, text[doc]):
        line = text[doc][max(0, m.start() - 160):m.end() + 40]
        if not re.search(r"(대체|이전|superseded|replaces|교체|why_not|대신|바꿨|바뀌|Rev B)", line):
            fail.append(f"{doc}: '{m.group(0)}' presented as current ({why})")


# driver circuit: AO3400A / 100 ohm gate / 100 k pull-down / 1N4148 / WT-1205 5 V
for doc in ("docs/G1_START_HERE_KO.md", "docs/REV_C_FINAL_KO.md", "docs/G1_G2_INSPECTION_KO.md"):
    need(doc, "AO3400A", "100 Ω", "100 kΩ", "1N4148")
need("electronics/wiring_m6.svg", "AO3400A", "100 Ω", "100 kΩ", "WT-1205")
for doc in CURRENT:
    forbid(doc, r"2N3904", "driver is AO3400A in Rev C")
    forbid(doc, r"470\s?(Ω|ohm)", "gate resistor is 100 ohm")
if "pin 1 = G, pin 2 = S, pin 3 = D" not in h["buzzer_driver"]["Q1"]:
    fail.append("harness Q1 lacks the SOT-23 pin map")
need("docs/G1_START_HERE_KO.md", "1 = G", "2 = S", "3 = D")
# USB pads + harness lengths
need("docs/G1_START_HERE_KO.md", "JP1-2", "JP1-1", "JP1-6", "JP1-5")
lens = {w["wire"]: w["len_mm"] for w in h["harness"]}
need("docs/G1_START_HERE_KO.md", f"{lens['W3']} mm", f"{lens['W5']} mm", f"{lens['W6']} mm", f"{lens['W8']} mm")
# CAD dims quoted in docs
bw, bh, bt = P.DRV_BOARD
need("docs/REV_C_FINAL_KO.md", f"{bw:g}×{bh:g}×{bt:g}")
need("docs/G1_START_HERE_KO.md", f"{bw:g}×{bh:g}")
# BOM carries the same parts
bom_text = " ".join(" ".join(r.values()) for r in bom)
for part in ("AO3400A", "WT-1205", "MF-R075", "1N4148", "4090", "30106"):
    if part not in bom_text:
        fail.append(f"BOM lacks {part}")
if not any("100 ohm" in r["exact_part_or_spec"] for r in bom) or not any("100 kohm" in r["exact_part_or_spec"] for r in bom):
    fail.append("BOM resistor values differ from the circuit")
if not any(f"{P.DRV_FOAM:.1f} mm" in r["exact_part_or_spec"] and "foam" in r["exact_part_or_spec"] for r in bom):
    fail.append("BOM foam tape thickness differs from CAD DRV_FOAM")
print("PASS" if not fail else "FAIL", fail)
sys.exit(1 if fail else 0)
