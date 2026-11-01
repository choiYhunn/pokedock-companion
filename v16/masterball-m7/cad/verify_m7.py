"""Independent mechanical verification of the M7 assembly (does not trust build_m7.py's own report).

usage: python verify_m7.py <cad_out_dir> <vendor_parts_dir> <report.json>
Loads the exported STLs (what the printer gets) and the official Waveshare 1.43 STEP parts
(per-component STLs, tools/vendor_step_to_parts.py) and checks:
  1 mesh validity                     2 closed-state interference (all pairs, manifold booleans)
  3 lid sweep 0..OPEN_DEG (1 deg)     4 mechanical stop engages just past OPEN_DEG
  5 mass / CoG / tipping (closed, open, finger push on the screen, lid pushed past the stop)
  6 screen: visible active area by ray casting, readability (angle subtended)
  7 printability: build volume per print orientation, unsupported overhang area
Status per item: PASS / FAIL. Things a computer cannot know (real board, real print) are not here.
"""
import glob
import itertools
import json
import math
import os
import sys

import manifold3d as mf
import numpy as np
import trimesh

sys.path.insert(0, os.path.dirname(__file__))
import m7_params as P  # noqa: E402

CAD, VEND, OUT = sys.argv[1:4]
rep = {"checks": {}, "fail": []}


def fail(msg):
    rep["fail"].append(msg)
    print("FAIL", msg)


def load(path):
    m = trimesh.load(path, force="mesh")
    m.merge_vertices()
    return m


printed = {os.path.basename(f)[:-4]: load(f) for f in sorted(glob.glob(f"{CAD}/stl/*.stl"))}
purch = {os.path.basename(f)[:-4]: load(f) for f in sorted(glob.glob(f"{CAD}/purchased/*.stl"))}
purch.pop("board_envelope", None)          # the real vendor parts are used instead


def step_to_ball(m):
    m = m.copy()
    v = m.vertices
    u = np.column_stack([-v[:, 1], 1.10 - v[:, 2], v[:, 0]])
    t = math.radians(P.POD_ROT_DEG)
    b = np.column_stack([u[:, 0] + P.POD_C[0], u[:, 1] * math.cos(t) - u[:, 2] * math.sin(t) + P.POD_C[1],
                         u[:, 1] * math.sin(t) + u[:, 2] * math.cos(t) + P.POD_C[2]])
    m.vertices = b
    return m


vendor = {}
rows = json.load(open(f"{VEND}/parts.json"))
for f in sorted(glob.glob(f"{VEND}/*.stl")):
    m = load(f)
    if len(m.vertices) < 4:
        continue
    h = m.convex_hull
    if not h.is_volume or h.volume < 0.01:
        continue
    idx = int(os.path.basename(f)[:3]) - 1
    path = rows[idx]["path"] if 0 <= idx < len(rows) else "?"
    if "TF_CARD" in path:
        continue          # no microSD card is fitted (assets live in flash)
    vendor[f"board_{idx + 1:03d}"] = step_to_ball(h)
board_all = trimesh.util.concatenate(list(vendor.values()))

LID_GROUP = ["lid_lavender", "lid_liner_lavender", "ear_left_pink", "ear_right_pink", "magnet_lid_0", "magnet_lid_1",
             "reed_actuator_57155"]
bodies = {**printed, **purch, **vendor}

# 1 validity -------------------------------------------------------------------------------------
val = {k: {"watertight": bool(m.is_watertight), "volume_mm3": round(float(m.volume), 1)} for k, m in printed.items()}
rep["checks"]["1_mesh_validity"] = val
for k, v in val.items():
    if not v["watertight"] or v["volume_mm3"] <= 0:
        fail(f"{k} mesh not watertight / no volume")
build = json.load(open(f"{CAD}/build_report.json"))
for k, v in build["parts"].items():
    if not v["valid"]:
        fail(f"{k}: STEP solid not valid")
rep["checks"]["1_step_valid"] = {k: v["valid"] for k, v in build["parts"].items()}

