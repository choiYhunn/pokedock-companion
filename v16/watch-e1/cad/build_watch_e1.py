"""PokeDock E1 "desk watch" - PRELIMINARY CAD (2026-11-16). Not approved, not printed, not fit-tested.

usage: python build_watch_e1.py <vendor parts dir (masterball-m6/vendor_cache/parts)> <out dir>

Same Waveshare ESP32-S3-Touch-AMOLED-1.43 (SKU 30106) and the same M7 firmware. Three printed parts:
  1. head   - round case with the bezel lip, two small Gengar-like ears, USB-C / J10 notch at the bottom
  2. back   - back cover screwed to the board's 4 standoffs (M2) and to the head (3 x M2 PT),
              with a stem that drops into the base
  3. base   - low oval foot; holds the stem, gives the USB-C plug + right-angle adapter a pocket and a
              rear cable exit. Optional sound unit (DFR0534 + 28 mm speaker) is a later variant of the base.
No hinge, lid, magnets, reed sensor or ballast. Board frame = the vendor STEP frame: glass top at
z = +1.10, standoff ends at z = -9.12, USB-C mouth toward -x (that edge is the bottom of the watch).
Checks written to <out>/watch_e1_report.json: board vs printed parts interference, USB / J10 plug
clearance, tip-over margin of the head on the base (rough masses), print sizes.
"""
import glob
import json
import math
import os
import sys

import numpy as np
import trimesh
from build123d import (Align, Axis, Box, Cylinder, Location, Plane, Pos, Rot, export_stl, fillet)

PARTS, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

# --- board (vendor STEP, verified in M6/M7) -----------------------------------------------------
GLASS_R, GLASS_TOP, STANDOFF_END = 23.0, 1.10, -9.12
STANDOFFS = [(sx * 11.6, sy * 15.75) for sx in (-1, 1) for sy in (-1, 1)]
HEADERS = [(-4.6, 4.6, -18.5, -14.0), (-4.6, 4.6, 14.0, 18.5)]          # 2x7 headers reach z = -9.6
USB_PLUG = dict(x=(-36.0, -21.5), y=(-6.3, 6.3), z=(-9.6, -2.9))         # C plug overmold 12.4 x 6.5 + slack
J10_PLUG = dict(x=(-27.5, -18.0), y=(6.5, 16.9), z=(-9.3, -5.4))         # M7 J10_PLUG_U in the STEP frame

# --- head ---------------------------------------------------------------------------------------
HEAD_OR = 30.0                 # d60 outer
BORE_R = GLASS_R + 0.5         # glass / PCB bore
LIP_GAP, LIP_T = 0.6, 2.0      # no load on the glass (as M7)
WINDOW_R = 22.4                # shows the glass's own black ring (as M7)
Z_LIP0 = GLASS_TOP + LIP_GAP
Z_FRONT = Z_LIP0 + LIP_T
Z_BACK = STANDOFF_END          # head back face flush with the standoff ends
EAR_H, EAR_W, EAR_AZ = 9.0, 11.0, 38.0   # two small ears, +/-38 deg from the top (+x)

# --- back ---------------------------------------------------------------------------------------
BACK_T = 3.0
M2_CLEAR, M2_CSK, M2_PILOT = 2.3, 4.4, 1.7
HEAD_SCREW_R, HEAD_SCREW_AZ = 27.0, (60.0, 180.0, 300.0)
STEM = (16.0, 12.0, 5.0)       # tongue below the head: x (down) length, y width, z thickness - into the base slot

# --- base ---------------------------------------------------------------------------------------
TILT = 15.0                    # screen leans back 15 deg from vertical
BASE = (74.0, 54.0, 12.0)      # footprint x (front-back), y, height


def stl(shape, name):
    p = os.path.join(OUT, name)
    export_stl(shape, p, tolerance=0.02, angular_tolerance=0.15)
    return trimesh.load(p)


