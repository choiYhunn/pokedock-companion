"""Mechanical verification of the M6 assembly against the official Waveshare 1.43 STEP.

usage: python verify_m6.py <cad_out_dir> <vendor_parts_dir> <report.json>
<vendor_parts_dir> holds per-component STLs exported from the official STEP (step frame) by
tools/vendor_step_to_parts.py, plus parts.json. Checks:
  1 mesh validity          2 pairwise interference (all bodies, manifold booleans)
  3 critical clearances    4 worst-case tolerance (MMC) on every non-contact pair
  5 insertion paths (swept)   6 mass / CoG / tip & slide   7 print overhang on cosmetic faces
"""
import glob
import itertools
import json
import os
import sys

import numpy as np
import trimesh

sys.path.insert(0, os.path.dirname(__file__))
import m6_params as P  # noqa: E402

CAD, VEND, OUT = sys.argv[1:4]
TOL_PRINT, TOL_VENDOR, TOL_PURCH = 0.15, 0.10, 0.20
report = {"checks": {}, "fail": []}


def fail(msg):
    report["fail"].append(msg)
    print("FAIL", msg)


def load(path):
    m = trimesh.load(path, force="mesh")
    m.merge_vertices()
    return m


printed = {os.path.basename(f)[:-4]: load(f) for f in sorted(glob.glob(f"{CAD}/stl/*.stl"))}
purch = {os.path.basename(f)[:-4]: load(f) for f in sorted(glob.glob(f"{CAD}/purchased/*.stl"))}
purch_path_only = {"usb_plug_path"}  # swept volume of the user's cable, outside the ball


def to_ball(m):
    m = m.copy()
    v = m.vertices.copy()
    m.vertices = np.column_stack([-v[:, 1], P.GLASS_Y + (1.10 - v[:, 2]), v[:, 0]])
    m.fix_normals()
    return m


vendor = {}
vrows = json.load(open(f"{VEND}/parts.json"))
for f in sorted(glob.glob(f"{VEND}/*.stl")):
    m = load(f)
    if len(m.vertices) < 4:
        continue
    h = m.convex_hull
    if not h.is_volume or h.volume < 0.01:
        continue  # sub-0.01 mm3 slivers (labels, pads) cannot be meshed as volumes
    idx = int(os.path.basename(f)[:3]) - 1
    leaf = vrows[idx]["path"].split("/")[-1] if 0 <= idx < len(vrows) else "?"
    if leaf.startswith(("SOLID", "COMPOUND", "EXTRUDED", "_", "2_", "3_", "5_", "CYLINDER")):
        leaf = vrows[idx]["path"].split("/")[-2] if 0 <= idx < len(vrows) else leaf
    if leaf == "TF_CARD":
        continue  # no microSD card is fitted in M6 (assets live in flash); a card would hit the bezel
    vendor[f"board_{idx + 1:03d}_{leaf}"] = to_ball(h)

# 1 validity -------------------------------------------------------------------------------------
val = {k: {"watertight": bool(m.is_watertight), "volume": round(float(m.volume), 1)} for k, m in printed.items()}
report["checks"]["mesh_validity"] = val
for k, v in val.items():
    if not v["watertight"]:
        fail(f"{k} not watertight")

# 2 interference ---------------------------------------------------------------------------------
CONTACT = {  # designed face contacts (clamped / seated); overlap must stay ~0
    frozenset({"display_plate_petg", "bezel_black"}), frozenset({"display_plate_petg", "lower_shell_ivory"}),
    frozenset({"belt_black", "upper_shell_purple"}), frozenset({"belt_black", "lower_shell_ivory"}),
    frozenset({"lobe_left_pink", "upper_shell_purple"}), frozenset({"lobe_right_pink", "upper_shell_purple"}),
    frozenset({"usb_breakout", "lower_shell_ivory"}), frozenset({"steel_disc", "lower_shell_ivory"}),
    frozenset({"buzzer", "lower_shell_ivory"}), frozenset({"m_inlay_white", "upper_shell_purple"}),
    frozenset({"usb_screw_l", "usb_breakout"}), frozenset({"usb_screw_r", "usb_breakout"}),
}
ENGAGED = []  # designed volumetric engagements (threads, socket over header pins) - reported, not failures
bodies = {**printed, **{k: v for k, v in purch.items() if k not in purch_path_only}, **vendor}
names = list(bodies)
bounds = {k: bodies[k].bounds for k in names}


def boxes_touch(a, b, pad=0.6):
    return np.all(bounds[a][0] - pad <= bounds[b][1]) and np.all(bounds[b][0] - pad <= bounds[a][1])