# 2 closed-state interference ----------------------------------------------------------------------
CONTACT = {frozenset(p) for p in [
    ("lid_lavender", "belt_black"), ("lid_lavender", "lid_liner_lavender"), ("lid_lavender", "ear_left_pink"),
    ("lid_lavender", "ear_right_pink"), ("belt_black", "lower_shell_ivory"), ("deck_lavender", "lower_shell_ivory"),
    ("display_cradle_plum", "deck_lavender"), ("display_cradle_plum", "display_bezel_plum"),
    ("button_ring_black", "lower_shell_ivory"), ("button_ring_black", "belt_black"), ("button_white", "lower_shell_ivory"),
    ("steel_weight", "lower_shell_ivory"), ("usb_panel_port_body", "lower_shell_ivory"),
    ("magnet_lid_0", "lid_lavender"), ("magnet_lid_1", "lid_lavender"), ("magnet_belt_0", "belt_black"),
    ("magnet_belt_1", "belt_black"), ("buzzer_wt1205", "lower_shell_ivory"), ("usb_right_angle_adapter", "usb_extension_plug"),
    ("stop_block_black", "belt_black"), ("reed_sensor_59155", "belt_black"), ("reed_actuator_57155", "lid_lavender")]}
PRESS = {frozenset(("dowel_pin_3x30", "belt_black"))}       # d3.0 pin in d2.9 holes: designed overlap


def is_contact(a, b):
    s = frozenset((a, b))
    if s in CONTACT:
        return True
    if a.startswith("board_") and b == "display_cradle_plum" or b.startswith("board_") and a == "display_cradle_plum":
        return True       # standoff ends seat on the plate
    if a.startswith("board_") and b.startswith("board_"):
        return True
    if {a, b} & {"usb_right_angle_adapter"} and (a.startswith("board_") or b.startswith("board_")):
        return True       # the plug sits in the board's receptacle
    return False


_MF = {}


def to_mf(m):
    key = id(m)
    if key not in _MF:
        _MF[key] = mf.Manifold(mf.Mesh(vert_properties=np.asarray(m.vertices, np.float32),
                                       tri_verts=np.asarray(m.faces, np.uint32)))
    return _MF[key]


def overlap(a, b, Ma=None):
    """Intersection volume of meshes a and b (a optionally moved by 4x4 Ma), manifold booleans."""
    ab = a.bounds if Ma is None else trimesh.transform_points(trimesh.bounds.corners(a.bounds), Ma)
    lo, hi = (ab[0], ab[1]) if Ma is None else (ab.min(0), ab.max(0))
    if not (np.all(lo <= b.bounds[1] + 0.05) and np.all(b.bounds[0] <= hi + 0.05)):
        return 0.0
    ma = to_mf(a)
    if Ma is not None:
        ma = ma.transform(np.asarray(Ma[:3, :4], np.float64))
    v = (ma ^ to_mf(b)).volume()
    return float(v)


inter = {}
names = sorted(bodies)
for a, b in itertools.combinations(names, 2):
    if a.startswith("board_") and b.startswith("board_"):
        continue
    v = overlap(bodies[a], bodies[b])
    if v == 0.0:
        continue
    inter[f"{a} x {b}"] = round(v, 3)
    s = frozenset((a, b))
    if s in PRESS:
        continue
    lim = 2.0 if is_contact(a, b) else 0.05
    if not (v <= lim):
        fail(f"closed: {a} x {b} overlap {v:.3f} mm3 (limit {lim})")
rep["checks"]["2_closed_interference_mm3"] = inter

# 3 + 4 lid sweep ----------------------------------------------------------------------------------
PIV = [0.0, P.PIVOT_Y, P.PIVOT_Z]


def rot(deg):
    return trimesh.transformations.rotation_matrix(math.radians(-deg), [1, 0, 0], PIV)


moving = {k: bodies[k] for k in LID_GROUP}
fixed = {k: v for k, v in bodies.items() if k not in LID_GROUP and k != "dowel_pin_3x30"}
fixed_board = {"board": board_all.convex_hull}
fixed_named = {k: v for k, v in fixed.items() if not k.startswith("board_")}
fixed_named.update(fixed_board)
sweep = {}
first_hit = None
angles = [a * 1.0 for a in range(0, int(P.OPEN_DEG) + 1)]
for deg in angles:
    M = rot(deg)
    hits = {}
    for mk, mm in moving.items():
        for fk, fm in fixed_named.items():
            if frozenset((mk, fk)) in CONTACT and deg == 0:
                continue
            v = overlap(mm, fm, M)
            lim = 2.0 if (deg == 0 and frozenset((mk, fk)) in CONTACT) else 0.05
            if v > lim:
                hits[f"{mk} x {fk}"] = round(v, 3)
    if hits:
        sweep[f"{deg:.0f}"] = hits
        if first_hit is None and deg <= P.OPEN_DEG - 0.5:
            first_hit = (deg, hits)