def head():
    body = Cylinder(HEAD_OR, Z_FRONT - Z_BACK, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Pos(0, 0, Z_BACK))
    body -= Cylinder(BORE_R, Z_LIP0 - Z_BACK + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Pos(0, 0, Z_BACK - 0.01))
    body -= Cylinder(WINDOW_R, LIP_T + 1, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Pos(0, 0, Z_LIP0 - 0.5))
    # front chamfer-like softening: a shallow outer bevel ring
    body = fillet(body.edges().filter_by(Axis.Z, reverse=True).group_by(Axis.Z)[-1], 1.2)
    for az in (EAR_AZ, -EAR_AZ):    # ears on the top edge (+x is the top: USB is at -x), pointing outward
        ear = Box(EAR_H + 3.0, EAR_W, 8.0, align=(Align.MIN, Align.CENTER, Align.CENTER))
        ear = fillet(ear.edges().filter_by(Axis.Z), 3.0)
        body += ear.moved(Location((HEAD_OR - 3.0, 0, (Z_FRONT + Z_BACK) / 2))).moved(Location((0, 0, 0), (0, 0, 1), az))
    # USB-C + J10 notch through the bottom wall, open to the back
    lo_y, hi_y = USB_PLUG["y"][0] - 0.5, J10_PLUG["y"][1] + 0.5
    notch = Box(HEAD_OR - 17.0 + 1.0, hi_y - lo_y, -2.4 - Z_BACK + 0.01, align=(Align.MAX, Align.MIN, Align.MIN))
    body -= notch.moved(Pos(-17.0, lo_y, Z_BACK - 0.01))   # J10 sits in the corner of the bore: start at x = -17
    # 3 screw bosses inside the back face for the back cover (M2 PT pilots)
    for az in HEAD_SCREW_AZ:
        a = math.radians(az)
        x, y = HEAD_SCREW_R * math.cos(a), HEAD_SCREW_R * math.sin(a)
        body -= Cylinder(M2_PILOT / 2, 7.0, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Pos(x, y, Z_BACK - 0.01))
    return body


def back():
    plate = Cylinder(HEAD_OR, BACK_T, align=(Align.CENTER, Align.CENTER, Align.MAX)).moved(Pos(0, 0, Z_BACK))
    for x, y in STANDOFFS:          # countersunk M2 into the board standoffs
        plate -= Cylinder(M2_CLEAR / 2, BACK_T + 1, align=(Align.CENTER, Align.CENTER, Align.MAX)).moved(Pos(x, y, Z_BACK + 0.5))
        plate -= Cylinder(M2_CSK / 2, 1.2, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Pos(x, y, Z_BACK - BACK_T - 0.01))
    for az in HEAD_SCREW_AZ:
        a = math.radians(az)
        x, y = HEAD_SCREW_R * math.cos(a), HEAD_SCREW_R * math.sin(a)
        plate -= Cylinder(M2_CLEAR / 2, BACK_T + 1, align=(Align.CENTER, Align.CENTER, Align.MAX)).moved(Pos(x, y, Z_BACK + 0.5))
    for x0, x1, y0, y1 in HEADERS:  # the 2x7 headers reach 0.5 mm past the standoffs
        plate -= Box(x1 - x0 + 1.0, y1 - y0 + 1.0, 1.0, align=(Align.CENTER, Align.CENTER, Align.MAX)).moved(
            Pos((x0 + x1) / 2, (y0 + y1) / 2, Z_BACK + 0.01))
    lo_y, hi_y = USB_PLUG["y"][0] - 0.5, J10_PLUG["y"][1] + 0.5   # notch reaches in to x = -17 (USB / J10 plug bodies)
    plate -= Box(HEAD_OR - 17.0 + 1.0, hi_y - lo_y, BACK_T + 1, align=(Align.MAX, Align.MIN, Align.MAX)).moved(
        Pos(-17.0, lo_y, Z_BACK + 0.5))
    # stem below the head (toward -x), on the back side, beside the USB notch (+y side would hit J10: use -y)
    stem = Box(STEM[0] + 6.0, STEM[1], STEM[2], align=(Align.MAX, Align.CENTER, Align.MAX)).moved(
        Pos(-HEAD_OR + 6.0, -14.0, Z_BACK))
    stem -= Cylinder(1.25, STEM[1] + 2, rotation=(90, 0, 0)).moved(Pos(-HEAD_OR - STEM[0] + 5.0, -14.0, Z_BACK - STEM[2] / 2))
    return plate + stem