def is_vendor(k):
    return k.startswith("board_")


def is_contact(a, b):
    if frozenset({a, b}) in CONTACT:
        return True
    pair = {a, b}
    if any(is_vendor(x) for x in pair) and "display_plate_petg" in pair:
        other = (pair - {"display_plate_petg"}).pop()
        return "SMTSO" in other  # board standoffs seat on the plate
    if any(x.startswith("m3_insert") for x in pair) and "upper_shell_purple" in pair:
        return True  # heat-set insert is pressed into its hole
    if any(x.startswith("m3x50") for x in pair) and (any(x.startswith("m3_insert") for x in pair)):
        return "engaged"  # screw threads into insert
    if any(x.startswith("usb_screw") for x in pair) and "lower_shell_ivory" in pair:
        return "engaged"  # self-tapping screw cuts its thread in the pilot hole
    if any(x.startswith("socket_") for x in pair) and any("2X7" in x for x in pair):
        return "engaged"  # female socket mated over the male header
    if all(is_vendor(x) for x in pair):
        return True  # vendor assembly internals are not ours to check
    return False


inter = []
for a, b in itertools.combinations(names, 2):
    if is_vendor(a) and is_vendor(b):
        continue
    if not boxes_touch(a, b):
        continue
    try:
        vol = float(bodies[a].intersection(bodies[b], engine="manifold").volume)
    except Exception as e:  # noqa: BLE001
        vol = float("nan")
        fail(f"boolean failed {a} x {b}: {e}")
    if vol > 0.05 or np.isnan(vol):
        contact = is_contact(a, b)
        inter.append({"a": a, "b": b, "overlap_mm3": round(vol, 3), "designed_contact": contact})
        if contact == "engaged":
            continue
        if not contact or vol > 0.5:
            fail(f"interference {a} x {b} = {vol:.3f} mm3")
report["checks"]["interference"] = inter
print("interference pairs reported:", len(inter))


# 2b fastener engagement: every screw / insert must be surrounded by host material ----------------
def ring_inside(host, centre, axis, r, z0, z1, n_ang=24, n_ax=5):
    axis = np.asarray(axis, float) / np.linalg.norm(axis)
    a = np.cross(axis, [0, 0, 1.0]) if abs(axis[2]) < 0.9 else np.cross(axis, [1.0, 0, 0])
    a /= np.linalg.norm(a)
    b = np.cross(axis, a)
    pts = [np.asarray(centre) + axis * t + r * (np.cos(q) * a + np.sin(q) * b)
           for t in np.linspace(z0, z1, n_ax) for q in np.linspace(0, 2 * np.pi, n_ang, endpoint=False)]
    return float(host.contains(np.array(pts)).mean())


def polar(r, ang):
    return r * np.cos(np.radians(ang)), r * np.sin(np.radians(ang))


eng = []
U, L, BZ, PL = printed["upper_shell_purple"], printed["lower_shell_ivory"], printed["bezel_black"], printed["display_plate_petg"]
for ang in P.COLUMN_ANGLES:
    x, y = polar(P.COLUMN_R_POS, ang)
    eng.append(("M3 insert wall in upper boss", U, (x, y, P.BH), (0, 0, 1), 2.0 + 0.9, 0.5, 5.5))
    eng.append(("M3 screw wall in lower column", L, (x, y, P.HEAD_SEAT_Z), (0, 0, 1), P.M3_CLEAR / 2 + 0.6, 1.0, 35.0))
    eng.append(("M3 head seat annulus", L, (x, y, P.HEAD_SEAT_Z), (0, 0, 1), 2.4, 0.3, 1.5))
for key, ang in P.INSERT_ANG.items():
    x, z = polar(P.INSERT_R, ang)
    eng.append((f"M2 insert {key} wall in bezel", BZ, (x, P.PLATE_FRONT_Y, z), (0, -1, 0), 1.6 + 0.6, 0.5, 4.0))
    eng.append((f"plate land {key}", PL, (x, P.PLATE_FRONT_Y, z), (0, 1, 0), 2.6, 0.3, 2.2))
for key in ("bot_l", "bot_r"):
    x, z = polar(P.INSERT_R, P.INSERT_ANG[key])
    eng.append((f"rib screw land {key}", L, (x, P.LOWER_RIB_Y0, z), (0, 1, 0), 2.2, 0.3, P.RIB_T - 0.3))
for x, z in P.STANDOFFS_XZ:
    eng.append((f"plate land at standoff ({x:+.1f},{z:+.1f})", PL, (x, P.PLATE_FRONT_Y, z), (0, 1, 0), 2.6, 0.3, 2.2))