rep["checks"]["3_sweep_hits"] = sweep
rep["checks"]["3_sweep_angles"] = [angles[0], angles[-1], len(angles)]
if first_hit:
    fail(f"sweep: collision at {first_hit[0]} deg: {first_hit[1]}")

stop = {}
lid_m = bodies["lid_lavender"]
for deg in (P.OPEN_DEG - 1, P.OPEN_DEG, P.OPEN_DEG + 1, P.OPEN_DEG + 2):
    stop[f"{deg:.0f}"] = round(overlap(lid_m, bodies["stop_block_black"], rot(deg)) + overlap(lid_m, bodies["belt_black"], rot(deg)), 3)
rep["checks"]["4_stop_lid_vs_belt_mm3"] = stop
if not (stop[f"{P.OPEN_DEG - 1:.0f}"] < 0.05 and stop[f"{P.OPEN_DEG + 2:.0f}"] > 1.0):
    fail(f"stop: lid/belt overlap around {P.OPEN_DEG} deg = {stop}")

# 5 mass, CoG, tipping -----------------------------------------------------------------------------
RHO = {"pla": 1.24e-3, "petg": 1.27e-3}       # g/mm3
FILL = {"ear_left_pink": 0.55, "ear_right_pink": 0.55}   # solid-ish parts at 15 % infill + 4 walls
MAT = {}   # every printed part is PLA (E-Studio X1C/H2S student printing is PLA only)
mass = {}
for k, m in printed.items():
    mass[k] = (RHO[MAT.get(k, "pla")] * float(m.volume) * FILL.get(k, 1.0), m.center_mass)
STEEL = 7.85e-3
washer_hole = math.pi * 10.5 ** 2 * P.WEIGHT_H          # ISO 7093 M20: d1 = 21 mm
mass["steel_weight"] = (STEEL * (float(purch["steel_weight"].volume) - washer_hole), purch["steel_weight"].center_mass)
mass["dowel_pin_3x30"] = (STEEL * float(purch["dowel_pin_3x30"].volume), purch["dowel_pin_3x30"].center_mass)
for k in ("magnet_lid_0", "magnet_lid_1", "magnet_belt_0", "magnet_belt_1"):
    mass[k] = (7.5e-3 * float(purch[k].volume), purch[k].center_mass)
EST = {  # purchased parts without a datasheet mass: estimates, flagged as such in the report
    "board": (20.0, board_all.centroid), "buzzer_wt1205": (2.0, purch["buzzer_wt1205"].centroid),
    "buzzer_driver_board": (3.0, purch["buzzer_driver_board"].centroid),
    "usb_right_angle_adapter": (4.0, purch["usb_right_angle_adapter"].centroid),
    "usb_extension_cable_4218": (25.0, purch["usb_panel_port_body"].centroid * 0.6),
    "screws_feet_wire": (8.0, np.array([0.0, 0.0, -30.0])),
    "reed_sensor_59155": (1.5, purch["reed_sensor_59155"].centroid),
    "reed_actuator_57155": (1.5, purch["reed_actuator_57155"].centroid)}
mass.update(EST)


def cog(deg, lid_scale=1.0, base_scale=1.0):
    M = rot(deg)
    tot, mom = 0.0, np.zeros(3)
    for k, (m, c) in mass.items():
        c = np.asarray(c, float)
        if k in LID_GROUP:
            c = trimesh.transform_points([c], M)[0]
            m = m * lid_scale
        elif k not in EST:
            m = m * base_scale
        tot += m
        mom += m * c
    return tot, mom / tot


feet = np.array([[P.FEET_R * math.cos(math.radians(90 + k * 360 / P.FEET_N)),
                  P.FEET_R * math.sin(math.radians(90 + k * 360 / P.FEET_N))] for k in range(P.FEET_N)])


def edge_margins(p):
    """Signed distance of p to each edge of the convex foot polygon (positive inside)."""
    pts = feet
    out = []
    n = len(pts)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        e = b - a
        nrm = np.array([e[1], -e[0]]) / np.linalg.norm(e)
        if np.dot(nrm, -a) < 0:
            nrm = -nrm
        out.append((float(np.dot(p - a, nrm)), a, b, nrm))
    return out


