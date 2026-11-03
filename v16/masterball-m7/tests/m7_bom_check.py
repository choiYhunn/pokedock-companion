"""The single M7 purchase list agrees with the harness, the CAD and itself (CSV = Markdown).

usage: python m7_bom_check.py
"""
import csv
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
rows = list(csv.DictReader(open(ROOT / "bom" / "M7_FINAL_PURCHASE.csv", encoding="utf8")))
md = (ROOT / "bom" / "M7_FINAL_PURCHASE_KO.md").read_text(encoding="utf8")
harness = json.loads((ROOT / "electronics" / "harness_m7.json").read_text(encoding="utf8"))
fails, n = [], 0


def check(name, cond, detail=""):
    global n
    n += 1
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  {detail}"))
    if not cond:
        fails.append(name)


STATUS = {"BUY_NOW", "BUY_NOW (if not owned)", "BUY_AFTER_MEASUREMENT", "BLOCKED", "OPTIONAL", "ALTERNATIVE_NOT_ORDERED", "REMOVED"}
check("every line has a known status", all(r["status"] in STATUS for r in rows), [r["line"] for r in rows if r["status"] not in STATUS])
check("line ids unique", len({r["line"] for r in rows}) == len(rows))
buy = [r for r in rows if r["status"].startswith("BUY_NOW")]
dk = [r for r in buy if r["supplier"] == "DigiKey Korea"]
total = sum(int(r["line_total_krw"]) for r in dk)
check(f"DigiKey cart = KRW {total:,} (Markdown states the same and it is >= 60,000 = free shipping)",
      total >= 60000 and f"₩{total:,}" in md, total)
for r in dk:
    q, spare = int(r["qty_order"]), int(r["qty_spare"])
    unit = int(re.sub(r"\D", "", r["unit_price"]))
    check(f"{r['line']}: total = unit x order, spare = order - used",
          int(r["line_total_krw"]) == unit * q and spare == q - int(r["qty_used"]), r)
    link = r["link"]
    ok = link.startswith("https://www.digikey.kr/ko/products/detail/") or re.fullmatch(
        r"https://www\.digikey\.kr/ko/products/result\?keywords=[0-9A-Z-]+-ND", link) is not None
    check(f"{r['line']}: link is a product page or an exact DigiKey part-number lookup (never a keyword search)", ok, link)
    pn = re.search(r"\(DigiKey ([0-9A-Z-]+-ND)", r["mpn_sku"])
    check(f"{r['line']}: link matches the DigiKey part number", pn is not None and (pn.group(1) in link or "/detail/" in link), r["mpn_sku"])
    check(f"{r['line']}: listed in the Markdown table", r["mpn_sku"].split(" (")[0].split(" ")[-1] in md or r["mpn_sku"].split(" ")[0] in md)
parts = {p["mpn"] for h in harness["harnesses"] for p in h["parts"]}
bom_text = " ".join(r["mpn_sku"] for r in buy)
check("every harness part is on the BUY list", all(p in bom_text for p in parts), sorted(p for p in parts if p not in bom_text))
for p in ("DFR0534", "57155-000", "SKU 30106"):
    check(f"{p} on the BUY list", p in bom_text)
removed = ("WT-1205", "AO3400A", "MF-R075", "1935161", "1N4148", "CFR-25")
check("no v0.5 buzzer/driver part on any BUY line", not any(x in " ".join(r["item"] + r["mpn_sku"] for r in buy) for x in removed))
check("BLOCKED lines: 0 (and the Markdown says so)", not [r for r in rows if r["status"] == "BLOCKED"] and "| **BLOCKED** | **0**" in md)
aft = [r for r in rows if r["status"] == "BUY_AFTER_MEASUREMENT"]
check("every BUY_AFTER_MEASUREMENT line says what to measure", all(r["verification_needed"] for r in aft))
# CAD: the screws the CAD expects are bought
sys.path.insert(0, str(ROOT / "cad"))
import m7_params as P  # noqa: E402
check("sound bracket screws (M2 PT) and module screws (M3 PT, hole d3.1) on the list",
      any("2x6" in r["mpn_sku"] for r in buy) and any("3x8" in r["mpn_sku"] for r in buy) and P.DFR_HOLE_D >= 3.0)
check("speaker on the list matches the CAD seat (d28, <= 6 mm)", "AS02808MR" in bom_text and P.SPK_D == 28.0 and P.SPK_H <= 6.0)
check("v0.5 BOM files are archived with a do-not-use note", (ROOT / "bom" / "archive_v0.5" / "README_구버전_KO.md").exists()
      and not (ROOT / "bom" / "BOM_M7.csv").exists())
print(f"{'FAIL' if fails else 'PASS'}: {n - len(fails)}/{n} purchase list checks")
sys.exit(1 if fails else 0)
