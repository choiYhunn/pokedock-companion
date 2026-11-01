"""Sweep the screen (pod) position and record why POD_C was chosen.

usage: python optimize_pod.py <cad_out_dir> <vendor_parts_dir> <report.json>
For each candidate offset (dy, dz) of the whole pod (bezel + cradle + board) from POD_C:
  - worst visible fraction of the active area over the 6 hardest seated eyes (lowest, farthest, sideways)
  - lowest eye height (mm above desk, 550 mm in front) that sees the full active area
  - closed-lid clearance pod -> lid / liner (mm)
  - USB-C mouth height vs the deck top (the right-angle adapter must stay hidden under the deck)
"""
import glob
import json
import math
import os
import sys

import numpy as np
import trimesh

sys.path.insert(0, os.path.dirname(__file__))
import m7_params as P  # noqa: E402
import view_check as VC  # noqa: E402

CAD, VEND, OUT = sys.argv[1:4]
ld = {os.path.basename(f)[:-4]: trimesh.load(f) for f in glob.glob(f"{CAD}/stl/*.stl")}
LID = ["lid_lavender", "lid_liner_lavender", "ear_left_pink", "ear_right_pink"]
M = trimesh.transformations.rotation_matrix(math.radians(-P.OPEN_DEG), [1, 0, 0], [0, P.PIVOT_Y, P.PIVOT_Z])
fixed_occ = []
for k in ("lower_shell_ivory", "belt_black", "button_ring_black", "button_white"):
    fixed_occ.append(ld[k])
for k in LID:
    m = ld[k].copy()
    m.apply_transform(M)
    fixed_occ.append(m)
lid_closed = trimesh.util.concatenate([ld["lid_lavender"], ld["lid_liner_lavender"]])
pod = [ld["display_bezel_plum"], ld["display_cradle_plum"]]
HARD = [(lat, 700.0, 350.0) for lat in (-150.0, 0.0, 150.0)] + [(lat, 550.0, 350.0) for lat in (-150.0, 150.0)] + [(0.0, 450.0, 350.0)]
t = math.radians(P.POD_ROT_DEG)
mouth_z0 = P.POD_C[2] + 7.4 * math.sin(t) + P.USB_MOUTH_ZU * math.cos(t)

rows = []
for dz in (-6.0, -3.0, 0.0, 3.0, 6.0):
    for dy in (-6.0, -3.0, 0.0, 3.0, 6.0):
        moved = []
        for m in pod:
            mm = m.copy()
            mm.apply_translation([0, dy, dz])
            moved.append(mm)
        bezel_only = moved[0]
        occ = trimesh.util.concatenate(fixed_occ + [bezel_only])
        pts = VC.active_points(dy, dz, nr=8, nt=24)
        worst = min(VC.visible_fraction(occ, pts, VC.eye_point(*e)) for e in HARD)
        low = VC.lowest_full_view_height(occ, dy=dy, dz=dz)
        gap = VC.min_clearance(moved, lid_closed, n=2500)
        mouth = mouth_z0 + dz
        ok = worst >= 0.995 and gap >= 3.0 and mouth <= P.DECK_TOP_Z + 2.0
        rows.append({"dy": dy, "dz": dz, "worst_visible": round(float(worst), 4), "lowest_full_view_h_mm": low,
                     "closed_gap_mm": round(gap, 2), "usb_mouth_minus_deck_mm": round(mouth - P.DECK_TOP_Z, 1), "ok": ok})
        print(rows[-1])
ok_rows = [r for r in rows if r["ok"]]
# preference among feasible positions: highest screen (photo: screen fills the opening), then lowest
# cut-off eye height, then the larger closed-lid gap
best = max(ok_rows, key=lambda r: (r["dz"], -(r["lowest_full_view_h_mm"] or 999), round(r["closed_gap_mm"]), -abs(r["dy"]))) if ok_rows else None
# (gap rounded to 1 mm: surface sampling noise is ~0.2 mm, so a 0.1 mm "gain" is not a reason to move the pod)
json.dump({"pod_c": P.POD_C, "candidates": rows, "chosen_offset": best,
           "rule": "feasible = all 6 hardest eyes >= 99.5 % visible, closed gap >= 3 mm, USB mouth <= deck + 2 mm"},
          open(OUT, "w"), indent=1)
print("best", best)
sys.exit(0 if best and best["dy"] == 0.0 and best["dz"] == 0.0 else 1)