def push_limit(deg, lid_scale=1.0, base_scale=1.0):
    """Largest finger force (N) on the glass centre along -normal before the ball tips."""
    W, g = cog(deg, lid_scale, base_scale)
    Wn = W * 9.81e-3
    pnt = np.array(P.POD_C)
    n = np.array([0.0, -math.sin(math.radians(P.SCREEN_TILT_DEG)), math.cos(math.radians(P.SCREEN_TILT_DEG))])
    f_dir = -n
    best = float("inf")
    if min(x[0] for x in edge_margins(g[:2])) <= 0:
        return 0.0
    for d, a, b, nrm in edge_margins(g[:2]):
        # moment about the edge line (at z = BASE_Z) of weight (restoring) and of the force (tipping)
        e = np.append(b - a, 0.0)
        e /= np.linalg.norm(e)
        a3 = np.array([a[0], a[1], P.BASE_Z])
        mw = np.dot(np.cross(g - a3, np.array([0, 0, -Wn])), e)
        mf = np.dot(np.cross(pnt - a3, f_dir), e)
        if mw * mf < 0:
            best = min(best, abs(mw) / abs(mf))
    return best


stab = {}
for deg in (0.0, 60.0, 90.0, P.OPEN_DEG):
    W, g = cog(deg)
    m = min(x[0] for x in edge_margins(g[:2]))
    stab[f"{deg:.0f}"] = {"mass_g": round(W, 1), "cog": [round(float(v), 1) for v in g], "margin_to_foot_edge_mm": round(m, 1)}
Wworst, gworst = cog(P.OPEN_DEG, 1.10, 0.90)
mw = min(x[0] for x in edge_margins(gworst[:2]))
stab["open_worst_lid+10%_base-10%"] = {"cog": [round(float(v), 1) for v in gworst], "margin_mm": round(mw, 1)}
fpush = push_limit(P.OPEN_DEG)
fpush_w = push_limit(P.OPEN_DEG, 1.10, 0.90)
stab["finger_push_limit_N"] = {"nominal": round(fpush, 2), "worst": round(fpush_w, 2), "required": 1.5}
W, g = cog(P.OPEN_DEG)
fh = 1.5 * math.cos(math.radians(90 - P.SCREEN_TILT_DEG))
fv = 1.5 * math.sin(math.radians(90 - P.SCREEN_TILT_DEG))
stab["slide_at_1.5N_needed_mu"] = round(fh / (W * 9.81e-3 + fv), 3)
# lid over-centre angle: lid CoG passes over the pivot
lid_mass = sum(mass[k][0] for k in LID_GROUP)
lid_c = sum(mass[k][0] * np.asarray(mass[k][1]) for k in LID_GROUP) / lid_mass
oc = None
for d10 in range(0, 1101):
    c = trimesh.transform_points([lid_c], rot(d10 / 10))[0]
    if c[1] >= P.PIVOT_Y:
        oc = d10 / 10
        break
stab["lid_mass_g"] = round(lid_mass, 1)
stab["lid_over_centre_deg"] = oc
c110 = trimesh.transform_points([lid_c], rot(P.OPEN_DEG))[0]
stab["lid_hold_open_torque_Nmm"] = round(lid_mass * 9.81e-3 * (c110[1] - P.PIVOT_Y), 1)
stab["stop_force_N_from_lid_weight"] = round(stab["lid_hold_open_torque_Nmm"] / ((P.STOP_LUG_R[0] + P.STOP_LUG_R[1]) / 2), 2)
stab["estimated_masses_g"] = {k: v[0] for k, v in EST.items()}
rep["checks"]["5_stability"] = stab
if stab[f"{P.OPEN_DEG:.0f}"]["margin_to_foot_edge_mm"] < 5.0:
    fail(f"open {P.OPEN_DEG} deg: CoG only {stab[f'{P.OPEN_DEG:.0f}']['margin_to_foot_edge_mm']} mm inside the feet")
if mw < 2.0:
    fail(f"open worst case CoG margin {mw:.1f} mm")
if fpush_w < 1.5:
    fail(f"finger push on the open screen tips the ball at {fpush_w:.2f} N (< 1.5 N)")
if oc is None or oc > P.OPEN_DEG - 10:
    fail(f"lid does not stay open by gravity (over-centre {oc})")