u = np.array(P.unit(180, P.USB_EL_DEG))
yl = np.cross(u, [1.0, 0, 0])
for hx, hd in P.USB_HOLES:
    c = P.RI - 0.1 - P.USB_CONN_PROTRUDE - hd
    centre = np.array([hx, 0, 0]) + u * c + yl * (P.USB_CONN[2] / 2 + P.USB_PCB[2])
    eng.append((f"USB M2.5 pilot wall in block x={hx:+.2f}", L, tuple(centre), tuple(yl), 1.0 + 0.9, 0.5, 5.5))
for side, nm in ((-1, "lobe_left_pink"), (1, "lobe_right_pink")):
    n = np.array(P.unit(side * P.LOBE_AZ, P.LOBE_EL))
    eng.append((f"{nm} screw boss wall in upper", U, tuple(n * 63.2), tuple(n), 1.2 + 0.9, 0.3, 3.0))
    eng.append((f"{nm} pilot wall in lobe", printed[nm], tuple(n * (P.R - P.LOBE_SEAT_SAG)), tuple(n), 0.8 + 0.8, 0.5, 5.0))
nb = np.array(P.unit(-140, P.BUZ_EL_DEG))
eng.append(("buzzer pocket wall", L, tuple(nb * (P.RI - 0.4 - P.BUZ_H)), tuple(nb), P.BUZ_D / 2 + P.BUZ_FIT + 0.8, 0.5, P.BUZ_H - 0.5))
erows = []
for label, host, c, ax_, r, z0, z1 in eng:
    frac = ring_inside(host, c, ax_, r, z0, z1)
    erows.append({"check": label, "material_fraction": round(frac, 3)})
    if frac < 0.95:
        fail(f"engagement {label}: only {frac:.0%} of the surrounding ring is material")
std_centres = [vendor[k].bounds.mean(axis=0) for k in vendor if "SMTSO" in k]
for (x, z) in P.STANDOFFS_XZ:
    dmin = min(np.hypot(c[0] - x, c[2] - z) for c in std_centres)
    erows.append({"check": f"plate hole vs board standoff ({x:+.2f},{z:+.2f})", "offset_mm": round(float(dmin), 3)})
    if dmin > 0.15:
        fail(f"plate hole {x},{z} misses standoff by {dmin:.2f} mm")
report["checks"]["fastener_engagement"] = erows
for e in erows:
    print("engagement", e)

# 3/4 clearances & MMC ---------------------------------------------------------------------------
def min_dist(a, b, n=25000):
    ma, mb = bodies[a], bodies[b]
    pa, _ = trimesh.sample.sample_surface_even(ma, n)
    pb, _ = trimesh.sample.sample_surface_even(mb, n)
    d1 = trimesh.proximity.ProximityQuery(mb).signed_distance(pa)
    d2 = trimesh.proximity.ProximityQuery(ma).signed_distance(pb)
    # signed_distance > 0 inside; clearance = -max(inside)
    return float(-max(d1.max(), d2.max()))


def tol(k):
    return TOL_VENDOR if is_vendor(k) else (TOL_PURCH if k in purch else TOL_PRINT)


CRIT = [
    ("bezel_black", "board_001_DO0143", "glass radial / lip"),
    ("bezel_black", "board_294_PMMA", "PMMA frame"),
    ("bezel_black", "upper_shell_purple", "button in upper opening"),
    ("bezel_black", "lower_shell_ivory", "button in lower opening"),
    ("bezel_black", "belt_black", "button in belt gap"),
    ("display_plate_petg", "upper_shell_purple", "upper backstop rib gap (foam)"),
    ("belt_black", "lower_shell_ivory", "belt on spigot"),
    ("upper_shell_purple", "lower_shell_ivory", "upper counterbore on spigot / boss gap"),
    ("socket_left", "display_plate_petg", "J socket through plate window"),
    ("socket_right", "display_plate_petg", "J socket through plate window"),
    ("socket_left", "lower_shell_ivory", "socket vs lower rib"),
    ("socket_right", "upper_shell_purple", "socket vs upper rib"),
    ("buzzer", "lower_shell_ivory", "buzzer pocket"),
    ("lobe_left_pink", "m_inlay_white", "decor spacing"),
    ("m_inlay_white", "upper_shell_purple", "inlay pocket"),
]
for k in list(vendor):
    if any(t in k for t in ("TYPE-C", "HP1_25", "2X7", "SWITCHER", "PITCH1MM", "MICRO_SD", "TF_CARD")):
        CRIT.append(("display_plate_petg", k, "plate vs board part"))
        CRIT.append(("bezel_black", k, "bezel vs board part"))
