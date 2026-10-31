"""Vendor package consistency: the turnkey documents must agree with the design sources.

- every purchasable line of procurement/BOM_M6.csv appears in vendor/BOM_TURNKEY.csv with order_qty >= design qty
- the 'NO substitution' parts are exactly the ones the CAD is built around (board, USB breakout, prints)
- the SOP harness table matches electronics/harness.json (wire, length, AWG, colour)
- spec / SOP quote the firmware version in core/protocol.hpp and the G1-E10 clock test exists
- package builder lists only files that exist
usage: python vendor_package_check.py
"""
import csv
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
fail = []
design = list(csv.DictReader(open(ROOT / "procurement/BOM_M6.csv", encoding="utf8")))
turnkey = list(csv.DictReader(open(ROOT / "vendor/BOM_TURNKEY.csv", encoding="utf8")))
tk_by_ref = {}
for r in turnkey:
    tk_by_ref.setdefault(r["ref"].rstrip("abc"), []).append(r)


def first_int(s):
    m = re.search(r"\d+", s or "")
    return int(m.group()) if m else 0


for d in design:
    if d["tier"].startswith(("TOOLS", "USER", "EXCLUDED")):
        continue
    rows = tk_by_ref.get(d["id"])
    if not rows:
        fail.append(f"design BOM {d['id']} ({d['item']}) missing from BOM_TURNKEY")
        continue
    need = first_int(d["qty"])
    have = max(first_int(r["order_qty"]) for r in rows)
    if "set" not in d["qty"] and have < need:
        fail.append(f"{d['id']}: order_qty {have} < design qty {need}")
for ref in ("X2", "X3"):
    if not any(r["ref"] == ref and r["stage"] == "EXCLUDED" for r in turnkey):
        fail.append(f"{ref} must stay EXCLUDED (no RTC cell / no LiPo)")
no_sub = {r["ref"] for r in turnkey if r["substitution"] == "NO"}
for must in ("E1", "E2", "C1", "C2"):
    if must not in no_sub:
        fail.append(f"{must} must be 'NO' substitution")
if not any("30106" in r["mpn_or_spec"] for r in turnkey):
    fail.append("board SKU 30106 not in BOM_TURNKEY")

h = json.loads((ROOT / "electronics/harness.json").read_text(encoding="utf8"))
sop = (ROOT / "vendor/03_SOP_BUILD_KO.md").read_text(encoding="utf8")
colour_ko = {"red": "빨강", "black": "검정", "green": "초록", "white": "흰색", "yellow": "노랑", "blue": "파랑"}
for w in h["harness"]:
    row = next((l for l in sop.splitlines() if l.startswith(f"| {w['wire']} |")), None)
    if not row:
        fail.append(f"SOP harness table lacks {w['wire']}")
        continue
    for frag in (f"{w['len_mm']} mm", f"{w['awg']} AWG", colour_ko[w["colour"]]):
        if frag not in row:
            fail.append(f"SOP {w['wire']}: '{frag}' differs from harness.json")
    for c in (w["colour"],):
        if not any(colour_ko[c] in r["notes"] or c in r["mpn_or_spec"] + r["substitute_must_meet"] + r["notes"]
                   for r in turnkey if r["category"] == "harness"):
            fail.append(f"BOM_TURNKEY harness wire colour {c} not listed")

fw = re.search(r'kFirmwareVersion = "([^"]+)"', (ROOT / "core/protocol.hpp").read_text(encoding="utf8")).group(1)
for doc in ("vendor/01_PRODUCT_SPEC_1P_KO.md", "vendor/03_SOP_BUILD_KO.md", "docs/CLOCK_WITHOUT_PHONE_KO.md"):
    if fw not in (ROOT / doc).read_text(encoding="utf8"):
        fail.append(f"{doc} does not quote firmware {fw}")
for doc in ("docs/G1_G2_INSPECTION_KO.md", "docs/G1_START_HERE_KO.md", "vendor/03_SOP_BUILD_KO.md",
            "vendor/04_ACCEPTANCE_GATES_KO.md"):
    if "G1-E10" not in (ROOT / doc).read_text(encoding="utf8"):
        fail.append(f"{doc} lacks the G1-E10 clock test")
if "G1-E10" not in (ROOT / "docs/G1_G2_RECORD_TEMPLATE.csv").read_text(encoding="utf8"):
    fail.append("record template lacks G1-E10")
fat = list(csv.DictReader(open(ROOT / "vendor/FAT_RECORD_TEMPLATE.csv", encoding="utf8")))
acc = (ROOT / "vendor/04_ACCEPTANCE_GATES_KO.md").read_text(encoding="utf8")
for r in fat:
    if f"| {r['id']} |" not in acc:
        fail.append(f"FAT {r['id']} not described in 04_ACCEPTANCE_GATES_KO.md")

src = (ROOT / "tools/make_vendor_package.py").read_text(encoding="utf8")
for rel in re.findall(r'"((?:vendor|docs|procurement|electronics|tests|cad)/[^"*]+\.(?:md|csv|json|svg|png))"', src):
    if not (ROOT / rel).exists():
        fail.append(f"package builder lists missing file {rel}")
print("PASS" if not fail else "FAIL", fail)
sys.exit(1 if fail else 0)