# 6 screen visibility and readability ------------------------------------------------------------
occluders = [printed[k] for k in printed if k not in ("display_bezel_plum",)]
bez = printed["display_bezel_plum"]
n = np.array([0.0, -math.sin(math.radians(P.SCREEN_TILT_DEG)), math.cos(math.radians(P.SCREEN_TILT_DEG))])
uvec = np.array([0.0, math.cos(math.radians(P.SCREEN_TILT_DEG)), math.sin(math.radians(P.SCREEN_TILT_DEG))])
xvec = np.array([1.0, 0.0, 0.0])
ctr = np.array(P.POD_C) + n * 0.05
rr = np.sqrt(np.linspace(0.02, 1, 14)) * P.ACTIVE_R
th = np.linspace(0, 2 * math.pi, 36, endpoint=False)
pts = np.array([ctr + r * (math.cos(t) * xvec + math.sin(t) * uvec) for r in rr for t in th])
scene_open = []
M = rot(P.OPEN_DEG)
for k, m in printed.items():
    mm = m.copy()
    if k in LID_GROUP:
        mm.apply_transform(M)
    scene_open.append(mm)
occ = trimesh.util.concatenate(scene_open)
ray = trimesh.ray.ray_triangle.RayMeshIntersector(occ)
vis = {}
for el in (15, 25, 35, 45, 60):
    for az in (-30, 0, 30):
        d = np.array([math.sin(math.radians(az)) * math.cos(math.radians(el)), -math.cos(math.radians(az)) * math.cos(math.radians(el)),
                      math.sin(math.radians(el))])
        if np.dot(d, n) <= 0:
            vis[f"el{el}_az{az}"] = 0.0
            continue
        hit = ray.intersects_any(pts + d * 0.02, np.tile(d, (len(pts), 1)))
        vis[f"el{el}_az{az}"] = round(1.0 - float(hit.mean()), 3)
rep["checks"]["6_visible_active_area_fraction"] = vis
for key in ("el25_az0", "el35_az0", "el45_az0", "el35_az-30", "el35_az30"):
    if vis[key] < 0.98:
        fail(f"screen: only {vis[key]:.0%} of the active area visible from {key}")
px = 466 / 36.75               # px per mm
read = {}
for name, hpx in (("clock digits (pd_digits_120, cap ~84 px)", 84), ("timer digits (pd_ui_48)", 34),
                  ("partner sprite (Gengar home 222 x 189 px)", 189), ("small label (pd_ui_40)", 28)):
    hmm = hpx / px
    read[name] = {"height_mm": round(hmm, 2), "arcmin_at_450mm": round(math.degrees(math.atan(hmm / 450)) * 60, 1)}
rep["checks"]["6_readability"] = read
rep["checks"]["6_active_area"] = {"diameter_mm": 36.75, "note": "drawn at true size; ISO 9241-303 asks >= 16 arcmin for text"}

# 6b seated-eye line of sight (perspective rays, bezel included) and closed-lid clearance ---------
import view_check as VC  # noqa: E402

occ_open = []
for k, m in printed.items():
    mm = m.copy()
    if k in LID_GROUP:
        mm.apply_transform(rot(P.OPEN_DEG))
    occ_open.append(mm)
occ_open = trimesh.util.concatenate(occ_open)
eyes = VC.view_report(occ_open)
rep["checks"]["6b_seated_eye_visible_fraction"] = eyes
low = VC.lowest_full_view_height(occ_open)
rep["checks"]["6b_lowest_full_view_eye_height_mm_at_550"] = low
for key, v in eyes.items():
    if v < 0.995:
        fail(f"seated eye {key}: only {v:.1%} of the active area visible")
if low is None or low > 300:
    fail(f"full screen only visible from eye height {low} mm above the desk (a seated eye is ~350-500)")
lid_closed = [printed[k] for k in ("lid_lavender", "lid_liner_lavender")]
pod = [printed["display_bezel_plum"], printed["display_cradle_plum"], board_all.convex_hull]
lidc = trimesh.util.concatenate(lid_closed)
gap_closed = VC.min_clearance(pod, lidc)
rep["checks"]["6b_closed_min_gap_pod_to_lid_mm"] = round(gap_closed, 2)
if gap_closed < 2.0:
    fail(f"closed lid: pod only {gap_closed:.2f} mm from the lid/liner (< 2.0)")