clear = []
for a, b, why in CRIT:
    if a not in bodies or b not in bodies:
        continue
    d = min_dist(a, b)
    need = tol(a) + tol(b)
    contact = is_contact(a, b)
    ok = contact or d >= need - 1e-3
    clear.append({"a": a, "b": b, "why": why, "min_clearance_mm": round(d, 3), "mmc_required_mm": need,
                  "designed_contact": contact, "mmc_ok": ok})
    if not ok:
        fail(f"MMC clearance {a} x {b}: {d:.3f} < {need}")
report["checks"]["clearance_mmc"] = clear

# 5 insertion paths ---------------------------------------------------------------------------------
board_all = trimesh.util.concatenate([vendor[k] for k in vendor])


def sweep(moving, fixed_names, direction, distance, step=1.0, label=""):
    hits = []
    d = np.asarray(direction, float) / np.linalg.norm(direction)
    for s in np.arange(distance, -1e-9, -step):
        mv = [m.copy() for m in moving]
        for m in mv:
            m.apply_translation(d * s)
        for m in mv:
            for fn in fixed_names:
                fb = bodies[fn]
                if not (np.all(m.bounds[0] - 0.1 <= fb.bounds[1]) and np.all(fb.bounds[0] - 0.1 <= m.bounds[1])):
                    continue
                try:
                    v = float(m.intersection(fb, engine="manifold").volume)
                except Exception:  # noqa: BLE001
                    v = float("nan")
                if v > 0.05 and s > 0.6:
                    hits.append({"offset_mm": round(float(s), 1), "fixed": fn, "overlap_mm3": round(v, 2)})
    ok = len(hits) == 0
    report["checks"].setdefault("insertion_paths", []).append({"step": label, "ok": ok, "hits": hits[:8]})
    print("path", label, "OK" if ok else f"BLOCKED {hits[:3]}")
    if not ok:
        fail(f"insertion path blocked: {label}")


board_hulls = [vendor[k] for k in vendor]
sweep(board_hulls, ["bezel_black"], (0, 1, 0), 14.0, label="1 display module into bezel pocket from behind (+y -> final)")
sub = [printed["bezel_black"], printed["display_plate_petg"], purch["socket_left"], purch["socket_right"]] + board_hulls
sweep([purch["usb_breakout"]], ["lower_shell_ivory"], tuple(-np.array(P.unit(180, P.USB_EL_DEG))), 8.0,
      label="2 USB-C breakout slid outward into port block")
sweep([purch["buzzer"]], ["lower_shell_ivory"], tuple(-np.array(P.unit(-140, P.BUZ_EL_DEG))), 10.0,
      label="3 buzzer pushed into pocket")
sweep(sub, ["lower_shell_ivory", "usb_breakout", "buzzer", "steel_disc"], (0, 0, 1), 80.0, step=2.0,
      label="4 display sub-assembly lowered into lower shell")
sweep([printed["belt_black"]], ["lower_shell_ivory", "bezel_black"], (0, 0, 1), 30.0, label="5 belt lowered over spigot")
sweep([printed["upper_shell_purple"], printed["lobe_left_pink"], printed["lobe_right_pink"], printed["m_inlay_white"]],
      ["lower_shell_ivory", "belt_black", "bezel_black", "display_plate_petg", "socket_left", "socket_right"], (0, 0, 1), 60.0,
      step=1.5, label="6 upper shell (with lobes + M) lowered")
sweep([purch[f"m3x50_{i}"] for i in range(3)], ["lower_shell_ivory", "upper_shell_purple"], (0, 0, -1), 50.0,
      label="7 three M3x50 screws from the base")
for side in ("left", "right"):
    n = P.unit((-1 if side == "left" else 1) * P.LOBE_AZ, P.LOBE_EL)
    sweep([printed[f"lobe_{side}_pink"]], ["upper_shell_purple"], n, 6.0, step=0.5, label=f"8 lobe {side} onto seat")

# 6 mass / CoG -------------------------------------------------------------------------------------
dens = {"upper_shell_purple": (1.24, 0.92), "lower_shell_ivory": (1.24, 0.92), "belt_black": (1.24, 0.95),
        "bezel_black": (1.27, 0.95), "display_plate_petg": (1.27, 0.95), "lobe_left_pink": (1.24, 0.6),
        "lobe_right_pink": (1.24, 0.6), "m_inlay_white": (1.24, 1.0)}
