"""Buzzer driver board (AO3400A perfboard, 24x18x10 mm envelope) installation check.

Checks the CAD envelope against everything around it, its insertion path, that the display
sub-assembly / upper shell never pass over it, the foam-tape gap to the curved wall, the space left
for component leads on the back, and that every harness wire reaches with routing slack.
usage: python driver_board_check.py <cad_out_dir> <report.json>
"""
import json
import math
import os
import sys

import numpy as np
import trimesh

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tests"))
import m6_params as P  # noqa: E402
from source_fingerprint import fingerprint  # noqa: E402

CAD, OUT = sys.argv[1:3]
ROOT = os.path.join(os.path.dirname(__file__), "..")
board = trimesh.load(f"{CAD}/purchased/buzzer_driver_board.stl")
bodies = {k: trimesh.load(f"{CAD}/stl/{k}.stl") for k in ("lower_shell_ivory", "upper_shell_purple", "bezel_black", "display_plate_petg")}
for k in ("buzzer", "usb_breakout", "steel_disc", "socket_left", "socket_right", "m3x50_0", "m3x50_1", "m3x50_2", "usb_screw_l", "usb_screw_r"):
    bodies[k] = trimesh.load(f"{CAD}/purchased/{k}.stl")
fail, rep = [], {}

# 1 clearance to every neighbour
def min_dist(a, b, n=15000):
    pa, _ = trimesh.sample.sample_surface_even(a, n)
    d = trimesh.proximity.ProximityQuery(b).signed_distance(pa)
    return float(-d.max())


clr = {k: round(min_dist(board, m), 2) for k, m in bodies.items()}
rep["clearance_mm"] = clr
for k, v in clr.items():
    if v < (P.DRV_PAD_GAP - 0.05 if k == "lower_shell_ivory" else 2.0):
        fail.append(f"driver board too close to {k}: {v} mm")

# 2 insertion: pressed onto the wall along +n from 25 mm inside, lower shell open
n = np.array(P.unit(P.DRV_AZ_DEG, P.DRV_EL_DEG))
hits = []
for s in np.arange(25.0, 0.0, -1.0):
    m = board.copy()
    m.apply_translation(-n * s)
    for k in ("lower_shell_ivory", "buzzer", "usb_breakout", "steel_disc", "m3x50_0", "m3x50_1", "m3x50_2"):
        if m.intersection(bodies[k], engine="manifold").volume > 0.05:
            hits.append((round(float(s), 1), k))
rep["insertion_path_hits"] = hits
if hits:
    fail.append(f"insertion path blocked {hits[:3]}")

# 3 later assembly steps never sweep over the board (they move along z only)
def xy_overlap(a, b):
    return np.all(a.bounds[0][:2] <= b.bounds[1][:2]) and np.all(b.bounds[0][:2] <= a.bounds[1][:2])


sub = trimesh.util.concatenate([bodies["bezel_black"], bodies["display_plate_petg"], bodies["socket_left"], bodies["socket_right"]])
rep["display_subassembly_xy_overlap"] = bool(xy_overlap(board, sub))
rep["board_top_z"] = round(float(board.bounds[1][2]), 1)
if rep["display_subassembly_xy_overlap"]:
    fail.append("display sub-assembly is lowered over the driver board")
if board.bounds[1][2] > P.BH - 5:
    fail.append("driver board reaches the equator zone where the upper shell lands")

# 4 foam tape on the two printed seat pads (flat, so the gap is uniform); lead zone = between pads
bw, bh, bt = P.DRV_BOARD
c0 = P.DRV_C0


def gap(u, v):
    return math.sqrt(P.RI ** 2 - (u * u + v * v)) - c0


inner = [gap(u, v) for u in np.linspace(-bw / 2 + P.DRV_PAD_W + 1, bw / 2 - P.DRV_PAD_W - 1, 9)
         for v in np.linspace(-bh / 2 + 1, bh / 2 - 1, 7)]
foam = P.DRV_FOAM
comp = round(100 * (foam - P.DRV_PAD_GAP) / foam)
rep["tape"] = {"foam_thickness_mm": foam, "pads": f"2 x ({P.DRV_PAD_W:g} x {bh:g} mm) printed seat pads, gap {P.DRV_PAD_GAP} mm",
               "tape_area_mm2": 2 * P.DRV_PAD_W * bh, "foam_compression_pct": [comp, comp],
               "lead_zone_gap_min_mm (between pads)": round(min(inner), 2),
               "board_mass_g_est": 3.0, "note": "adhesion on rough FDM layers: IPA wipe, 30 s press; hot-melt fillet as backup"}
cmin, cmax = rep["tape"]["foam_compression_pct"]
if not (5 <= cmin and cmax <= 60):
    fail.append(f"foam compression {cmin}-{cmax} % outside 5-60 %")
if min(inner) < 1.0 + 0.06 + 0.3:   # trimmed leads 1.0 mm + Kapton + margin
    fail.append("not enough room behind the board for trimmed leads + Kapton")

# 5 wire reach with routing slack (x1.3 + 20 mm service loop)
h = json.load(open(os.path.join(ROOT, "electronics", "harness.json"), encoding="utf8"))
bc = board.bounds.mean(axis=0)
ends = {"J1 (either header)": [np.array([sx * P.HEADERS_X, P.PLATE_BACK_Y + 5, 0.0]) for sx in (-1, 1)],
        "USB breakout": [bodies["usb_breakout"].bounds.mean(axis=0)],
        "buzzer": [bodies["buzzer"].bounds.mean(axis=0)]}
need = {k: max(float(np.linalg.norm(e - bc)) for e in v) * 1.3 + 20 for k, v in ends.items()}
have = {"J1 (either header)": next(w["len_mm"] for w in h["harness"] if w["wire"] == "W5"),
        "USB breakout": min(w["len_mm"] for w in h["harness"] if w["wire"] in ("W6", "W7")),
        "buzzer": min(w["len_mm"] for w in h["harness"] if w["wire"] in ("W8", "W9"))} if any(
    w["wire"] == "W8" for w in h["harness"]) else {}
rep["wire_reach_mm"] = {k: {"needed": round(need[k]), "harness": have.get(k)} for k in need}
for k in need:
    if have.get(k) is None or have[k] < need[k]:
        fail.append(f"wire to {k} too short: needs {need[k]:.0f} mm, harness {have.get(k)}")

rep["source_fingerprint"] = fingerprint()
rep["verdict"] = "PASS" if not fail else "FAIL"
rep["fail"] = fail
json.dump(rep, open(OUT, "w"), indent=1)
print(json.dumps(rep, indent=1))
sys.exit(1 if fail else 0)