def base():
    b = Box(*BASE, align=(Align.CENTER, Align.CENTER, Align.MIN))
    b = fillet(b.edges().filter_by(Axis.Z), 14.0)
    return b


# ---- build -----------------------------------------------------------------------------------------
H, B = head(), back()
mh, mb = stl(H, "e1_head.stl"), stl(B, "e1_back.stl")
# the base is a placeholder slab (footprint and height only) until the stem socket is fixed at fit
mbase = stl(base(), "e1_base_placeholder.stl")

# ---- checks ----------------------------------------------------------------------------------------
board = trimesh.util.concatenate([trimesh.load(f) for f in sorted(glob.glob(os.path.join(PARTS, "*.stl")))])
rep = {"status": "PRELIMINARY - CAD only, nothing printed or fitted", "checks": {}}


def overlap(a, b):
    try:
        i = trimesh.boolean.intersection([a, b], engine="manifold")
        return round(float(i.volume), 2) if i and not i.is_empty else 0.0
    except Exception as e:  # noqa: BLE001
        return f"n/a ({type(e).__name__})"


board_parts = [trimesh.load(f) for f in sorted(glob.glob(os.path.join(PARTS, "*.stl")))]
for name, m in (("head", mh), ("back", mb)):
    hits = 0.0
    for p in board_parts:
        lo = np.maximum(p.bounds[0], m.bounds[0]); hi = np.minimum(p.bounds[1], m.bounds[1])
        if np.all(hi > lo):
            v = overlap(m, p)
            hits += v if isinstance(v, float) else 0
    rep["checks"][f"{name}_vs_board_mm3"] = round(hits, 2)


def box_mesh(d):
    return trimesh.creation.box(bounds=[[d["x"][0], d["y"][0], d["z"][0]], [d["x"][1], d["y"][1], d["z"][1]]])


for nm, d in (("usb_plug", USB_PLUG), ("j10_plug", J10_PLUG)):
    pm = box_mesh(d)
    rep["checks"][f"{nm}_vs_head_mm3"] = overlap(pm, mh)
    rep["checks"][f"{nm}_vs_back_mm3"] = overlap(pm, mb)
rep["sizes_mm"] = {n: (m.bounds[1] - m.bounds[0]).round(1).tolist() for n, m in (("head", mh), ("back", mb), ("base", mbase))}
rep["volume_cm3"] = {n: round(m.volume / 1000, 1) for n, m in (("head", mh), ("back", mb), ("base", mbase))}
# rough tip-over: head + board (20 g) on the base, centre of mass vs the base's rear edge
m_head = mh.volume / 1000 * 1.24 * 0.45 + mb.volume / 1000 * 1.24 * 0.45 + 20.0    # PLA, ~45 % effective fill
m_base = mbase.volume / 1000 * 1.24 * 0.45
h_cg = BASE[2] + HEAD_OR + 4.0
x_cg_head = -h_cg * math.sin(math.radians(TILT))       # leans back
x_cg = (m_head * x_cg_head) / (m_head + m_base)
rep["tip_estimate"] = {"mass_head_g": round(m_head, 1), "mass_base_g": round(m_base, 1),
                       "cg_offset_back_mm": round(-x_cg, 1), "base_half_depth_mm": BASE[0] / 2,
                       "margin_mm": round(BASE[0] / 2 - (-x_cg), 1),
                       "note": "ignores cable pull; a USB-C cable bending backward adds a tipping moment - keep the rear exit low"}
json.dump(rep, open(os.path.join(OUT, "watch_e1_report.json"), "w"), indent=1)
print(json.dumps(rep, indent=1))