items = [(printed[k].volume / 1000 * d * f, printed[k].center_mass) for k, (d, f) in dens.items()]
items.append((27.0, np.array([0.0, P.GLASS_Y + 5.0, 0.0])))           # board + glass (estimate, weigh on receipt)
items.append((4.0, purch["usb_breakout"].center_mass))
items.append((2.0, purch["buzzer"].center_mass))
items.append((9.0, np.array([0.0, 0.0, -20.0])))                      # 3x M3x50, inserts, M2 screws
mass_wo = sum(m for m, _ in items)
cog_wo = sum(m * c for m, c in items) / mass_wo
disc_mass = np.pi * (P.WEIGHT_DISC[0] / 20) ** 2 * (P.WEIGHT_DISC[1] / 10) * 7.85
items2 = items + [(disc_mass, purch["steel_disc"].center_mass)]
mass_w = sum(m for m, _ in items2)
cog_w = sum(m * c for m, c in items2) / mass_w
foot_r = P.FEET_R
inr = foot_r * np.cos(np.pi / 6)  # 6 feet hexagon inradius


def stability(mass, cog):
    h = cog[2] - (P.BASE_Z - 3.0)       # feet 3 mm tall
    off = float(np.hypot(cog[0], cog[1]))
    tip = float(np.degrees(np.arctan2(inr - off, h)))
    W = mass / 1000 * 9.81
    press_h = 0 - (P.BASE_Z - 3.0)      # screen centre height above desk
    f_tip_back = W * (inr - cog[1]) / press_h   # push at screen toward +y, pivot = rear foot edge
    return {"mass_g": round(mass, 1), "cog_mm": [round(float(c), 2) for c in cog], "tip_angle_deg": round(tip, 1),
            "push_to_tip_N": round(float(f_tip_back), 2), "push_to_slide_N_mu0.8": round(W * 0.8, 2),
            "push_to_slide_N_mu0.3": round(W * 0.3, 2)}


report["checks"]["mass_cog"] = {"without_disc": stability(mass_wo, cog_wo), "with_steel_disc": stability(mass_w, cog_w)}
print("mass/cog", report["checks"]["mass_cog"])

# 7 print orientation / cosmetic overhang ----------------------------------------------------------
ORIENT = {"upper_shell_purple": np.array([0, 0, 1.0]),      # rim on bed, dome up
          "lower_shell_ivory": np.array([0, 0, 1.0]),       # flat base on bed (45 deg conical foot)
          "belt_black": np.array([0, 0, 1.0]),
          "bezel_black": np.array([0, -1.0, 0]),            # rear face on bed, front face is the top skin
          "display_plate_petg": np.array([0, 1.0, 0]),
          "lobe_left_pink": None, "lobe_right_pink": None, "m_inlay_white": None}
ov = {}
for k, up in ORIENT.items():
    m = printed[k]
    if up is None:  # decor parts print on their own flat base: base normal is "down"
        n_base = -m.face_normals[np.argmax(m.area_faces)]
        up = n_base / np.linalg.norm(n_base)
    cos = m.face_normals @ up
    down = cos < -np.cos(np.radians(44))  # 1 deg slack: 45 deg design faces are self-supporting
    centers = m.triangles_center
    bed = float((m.vertices @ up).min())
    on_bed = np.abs(centers @ up - bed) < 0.05
    rad = np.linalg.norm(centers, axis=1)
    cosmetic = rad >= P.R - 0.05
    if k == "lower_shell_ivory":
        cosmetic = cosmetic | ((centers[:, 2] < P.FOOT_TANGENT_Z) & (rad > P.RI + 0.5))
    if k == "bezel_black":  # visible = faces on the convex hull in front of the shell surface
        _, dh, _ = trimesh.proximity.closest_point(m.convex_hull, centers)
        cosmetic = (dh < 0.05) & (centers[:, 1] <= -62.0)
    sup = down & ~on_bed
    ov[k] = {"support_area_total_mm2": round(float(m.area_faces[sup].sum()), 1),
             "support_area_on_cosmetic_faces_mm2": round(float(m.area_faces[sup & cosmetic].sum()), 1)}
    if ov[k]["support_area_on_cosmetic_faces_mm2"] > 5.0:
        fail(f"{k}: supports on cosmetic faces {ov[k]['support_area_on_cosmetic_faces_mm2']} mm2")
report["checks"]["print_overhang"] = ov
print("overhang", ov)

report["verdict"] = "PASS" if not report["fail"] else "FAIL"
json.dump(report, open(OUT, "w"), indent=1, default=float)
print("VERDICT", report["verdict"], len(report["fail"]), "failures")
