"""FDM tolerance stack + sensitivity for the M6 critical fits (worst case and Monte Carlo).

verify_m6.py checks geometric clearance against a symmetric +/-0.15 mm per surface. Real FDM
is biased (outer walls bulge, holes print small), shrinks by material, and assembly play moves
parts. This model makes each contributor explicit (radial mm, + = more clearance):

  outer_wall  printed outer surface  : -0.20 .. 0.00   (bulge / seam)
  hole_wall   printed hole surface   : -0.25 .. 0.00   (holes print undersize)
  shrink      PLA 0.2-0.5 %, PETG 0.3-0.8 % of the feature radius (outer grows clearance,
              hole loses it); same-material pairs share 70 % of their shrink (same spool/shop)
  position    assembly play between the two features (screw-in-hole, spigot float, ...)
  vendor      purchased-part tolerance from its drawing

usage: python tolerance_stack.py <out.json> [--n 200000]
"""
import json
import sys

import numpy as np

sys.path.insert(0, __import__("os").path.dirname(__file__))
import m6_params as P  # noqa: E402

N = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 200_000
rng = np.random.default_rng(20261024)
SHRINK = {"PLA": (0.002, 0.005), "PETG": (0.003, 0.008)}


def U(lo, hi):
    return rng.uniform(lo, hi, N)


def fit(name, nominal, outer=None, hole=None, position=0.0, vendor=0.0, extra=None):
    """outer/hole = (material, radius) of a printed outer feature / printed hole; None = vendor part."""
    terms = {}
    s_common = U(0, 1)
    if outer:
        mat, r = outer
        lo, hi = SHRINK[mat]
        terms["outer_wall"] = U(-0.20, 0.0)
        s = lo + (hi - lo) * (0.7 * s_common + 0.3 * U(0, 1))
        terms["outer_shrink"] = s * r
    if hole:
        mat, r = hole
        lo, hi = SHRINK[mat]
        terms["hole_wall"] = U(-0.25, 0.0)
        same = outer and outer[0] == mat
        s = lo + (hi - lo) * ((0.7 * s_common + 0.3 * U(0, 1)) if same else U(0, 1))
        terms["hole_shrink"] = -s * r
    if position:
        terms["position"] = -np.abs(U(-position, position))
    if vendor:
        terms["vendor"] = U(-vendor, vendor)
    for k, (lo, hi) in (extra or {}).items():
        terms[k] = U(lo, hi)
    total = nominal + sum(terms.values())
    worst = nominal + sum(t.min() for t in terms.values())
    var = {k: float(np.var(t)) for k, t in terms.items()}
    vs = sum(var.values())
    return {"fit": name, "nominal_mm": round(nominal, 3), "worst_case_min_mm": round(float(worst), 3),
            "p0_1_percentile_mm": round(float(np.percentile(total, 0.1)), 3),
            "p_interference": float((total < 0).mean()),
            "sensitivity_share": {k: round(v / vs, 2) for k, v in sorted(var.items(), key=lambda kv: -kv[1])}}


def analyse(opening_clr, pocket_clr, spigot_clr, usb_clr, screw_play):
    return [
        fit("F1 button bezel (PETG) in shell opening (PLA)", opening_clr, ("PETG", P.BEZEL_R), ("PLA", P.BEZEL_R + opening_clr),
            position=screw_play, extra={"opening_halves_shrink_offset": (-0.10, 0.10)}),
        fit("F2 display plate rim in opening throat", opening_clr, ("PETG", P.PLATE_R), ("PLA", P.BEZEL_R + opening_clr),
            position=screw_play),
        fit("F3 glass (vendor 46.00 +/-0.1) in bezel pocket (PETG)", pocket_clr, None, ("PETG", P.GLASS_R + pocket_clr),
            vendor=0.05),
        fit("F4 lower spigot (PLA) in belt / upper bore (PLA)", spigot_clr, ("PLA", P.SPIGOT_R_OUT), ("PLA", P.SPIGOT_R_OUT + spigot_clr)),
        fit("F5 USB receptacle slides through block slot (PLA)", usb_clr, None, ("PLA", 4.47 + usb_clr), vendor=0.05),
        fit("F6 buzzer d12 in pocket (PLA)", P.BUZ_FIT, None, ("PLA", 6.0 + P.BUZ_FIT), vendor=0.10),
        fit("F7 M3 shank in 35 mm column bore", P.M3_CLEAR / 2 - 1.5, None, ("PLA", P.M3_CLEAR / 2),
            extra={"bore_straightness": (-0.10, 0.0)}),
    ]


before = analyse(0.35, 0.30, 0.35, 0.30, screw_play=0.20)
after = analyse(P.OPENING_R - P.BEZEL_R, P.POCKET_R - P.GLASS_R, P.COUNTERBORE_R - P.SPIGOT_R_OUT, P.USB_SLOT_CLR,
                screw_play=P.SCREW_PLAY)
sweep = {}
for c in (0.35, 0.45, 0.55, 0.65, 0.75):
    r = analyse(c, 0.5, 0.55, 0.45, P.SCREW_PLAY)[0]
    sweep[f"{c:.2f}"] = {"worst": r["worst_case_min_mm"], "p_interference": r["p_interference"]}
out = {"model": __doc__, "samples": N, "before_m6_rev_a": before, "after_m6_rev_b": after,
       "opening_clearance_sweep": sweep}
json.dump(out, open(sys.argv[1], "w", encoding="utf8"), ensure_ascii=False, indent=1)
for tag, rows in (("REV A", before), ("REV B", after)):
    print(tag)
    for r in rows:
        print(f'  {r["fit"][:52]:52s} nom {r["nominal_mm"]:5.2f}  WC {r["worst_case_min_mm"]:6.3f}  '
              f'p0.1% {r["p0_1_percentile_mm"]:6.3f}  P(int) {r["p_interference"]:.4f}  top {list(r["sensitivity_share"].items())[:2]}')
print("opening sweep", sweep)
bad = [r["fit"] for r in after if r["p_interference"] > 0.001 or r["worst_case_min_mm"] < -0.15]
print("REV B", "PASS" if not bad else "FAIL", bad)
sys.exit(1 if bad else 0)