# 8 lid sensor geometry ------------------------------------------------------------------------------
sen, act = purch["reed_sensor_59155"], purch["reed_actuator_57155"]
gap0 = float(act.bounds[0][2] - sen.bounds[1][2])
rel = None
for d10 in range(0, 300):
    a2 = act.copy()
    a2.apply_transform(rot(d10 / 10))
    if float(np.linalg.norm(a2.centroid - act.centroid)) >= 4.7:      # 59155-S release ~4.2-4.7 mm (distributor data)
        rel = d10 / 10
        break
mags = [purch[k].centroid for k in ("magnet_lid_0", "magnet_lid_1", "magnet_belt_0", "magnet_belt_1")]
stray = min(float(np.linalg.norm(sen.centroid - mcen)) for mcen in mags)
rep["checks"]["8_lid_sensor"] = {"closed_gap_mm": round(gap0, 2), "operate_mm_datasheet_approx": 4.0,
                                 "opens_at_lid_deg": rel, "nearest_latch_magnet_mm": round(stray, 1)}
if not (0 <= gap0 <= 2.0):
    fail(f"reed/actuator gap {gap0:.2f} mm (want 0..2 for a ~4 mm operate distance)")
if rel is None or rel > 8:
    fail(f"sensor releases only at {rel} deg")
if stray < 30:
    fail(f"latch magnet {stray:.1f} mm from the reed (stray actuation)")

# 7 printability ----------------------------------------------------------------------------------
import print_orient as PO  # noqa: E402

COSMETIC_OK = {"lid_lavender": "inside dome above the liner (z > 46) and the knuckle underside only",
               "display_cradle_plum": "plate back face 40 deg from vertical (no support)",
               "belt_black": "3.5 mm ledge ring under the band (sits on the lower shell, hidden)"}


def orient(k, m):
    return PO.orient(k, m)


pr = {}
for k, m in printed.items():
    mo = orient(k, m)
    ext = mo.bounds[1] - mo.bounds[0]
    zmin = mo.bounds[0][2]
    fn = mo.face_normals
    cz = mo.triangles_center[:, 2]
    over = (fn[:, 2] < -math.cos(math.radians(45))) & (cz > zmin + 0.4)
    area = float(mo.area_faces[over].sum())
    pr[k] = {"extent_mm": [round(float(v), 1) for v in ext], "fits_180_cube": bool(np.all(ext <= 178)),
             "overhang_gt45_area_mm2": round(area, 0)}
    if k == "lid_lavender":
        # where the lid needs support: hidden above the liner, or elsewhere (visible when open)?
        zc = m.triangles_center[:, 2]          # lid is printed as modelled (rim on the bed)
        hidden = over & (zc > P.LINER_Z[1] - 0.1)
        for pk in ("magnet_lid_0", "magnet_lid_1", "reed_actuator_57155"):   # pocket ceilings, covered by the glued part
            lo, hi = purch[pk].bounds
            inside = np.all((m.triangles_center > lo - 0.6) & (m.triangles_center < hi + 0.6), axis=1)
            hidden = hidden | (over & inside)
        knuckle = over & (m.triangles_center[:, 1] > 60) & (zc < 16)
        pr[k]["overhang_hidden_above_liner_mm2"] = round(float(m.area_faces[hidden].sum()), 0)
        pr[k]["overhang_at_hinge_mm2"] = round(float(m.area_faces[knuckle & ~hidden].sum()), 0)
        vis_area = float(m.area_faces[over & ~hidden & ~knuckle].sum())
        pr[k]["overhang_visible_when_open_mm2"] = round(vis_area, 0)
        if vis_area > 150:
            fail(f"lid: {vis_area:.0f} mm2 of support-needing surface visible when open")
    if not np.all(ext <= 178):
        fail(f"{k}: {ext.round(1)} does not fit a 180 mm printer (A1 mini)")
rep["checks"]["7_print"] = pr
rep["checks"]["7_print_notes"] = COSMETIC_OK

rep["result"] = "PASS" if not rep["fail"] else "FAIL"
json.dump(rep, open(OUT, "w"), indent=1, default=float)
print(json.dumps({k: rep["checks"][k] for k in ("4_stop_lid_vs_belt_mm3", "5_stability", "6_visible_active_area_fraction")}, indent=1, default=float))
print("RESULT", rep["result"], len(rep["fail"]), "fail(s)")
sys.exit(1 if rep["fail"] else 0)
