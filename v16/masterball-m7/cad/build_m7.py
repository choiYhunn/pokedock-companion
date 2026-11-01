"""Generate PokéDock M7 (openable Master Ball) printable parts, fit-kit coupons and assemblies.

usage: python build_m7.py <out_dir>
Writes <out_dir>/step/*.step, <out_dir>/stl/*.stl (printed parts, print-ready),
<out_dir>/fitkit/*.step|stl (coupons cut from the SAME solids), <out_dir>/purchased/*.stl
(envelopes of bought parts, checks only, never printed), <out_dir>/m7_assembly_closed.step and
m7_assembly_open110.step (printed parts + simplified envelopes; the Waveshare STEP is not embedded).
All geometry is written here from scratch; no third-party CAD is used.
"""
import json
import math
import os
import sys

from build123d import (Box, Compound, Cone, Cylinder, Location, Plane, Polyline, Pos, Rot, Sphere,
                       Vector, export_step, export_stl, extrude, make_face, revolve, scale, Axis)

sys.path.insert(0, os.path.dirname(__file__))
import m7_params as P  # noqa: E402

OUT = sys.argv[1]
BIG = 300.0
for d in ("step", "stl", "fitkit", "purchased"):
    os.makedirs(os.path.join(OUT, d), exist_ok=True)


def V(*a):
    return Vector(*a)


def box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def zslab(z0, z1):
    return box(-BIG, BIG, -BIG, BIG, z0, z1)


def cyl_between(r, p0, p1):
    p0, p1 = V(*p0), V(*p1)
    d = p1 - p0
    return Plane(origin=(p0 + p1) * 0.5, z_dir=d.normalized()).location * Cylinder(r, d.length)


def cyl_x(r, x0, x1, y, z):
    return cyl_between(r, (x0, y, z), (x1, y, z))


def cyl_z(r, z0, z1, x=0.0, y=0.0):
    return cyl_between(r, (x, y, z0), (x, y, z1))


def yz_prism(pts, x0, x1):
    """Polygon given in (y, z) extruded along x from x0 to x1."""
    pl = Plane(origin=(x0, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
    face = make_face(Polyline(*[(a, b) for a, b in pts], close=True))
    return pl.location * extrude(face, x1 - x0)


def sector_x(cy, cz, r0, r1, a0, a1, x0, x1, n=24):
    """Annular sector around an x-parallel axis; angles in degrees from +y toward +z."""
    outer = [(cy + r1 * math.cos(math.radians(a)), cz + r1 * math.sin(math.radians(a)))
             for a in [a0 + (a1 - a0) * i / n for i in range(n + 1)]]
    inner = [(cy + r0 * math.cos(math.radians(a)), cz + r0 * math.sin(math.radians(a)))
             for a in [a1 - (a1 - a0) * i / n for i in range(n + 1)]]
    return yz_prism(outer + inner, x0, x1)


def teardrop_x(d, x0, x1, y, z):
    """Horizontal hole along x printable without support (45 deg roof toward +z)."""
    r = d / 2
    tip = r * math.sqrt(2)
    roof = yz_prism([(y - r * math.cos(math.radians(45)), z + r * math.sin(math.radians(45))),
                     (y, z + tip), (y + r * math.cos(math.radians(45)), z + r * math.sin(math.radians(45))),
                     (y, z)], x0, x1)
    return cyl_x(r, x0, x1, y, z) + roof


def along(d, r, s0, s1):
    """Cylinder of radius r along unit direction d from distance s0 to s1 from the ball centre."""
    return cyl_between(r, tuple(c * s0 for c in d), tuple(c * s1 for c in d))


def polar_xy(r, ang):
    a = math.radians(ang)
    return r * math.cos(a), r * math.sin(a)


POD = Pos(*P.POD_C) * Rot(X=P.POD_ROT_DEG)        # U frame -> ball frame


def cyl_u(r, y0, y1, x=0.0, z=0.0):
    """Cylinder along the U-frame screen axis (y_u)."""
    return cyl_between(r, (x, y0, z), (x, y1, z))


def lid_open(shape, deg):
    return Pos(0, P.PIVOT_Y, P.PIVOT_Z) * Rot(X=-deg) * Pos(0, -P.PIVOT_Y, -P.PIVOT_Z) * shape


report = {"parts": {}}


# ------------------------------------------------------------------------------------------------
def build_lid():
    outer = Sphere(P.R) & zslab(P.BH, P.R + 1)
    cavity = Sphere(P.RI_LID) & zslab(P.BH - 1, P.R)
    lid = outer - cavity
    # centre knuckle + web into the wall (the web is in front of and below the pivot: it only rises)
    h = P.LID_KNUCKLE_HALF
    lid = lid + (box(-h, h, 63.5, P.PIVOT_Y, P.BH, P.PIVOT_Z + P.KNUCKLE_R) & Sphere(P.R + 2)) \
        + cyl_x(P.KNUCKLE_R, -h, h, P.PIVOT_Y, P.PIVOT_Z)
    # stop lug: leading face at STOP_LUG_ANG0, meets the belt heel face at OPEN_DEG
    lid = lid + sector_x(P.PIVOT_Y, P.PIVOT_Z, P.STOP_LUG_R[0], P.STOP_LUG_R[1],
                         P.STOP_LUG_ANG0, P.STOP_LUG_ANG0 + P.STOP_LUG_SPAN, -P.STOP_HALF_X, P.STOP_HALF_X)
    lid = lid - teardrop_x(P.PIN_RUN_D, -h - 1, h + 1, P.PIVOT_Y, P.PIVOT_Z)
    # notches for the two belt knuckles (and their necks below the pivot)
    for s in (-1, 1):
        x0, x1 = sorted((s * (h + 0.0), s * (P.BELT_KNUCKLE_X[1] + 0.4)))
        lid = lid - cyl_x(P.LID_NOTCH_R, x0, x1, P.PIVOT_Y, P.PIVOT_Z)
        lid = lid - box(x0, x1, P.PIVOT_Y - 2.6, P.PIVOT_Y + 10, P.BH - 1, P.PIVOT_Z)
    # magnet bosses + pockets (faces flush with the rim)
    for az in P.MAG_AZ:
        x, y, _ = P.unit(az, 0)
        cx, cy = x * P.MAG_R, y * P.MAG_R
        lid = lid + (cyl_z(P.MAG_BOSS_D / 2, P.BH, P.BH + 6.0, cx, cy) & Sphere(P.R - 0.5))
        lid = lid - cyl_z(P.MAG_POCKET_D / 2, P.BH - 1, P.BH + P.MAG_POCKET_H, cx, cy)
    # lid-sensor actuator (Littelfuse 57155) right above the reed sensor, flush with the rim face
    sx, sy, _ = P.unit(P.SENSOR_AZ, 0)
    pl = Plane(origin=(0, 0, 0), x_dir=(sy, -sx, 0), z_dir=(0, 0, 1))
    t, rr, hh = P.ACTUATOR_BOX
    lid = lid + ((pl.location * box(-9, 9, P.SENSOR_R - rr / 2 - 1.6, P.R, P.BH, P.BH + hh + 1.6)) & Sphere(P.R - 0.5))
    lid = lid - (pl.location * box(-t / 2 - P.SENSOR_FIT, t / 2 + P.SENSOR_FIT, P.SENSOR_R - rr / 2 - P.SENSOR_FIT,
                                   P.SENSOR_R + rr / 2 + P.SENSOR_FIT, P.BH - 1, P.BH + hh + 0.2))
    # ear seats: flat spot-face + inner boss + screw from inside + orientation bump
    for s in (-1, 1):
        d, side, base_c, loc = ear_frame(s)
        seat = P.R - P.EAR_SEAT_DEPTH
        if P.EAR_VARIANT == "B":   # below the liner: a 1.8 mm inner pad following the dome (no support needed)
            pad = (Sphere(P.RI_LID + 0.2) - Sphere(P.RI_LID - 1.8)) & (Plane(origin=(0, 0, 0), z_dir=V(*d)).location * Cone(0.01, 15.5, P.R, align=None)) & zslab(P.BH + 1.0, P.R)
            lid = lid + pad
        else:
            lid = lid + (along(d, P.EAR_BASE_D / 2, 63.8, P.RI_LID + 0.5))      # boss under the whole seat, above the liner
        r0 = P.EAR_BASE_D / 2
        lid = lid - loc * ellipse_cyl(r0 + P.EAR_SEAT_CLEAR, r0 * P.EAR_FLAT + P.EAR_SEAT_CLEAR, 0, 10)
        lid = lid - along(d, P.M2_CLEAR / 2 + 0.05, 55, seat + 0.1)
        bump = ear_bump_centre(d, seat)
        lid = lid + cyl_between(1.5, bump, tuple(b + c * 1.6 for b, c in zip(bump, d)))
    # liner bosses (2 x M2 PT, visible screws as in the reference photo)
    for s in (-1, 1):
        x = s * P.LINER_SCREW_X
        top = math.sqrt(P.RI_LID ** 2 - x ** 2) + 1.0
        lid = lid + (cyl_z(3.5, P.LINER_Z[1], top, x, 0) & Sphere(P.R - 0.8))
        lid = lid - cyl_z(P.M2_PT_PILOT / 2, P.LINER_Z[1] - 1, P.LINER_Z[1] + 9, x, 0)
    return lid


def ear_axis(d, s):
    side = V(-d[1], d[0], 0).normalized() * (-1 if s < 0 else 1)   # horizontal tangent, outward
    if side.dot(V(s, 0, 0)) < 0:
        side = side * -1
    a = V(*d) + side * math.tan(math.radians(P.EAR_TILT_OUT))
    return a.normalized()


def ear_bump_centre(d, seat):
    side = V(-d[1], d[0], 0).normalized()
    p = V(*d) * seat + side * 8.0
    return (p.X, p.Y, p.Z)


from ear_shape import EAR_SHAPE, ear_profile  # noqa: E402,F401  (shared with appearance_gate.py)


def ear_frame(s):
    d = P.unit(s * P.EAR_AZ, P.EAR_EL)
    side = V(-d[1], d[0], 0).normalized()
    if side.dot(V(s, 0, 0)) < 0:
        side = side * -1                            # local x = outward horizontal tangent
    base_c = V(*d) * (P.R - P.EAR_SEAT_DEPTH)
    return d, side, base_c, Plane(origin=base_c, x_dir=side, z_dir=V(*d)).location


def ellipse_cyl(rx, ry, z0, z1):
    return scale(Pos(0, 0, (z0 + z1) / 2) * Cylinder(rx, z1 - z0), by=(1, ry / rx, 1))


def build_ear(s):
    d, side, base_c, loc = ear_frame(s)
    seat = P.R - P.EAR_SEAT_DEPTH
    r0 = P.EAR_BASE_D / 2
    face = make_face(Polyline(*ear_profile(), close=True))
    body = Rot(X=90) * revolve(face, Axis.Y, 360)           # local z = ear axis
    body = scale(body, by=(1, P.EAR_FLAT, 1))                 # flattened along the meridian
    body = Rot(Y=P.EAR_TILT_OUT) * body                       # lean outward
    ear = body & (Pos(0, 0, 50) * Box(100, 100, 100))
    ear = loc * (ear & ellipse_cyl(r0, r0 * P.EAR_FLAT, -1, 60))
    ear = ear - cyl_between(P.M2_PT_PILOT / 2, tuple(base_c - V(*d) * 1), tuple(base_c + V(*d) * 9))
    bump = ear_bump_centre(d, seat)
    ear = ear - cyl_between(1.75, tuple(V(*bump) - V(*d) * 0.5), tuple(V(*bump) + V(*d) * 2.0))
    return ear


def build_liner():
    z0, z1 = P.LINER_Z
    r = math.sqrt(P.RI_LID ** 2 - z1 ** 2) - 0.6
    liner = cyl_z(r, z0, z1)
    for s in (-1, 1):
        x = s * P.LINER_SCREW_X
        liner = liner - cyl_z(P.M2_CLEAR / 2, z0 - 1, z1 + 1, x, 0)
        liner = liner - (Pos(x, 0, z0 - 0.01) * Cone(2.2, 1.15, 1.05, align=None))
    # moon + three stars engraved in the visible face (generic motif, matches the night UI)
    e = P.LINER_ENGRAVE
    moon = cyl_z(9.0, z0 - 0.01, z0 + e, -10.0, 6.0) - cyl_z(8.0, z0 - 1, z0 + 1, -6.2, 8.4)
    liner = liner - moon
    for cx, cy, rs in ((13.0, 12.0, 4.6), (16.0, -6.0, 3.2), (-2.0, -16.0, 2.6)):
        pts = []
        for k in range(10):
            rr = rs if k % 2 == 0 else rs * 0.45
            a = math.radians(90 + 36 * k)
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        star = Pos(0, 0, z0 - 0.01) * extrude(make_face(Polyline(*pts, close=True)), e + 0.01)
        liner = liner - star
    return liner


def build_belt():
    band = (Sphere(P.R) & zslab(-P.BH, P.BH)) - cyl_z(P.BELT_BORE_R, -10, 10)
    spigot = cyl_z(P.SPIGOT_R_OUT, P.SPIGOT_Z0, -P.BH + 0.01) - cyl_z(P.SPIGOT_R_IN, P.SPIGOT_Z0 - 1, 0)
    belt = band + spigot
    for az in P.MAG_AZ:
        x, y, _ = P.unit(az, 0)
        cx, cy = x * P.MAG_R, y * P.MAG_R
        belt = belt + (cyl_z(P.MAG_BOSS_D / 2, -P.BH, P.BH, cx, cy) & Sphere(P.R - 0.5))
        belt = belt - cyl_z(P.MAG_POCKET_D / 2, P.BH - P.MAG_POCKET_H, P.BH + 1, cx, cy)
    # hinge base: two knuckles with necks, centre block with the stop heel
    k0, k1 = P.BELT_KNUCKLE_X
    for s in (-1, 1):
        x0, x1 = sorted((s * k0, s * k1))
        belt = belt + cyl_x(P.KNUCKLE_R, x0, x1, P.PIVOT_Y, P.PIVOT_Z)
        belt = belt + box(x0, x1, P.PIVOT_Y - 2.0, P.PIVOT_Y + P.KNUCKLE_R, P.BH - 0.01, P.PIVOT_Z)
        belt = belt + box(x0, x1, 62.5, P.PIVOT_Y + P.KNUCKLE_R, -P.BH, P.BH)
    hx = P.STOP_HALF_X
    belt = belt + box(-hx, hx, 62.5, P.STOP_BLOCK_Y[1], P.STOP_SHELF_Z[0], P.STOP_SHELF_Z[1])   # shelf for the stop block
    belt = belt + box(-hx, hx, 62.5, P.STOP_BLOCK_Y[0], P.STOP_SHELF_Z[0], P.BH - 1.1)
    for s in (-1, 1):
        belt = belt - cyl_z(1.15, P.STOP_SHELF_Z[0] - 1, P.STOP_SHELF_Z[1] + 0.01, s * P.STOP_SCREW_X, P.STOP_SCREW_Y)
    belt = belt - cyl_x(P.PIN_PRESS_D / 2, -k1 - 1, k1 + 1, P.PIVOT_Y, P.PIVOT_Z)
    # lid sensor: boss inside the bore, pocket open toward the inside (sensor slides in radially)
    sx, sy, _ = P.unit(P.SENSOR_AZ, 0)
    pl = Plane(origin=(0, 0, 0), x_dir=(sy, -sx, 0), z_dir=(0, 0, 1))      # local x = tangent, y = radial
    t, rr, hh = P.SENSOR_BOX
    belt = belt + ((pl.location * box(-9, 9, P.SENSOR_R - 6.0, P.R, -P.BH, P.BH)) & Sphere(P.R - 0.5))
    ztop = P.BH - P.SENSOR_SKIN
    belt = belt - (pl.location * box(-t / 2 - P.SENSOR_FIT, t / 2 + P.SENSOR_FIT, P.SENSOR_R - rr / 2 - 8,
                                     P.SENSOR_R + rr / 2 + P.SENSOR_FIT, ztop - hh - 0.3, ztop))
    # 1.2 mm step on the top face for the lavender rim ring
    belt = belt - (cyl_z(P.RIM_RING_R[1] + 0.2, P.BH - P.RIM_RING_T, P.BH + 0.5) - cyl_z(P.RIM_RING_R[0] - 3, P.BH - 5, P.BH + 1))
    return belt


def build_rim_ring():
    """Lavender rim ring glued in the belt-top step: the open ball shows a light rim like the photo."""
    ring = cyl_z(P.RIM_RING_R[1], P.BH - P.RIM_RING_T, P.BH) - cyl_z(P.RIM_RING_R[0], P.BH - 5, P.BH + 1)
    for az in P.MAG_AZ:                         # latch magnets pass through (glued flush with the ring top)
        x, y, _ = P.unit(az, 0)
        ring = ring - cyl_z(P.MAG_POCKET_D / 2, P.BH - 5, P.BH + 1, x * P.MAG_R, y * P.MAG_R)
    return ring


def build_stop_block():
    """Separate, replaceable lid stop (black PLA): heel face at STOP_FACE_DEG meets the lid lug at OPEN_DEG."""
    hx = P.STOP_HALF_X
    blk = box(-hx, hx, P.STOP_BLOCK_Y[0], P.STOP_BLOCK_Y[1], P.STOP_SHELF_Z[1], P.BH - 1.1) - Sphere(P.R + 0.1)
    blk = blk + sector_x(P.PIVOT_Y, P.PIVOT_Z, P.STOP_HEEL_R[0], P.STOP_HEEL_R[1],
                         P.STOP_FACE_DEG - 40.0, P.STOP_FACE_DEG, -hx, hx)
    blk = blk & zslab(P.STOP_SHELF_Z[1], 50)
    blk = blk - cyl_x(P.KNUCKLE_R + 0.35, -hx - 1, hx + 1, P.PIVOT_Y, P.PIVOT_Z)
    for s in (-1, 1):
        blk = blk - cyl_z(P.M2_PT_PILOT / 2, P.STOP_SHELF_Z[1] - 0.01, P.STOP_SHELF_Z[1] + 6.0, s * P.STOP_SCREW_X, P.STOP_SCREW_Y)
    return blk


def build_lower():
    foot = Pos(0, 0, (P.BASE_Z + P.FOOT_TANGENT_Z) / 2) * Cone(P.FOOT_R_AT_BASE, -P.FOOT_TANGENT_Z, P.FOOT_TANGENT_Z - P.BASE_Z)
    outer = (Sphere(P.R) + foot) & zslab(P.BASE_Z, -P.BH)
    cavity = Sphere(P.RI_LOW) & zslab(P.BASE_Z + P.FLOOR_T, -P.BH + 1)
    low = outer - cavity
    # deck pillars (M3 PT from the deck)
    for ang in P.DECK_SCREW_ANG:
        x, y = polar_xy(P.DECK_SCREW_R, ang)
        zb = -math.sqrt(P.RI_LOW ** 2 - P.DECK_SCREW_R ** 2) - 3
        low = low + (cyl_z(4.5, zb, P.DECK_TOP_Z - P.DECK_T, x, y) & Sphere(P.R - 0.5))
        low = low - cyl_z(P.M3_PT_PILOT / 2, P.DECK_TOP_Z - P.DECK_T - 14, P.DECK_TOP_Z, x, y)
    # steel weight pocket (glued)
    fz = P.BASE_Z + P.FLOOR_T
    low = low + (cyl_z(P.WEIGHT_D / 2 + 0.3 + 1.6, fz - 0.5, fz + P.WEIGHT_H) - cyl_z(P.WEIGHT_D / 2 + 0.3, fz - 0.01, fz + P.WEIGHT_H + 1))
    # buzzer pocket + 7 sound holes through the wall
    d = P.unit(P.BUZ_AZ, P.BUZ_EL)
    br = P.BUZ_D / 2 + P.BUZ_FIT / 2
    low = low + (along(d, br + 2.0, P.RI_LOW - P.BUZ_H - 1.2, P.R - 0.5) & Sphere(P.R - 0.3))
    low = low - along(d, br, P.RI_LOW - P.BUZ_H - 3, P.RI_LOW + 0.2)
    side = V(-d[1], d[0], 0).normalized()
    up = V(*d).cross(side).normalized()
    for k in range(7):
        off = V(0, 0, 0) if k == 0 else (side * math.cos(k * math.pi / 3) + up * math.sin(k * math.pi / 3)) * 3.2
        p0, p1 = V(*d) * (P.RI_LOW - 1) + off, V(*d) * (P.R + 2) + off
        low = low - cyl_between(0.8, tuple(p0), tuple(p1))
    # rear USB-C panel port: flat spot-face outside, flat boss inside, hole
    pd = P.unit(180, P.PORT_EL)
    low = low + (along(pd, P.PORT_FLAT_D / 2 + 1.5, P.R - 3.6, P.R - 1.0) & Sphere(P.R - 0.2))
    low = low - along(pd, P.PORT_FLAT_D / 2 + 1.5, P.R - 14, P.R - 3.6)   # flat inside face for the nut
    low = low - along(pd, P.PORT_FLAT_D / 2, P.R - 1.0, P.R + 5)
    low = low - along(pd, P.PORT_HOLE_D / 2, P.R - 10, P.R + 5)
    # feet recesses (d10.4 x 0.6), one exactly at the back
    for k in range(P.FEET_N):
        x, y = polar_xy(P.FEET_R, 90 + k * 360 / P.FEET_N)
        low = low - cyl_z(P.FEET_D / 2 + 0.2, P.BASE_Z - 1, P.BASE_Z + 0.6, x, y)
    # button + ring locating holes (blind, glued)
    bz = P.BTN_Z
    yb = -math.sqrt(P.R ** 2 - bz ** 2)
    low = low - cyl_between(2.15, (0, yb - 1, bz), (0, yb + 2.0, bz))
    for s in (-1, 1):
        x = s * P.BTN_RING_PEG_R
        y = -math.sqrt(P.R ** 2 - bz ** 2 - x ** 2)
        low = low - cyl_between(1.6, (x, y - 1, bz), (x, y + 1.9, bz))
    return low


def pod_cup_u():
    """Bezel cup in the U frame (front lip with window, bore for the glass)."""
    y_front = -(P.LIP_GAP + P.LIP_T)
    yr = y_front - 1.0                                   # raised outer rim (stepped bezel, photo)
    prof = [(P.WINDOW_R + 0.6, y_front), (24.0, y_front), (25.0, yr), (P.BEZEL_OR - 1.6, yr), (P.BEZEL_OR - 0.47, yr + 0.47),
            (P.BEZEL_OR, yr + 1.6), (P.BEZEL_OR, P.PLATE_Y0), (P.BEZEL_BORE_R, P.PLATE_Y0),
            (P.BEZEL_BORE_R, -P.LIP_GAP), (P.WINDOW_R, -P.LIP_GAP), (P.WINDOW_R, y_front + 0.6)]
    face = make_face(Polyline(*prof, close=True))         # XY plane: x = radius, y = axial
    cup = revolve(face, Axis.Y, 360)
    return cup


def build_bezel():
    cup = pod_cup_u()
    ox, oy0, oy1 = P.USB_OPEN
    cup = cup - box(-ox, ox, oy0, oy1, -40, -18)
    cup = cup - box(-ox, -6 + P.USB_ADAPTER[1] + 1.0, oy0, oy1, -40, P.USB_MOUTH_ZU - P.USB_ADAPTER[0] + 12.8)   # adapter side leg (hidden under the floor)
    for ang in P.BEZEL_SCREW_ANG:
        x, z = polar_xy(P.BEZEL_SCREW_R, ang)
        cup = cup - cyl_u(P.M2_PT_PILOT / 2, P.PLATE_Y0 - 8, P.PLATE_Y0 + 1, x, z)
    return POD * cup


def plate_u():
    y0, y1 = P.PLATE_Y0, P.PLATE_Y0 + P.PLATE_T
    plate = cyl_u(P.BEZEL_OR, y0, y1)
    a, b, hz = P.HEADER_WIN
    for s in (-1, 1):
        x0, x1 = sorted((s * a, s * b))
        plate = plate - box(x0, x1, y0 - 1, y1 + 1, -hz, hz)
    kw, kh = P.KEY_WIN
    for kx, kz in P.KEYS_XZ:
        plate = plate - box(kx - kw / 2, kx + kw / 2, y0 - 1, y1 + 1, kz - kh / 2, kz + kh / 2)
    for x, z in P.STANDOFFS_XZ:
        plate = plate - cyl_u(P.M2_CLEAR / 2, y0 - 1, y1 + 1, x, z)
        plate = plate - (Plane(origin=(x, y1 + 0.01, z), z_dir=(0, -1, 0)).location * Cone(2.1, 1.15, 1.0, align=None))
    for ang in P.BEZEL_SCREW_ANG:
        x, z = polar_xy(P.BEZEL_SCREW_R, ang)
        plate = plate - cyl_u(P.M2_CLEAR / 2, y0 - 1, y1 + 1, x, z)
    ox, _, _ = P.USB_OPEN
    plate = plate - box(-ox, ox, y0 - 1, y1 + 1, -40, -20)
    return plate


def build_cradle():
    plate = POD * plate_u()
    keep = zslab(P.DECK_TOP_Z, 200)
    plate = plate & keep
    foot = box(-P.FOOT_HALF_X - 4, P.FOOT_HALF_X + 4, P.FOOT_Y[0] - 30, P.FOOT_Y[1], P.DECK_TOP_Z, P.DECK_TOP_Z + P.FOOT_T)
    # gussets: plate back face -> foot, outside the header columns
    gus = None
    for s in (-1, 1):
        a = P.u_to_ball((0, P.PLATE_Y0 + P.PLATE_T - 0.4, -19.5))
        b = P.u_to_ball((0, P.PLATE_Y0 + P.PLATE_T - 0.4, 6.0))
        pts = [(a[1], P.DECK_TOP_Z), (b[1], b[2]), (P.FOOT_Y[1], P.DECK_TOP_Z + P.FOOT_T - 0.01), (P.FOOT_Y[1], P.DECK_TOP_Z)]
        x0, x1 = sorted((s * 21.0, s * 24.0))
        g = yz_prism(pts, x0, x1)
        gus = g if gus is None else gus + g
    # side brackets beside the bezel, reaching the tray floor (photo: chunky cradle with corner screws)
    w0, w1 = P.WING_X
    for s in (-1, 1):
        x0, x1 = sorted((s * w0, s * w1))
        wing = yz_prism([(-1.5, -50.0), (P.PLATE_Y0 + P.PLATE_T, -50.0), (P.PLATE_Y0 + P.PLATE_T, 6.0), (5.0, 9.0), (-1.5, 4.0)], x0, x1)
        tx0, tx1 = sorted((s * 29.0, s * w1))
        tab_u = box(tx0, tx1, P.PLATE_Y0, P.PLATE_Y0 + P.PLATE_T, -30.0, 6.0)
        gus = gus + (POD * (wing + tab_u))
        fx0, fx1 = sorted((s * w0, s * (P.WING_SCREW[0] + 3.4)))
        gus = gus + box(fx0, fx1, P.WING_TAB_Y[0], P.WING_TAB_Y[1], P.DECK_TOP_Z, P.DECK_TOP_Z + 3.0)
    shroud = cyl_u(P.BEZEL_OR, P.PLATE_Y0 + P.PLATE_T - 0.01, P.SHROUD_Y1) - cyl_u(P.BEZEL_OR - P.SHROUD_T, P.PLATE_Y0, P.SHROUD_Y1 + 1)
    gus = gus + (POD * shroud)
    cr = plate + foot + gus
    # the slab must stay behind the plate front (it would show under the screen otherwise)
    front_cut = POD * box(-P.WING_X[0] + 0.01, P.WING_X[0] - 0.01, -60, P.PLATE_Y0 + 0.01, -80, 80)
    cr = cr - (front_cut - plate)
    for s in (-1, 1):
        x = s * P.FOOT_SCREW_X
        cr = cr - cyl_z(P.M3_CLEAR / 2, P.DECK_TOP_Z - 1, P.DECK_TOP_Z + P.FOOT_T + 1, x, 18.0)
        cr = cr - cyl_z(3.2, P.DECK_TOP_Z + P.FOOT_T - 1.6, P.DECK_TOP_Z + P.FOOT_T + 5, x, 18.0)
        wx, wy = s * P.WING_SCREW[0], P.WING_SCREW[1]
        cr = cr - cyl_z(P.M3_CLEAR / 2, P.DECK_TOP_Z - 1, P.DECK_TOP_Z + 4, wx, wy)
        cr = cr - (Pos(wx, wy, P.DECK_TOP_Z + 3.0 - 1.75) * Cone(1.7, 3.2, 1.76, align=None))
        cx, cy = P.CABLE_HOLE
        cr = cr - box(s * 16 - cx / 2 - 0.6, s * 16 + cx / 2 + 0.6, 2.0 - 0.6, 2.0 + cy + 0.6, P.DECK_TOP_Z - 1, P.DECK_TOP_Z + 6)
    # board standoff holes must stay open through the slab region (screwdriver access from behind)
    for x, z in P.STANDOFFS_XZ:
        cr = cr - (POD * cyl_u(3.0, P.PLATE_Y0 + P.PLATE_T, P.PLATE_Y0 + 40, x, z))
    return cr & zslab(P.DECK_TOP_Z, 200)


def pod_envelope_u(grow):
    """Envelope of bezel + plate (U frame) used to cut the deck."""
    return cyl_u(P.BEZEL_OR + grow, -(P.LIP_GAP + P.LIP_T) - grow, P.PLATE_Y0 + P.PLATE_T + grow)


def hex_z(af, z0, z1, x, y):
    r = af / math.sqrt(3)
    pts = [(x + r * math.cos(math.radians(60 * k)), y + r * math.sin(math.radians(60 * k))) for k in range(6)]
    return Pos(0, 0, z0) * extrude(make_face(Polyline(*pts, close=True)), z1 - z0)


def build_tray():
    """Lavender inner cover: floor + wall + rim lip. Hides all wiring; goes in through the belt bore (r <= 61.4)."""
    z0, z1 = P.DECK_TOP_Z - P.DECK_T, P.DECK_TOP_Z
    wi, wo = P.TRAY_WALL_R
    top, lt = P.TRAY_LIP_TOP, P.TRAY_LIP_T
    tray = cyl_z(P.TRAY_R, z0, z1)
    tray = tray + (cyl_z(wo, z1 - 0.01, top) - cyl_z(wi, z0 - 1, top + 1))
    tray = tray + (cyl_z(P.TRAY_R, top - lt, top) - cyl_z(wi, z0, top + 1))
    cone_h = P.TRAY_R - wo                                # 45 deg chamfer under the lip: printable floor-down
    tray = tray + ((Pos(0, 0, top - lt - cone_h) * Cone(wo, P.TRAY_R, cone_h, align=None)) - cyl_z(wi, z0, top + 1))
    # clear the belt bosses (latch magnets, reed sensor) that hang inside the bore
    for az in P.MAG_AZ:
        x, y, _ = P.unit(az, 0)
        tray = tray - cyl_z(P.MAG_BOSS_D / 2 + 0.6, z1 + 0.5, top + 1, x * P.MAG_R, y * P.MAG_R)
    sx, sy, _ = P.unit(P.SENSOR_AZ, 0)
    pl = Plane(origin=(0, 0, 0), x_dir=(sy, -sx, 0), z_dir=(0, 0, 1))
    tray = tray - (pl.location * box(-9.6, 9.6, P.SENSOR_R - 6.6, P.R, z1 + 0.5, top + 1))
    tray = tray - (POD * pod_envelope_u(P.DECK_CLEAR))
    for ang in P.DECK_SCREW_ANG:
        x, y = polar_xy(P.DECK_SCREW_R, ang)
        tray = tray - cyl_z(P.M3_CLEAR / 2, z0 - 1, z1 + 1, x, y)
        tray = tray - (Pos(x, y, z1 - 1.75) * Cone(1.7, 3.2, 1.76, align=None))
    nuts = [(s * P.FOOT_SCREW_X, 18.0) for s in (-1, 1)] + [(s * P.WING_SCREW[0], P.WING_SCREW[1]) for s in (-1, 1)]
    for x, y in nuts:                                     # M3 machine screw from the top + nut underneath
        tray = tray + cyl_z(4.6, z0 - 3.0, z0 + 0.01, x, y)
        tray = tray - cyl_z(P.M3_CLEAR / 2, z0 - 4, z1 + 1, x, y)
        tray = tray - hex_z(5.7, z0 - 3.01, z0 - 0.6, x, y)
    for s in (-1, 1):
        cx, cy = P.CABLE_HOLE
        tray = tray - box(s * 16 - cx / 2, s * 16 + cx / 2, 2.0, 2.0 + cy, z0 - 1, z1 + 1)
    return tray


def build_button_ring():
    bz = P.BTN_Z
    ax_y = -math.sqrt(P.R ** 2 - bz ** 2)
    front = ax_y - P.BTN_RING_PROUD
    ring = cyl_between(P.BTN_RING_OD / 2, (0, front, bz), (0, ax_y + 8, bz)) - Sphere(P.R)
    ring = ring - cyl_between(P.BTN_RING_ID / 2, (0, front - 1, bz), (0, ax_y + 9, bz))
    # soft outer edge: 0.8 mm 45 deg chamfer on the front rim
    edge = cyl_between(P.BTN_RING_OD / 2 + 1, (0, front - 1, bz), (0, front + 0.8, bz)) - \
        (Pos(0, front + 0.8, bz) * Rot(X=90) * Cone(P.BTN_RING_OD / 2, P.BTN_RING_OD / 2 - 1.8, 1.8, align=None))
    ring = ring - edge
    for s in (-1, 1):
        x = s * P.BTN_RING_PEG_R
        y = -math.sqrt(P.R ** 2 - bz ** 2 - x ** 2)
        ring = ring + cyl_between(1.45, (x, y - 0.5, bz), (x, y + 1.7, bz))
    return ring


def build_button():
    """White button: cylinder from the shell to the rim plane + a shallow dome (photo: clearly 3D, rounded)."""
    bz = P.BTN_Z
    ax_y = -math.sqrt(P.R ** 2 - bz ** 2)
    r = P.BTN_D / 2
    rim = ax_y - (P.BTN_PROUD - P.BTN_DOME)
    btn = cyl_between(r, (0, rim, bz), (0, ax_y + 8, bz)) - Sphere(P.R + 0.05)
    rc = (r ** 2 + P.BTN_DOME ** 2) / (2 * P.BTN_DOME)
    dome = (Pos(0, rim - P.BTN_DOME + rc, bz) * Sphere(rc)) & cyl_between(r, (0, rim - P.BTN_DOME - 1, bz), (0, rim + 0.01, bz))
    btn = btn + dome
    btn = btn + cyl_between(2.0, (0, ax_y - 0.5, bz), (0, ax_y + 1.8, bz))
    return btn


# ------------------------------------------------------------------------------------------------
def write_stl(shape, path):
    """Tessellate and make sure the printer gets a closed mesh (retry finer, then repair tiny holes)."""
    import trimesh
    for tol, ang in ((0.04, 0.12), (0.03, 0.1), (0.05, 0.15), (0.02, 0.08)):
        export_stl(shape, path, tolerance=tol, angular_tolerance=ang)
        m = trimesh.load(path, force="mesh")
        m.merge_vertices()
        if m.is_watertight:
            return "ok"
    m.update_faces(m.nondegenerate_faces())
    trimesh.repair.fill_holes(m)
    m.merge_vertices()
    m.export(path)
    return "repaired" if m.is_watertight else "OPEN"


def export(name, shape, folder="step"):
    export_step(shape, os.path.join(OUT, folder if folder != "stl" else "step", f"{name}.step"))
    sub = "stl" if folder == "step" else folder
    stl_state = write_stl(shape, os.path.join(OUT, sub, f"{name}.stl"))
    bb = shape.bounding_box()
    report["parts"][name] = {"valid": bool(shape.is_valid), "volume_mm3": round(shape.volume, 1), "stl": stl_state,
                             "bbox": [round(v, 2) for v in (bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z)]}
    print(name, report["parts"][name])


def export_fit(name, shape):
    export_step(shape, os.path.join(OUT, "fitkit", f"{name}.step"))
    stl_state = write_stl(shape, os.path.join(OUT, "fitkit", f"{name}.stl"))
    bb = shape.bounding_box()
    report.setdefault("fitkit", {})[name] = {"valid": bool(shape.is_valid), "volume_mm3": round(shape.volume, 1), "stl": stl_state,
                                             "bbox": [round(v, 2) for v in (bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z)]}
    print("fit", name, report["fitkit"][name])


def purchased():
    """Envelopes of bought parts (checks only)."""
    env = {}
    env["dowel_pin_3x30"] = cyl_x(P.PIN_D / 2, -P.PIN_L / 2, P.PIN_L / 2, P.PIVOT_Y, P.PIVOT_Z)
    for i, az in enumerate(P.MAG_AZ):
        x, y, _ = P.unit(az, 0)
        cx, cy = x * P.MAG_R, y * P.MAG_R
        env[f"magnet_lid_{i}"] = cyl_z(P.MAG_D / 2, P.BH + 0.05, P.BH + P.MAG_H, cx, cy)
        env[f"magnet_belt_{i}"] = cyl_z(P.MAG_D / 2, P.BH - P.MAG_H, P.BH - 0.05, cx, cy)
    fz = P.BASE_Z + P.FLOOR_T
    env["steel_weight"] = cyl_z(P.WEIGHT_D / 2, fz + 0.05, fz + P.WEIGHT_H)
    d = P.unit(P.BUZ_AZ, P.BUZ_EL)
    env["buzzer_wt1205"] = along(d, P.BUZ_D / 2 + 0.25, P.RI_LOW - P.BUZ_H - 0.25, P.RI_LOW - 0.05)
    # buzzer driver perfboard taped under the deck (left-front, away from the pod and USB route)
    zd = P.DECK_TOP_Z - P.DECK_T
    env["buzzer_driver_board"] = box(-48, -48 + P.DRV_BOARD[0], -14, -14 + P.DRV_BOARD[1], zd - P.DRV_BOARD[2] - 1.0, zd - 1.0)
    # right-angle USB-C adapter (Adafruit 4432 envelope, turning to +x_u) + extension plug
    y0, y1 = P.USB_YU
    m = P.USB_MOUTH_ZU
    a = box(-6, 6, y0, y1, m - P.USB_ADAPTER[0], m)
    b = box(-6, -6 + P.USB_ADAPTER[1], y0, y1, m - P.USB_ADAPTER[0], m - P.USB_ADAPTER[0] + 12)
    plug = box(-6 + P.USB_ADAPTER[1], -6 + P.USB_ADAPTER[1] + 22, y0 + 0.5, y1 - 0.5, m - P.USB_ADAPTER[0] + 2.5, m - P.USB_ADAPTER[0] + 9.5)
    env["usb_right_angle_adapter"] = POD * (a + b)
    env["usb_extension_plug"] = POD * plug
    pd = P.unit(180, P.PORT_EL)
    env["usb_panel_port_body"] = along(pd, 29.5 / 2, P.R - 3.6 - 12.0, P.R - 3.65)
    # lid sensor (Littelfuse 59155) in the belt pocket, actuator (57155, envelope assumed) in the lid pocket
    sx, sy, _ = P.unit(P.SENSOR_AZ, 0)
    pl = Plane(origin=(0, 0, 0), x_dir=(sy, -sx, 0), z_dir=(0, 0, 1))
    t, rr, hh = P.SENSOR_BOX
    ztop = P.BH - P.SENSOR_SKIN
    env["reed_sensor_59155"] = pl.location * box(-t / 2, t / 2, P.SENSOR_R - rr / 2, P.SENSOR_R + rr / 2, ztop - hh - 0.05, ztop - 0.05)
    t, rr, hh = P.ACTUATOR_BOX
    env["reed_actuator_57155"] = pl.location * box(-t / 2, t / 2, P.SENSOR_R - rr / 2, P.SENSOR_R + rr / 2, P.BH + 0.05, P.BH + hh)
    # board envelope puck (used in the assembly STEP instead of the vendor model)
    env["board_envelope"] = POD * cyl_u(P.GLASS_R, -0.0, 10.7)
    return env


lid = build_lid()
ear_l, ear_r = build_ear(-1), build_ear(1)
liner = build_liner()
belt = build_belt()
lower = build_lower()
deck = build_tray()
bezel = build_bezel()
cradle = build_cradle()
stop_block = build_stop_block()
rim_ring = build_rim_ring()
ring = build_button_ring()
btn = build_button()

PARTS = {"lid_lavender": lid, "lid_liner_lavender": liner, "ear_left_pink": ear_l, "ear_right_pink": ear_r,
         "belt_black": belt, "lower_shell_ivory": lower, "inner_cover_lavender": deck,
         "display_bezel_plum": bezel, "display_cradle_plum": cradle, "stop_block_black": stop_block,
         "rim_ring_lavender": rim_ring,
         "button_ring_plum": ring, "button_white": btn}
for k, v in PARTS.items():
    export(k, v)

ENV = purchased()
for k, v in ENV.items():
    export_stl(v, os.path.join(OUT, "purchased", f"{k}.stl"), tolerance=0.05, angular_tolerance=0.2)

# fit-kit coupons: intersections of the real solids (same geometry, same print orientation)
fit = {
    "fit1_display_bezel": bezel,
    "fit1_display_plate": cradle & (POD * box(-40, 40, P.PLATE_Y0 - 1, P.PLATE_Y0 + P.PLATE_T + 1, -40, 40)),
    "fit2_hinge_belt": belt & box(-20, 20, 56, 80, -BIG, BIG),
    "fit2_hinge_lid": lid & box(-20, 20, 56, 80, P.BH - 1, 22),
    "fit3_joint_belt": belt & box(-20, 20, -BIG, -45, -BIG, BIG),
    "fit3_joint_lower": lower & box(-20, 20, -BIG, -45, -16, BIG),
    "fit4_magnet_lid": lid & box(18, 52, -70, -40, P.BH - 1, 14),
    "fit4_magnet_belt": belt & box(18, 52, -70, -40, -BIG, BIG),
    "fit6_sensor_belt": belt & box(-BIG, -50, -16, 16, -BIG, BIG),
    "fit6_sensor_lid": lid & box(-BIG, -50, -16, 16, P.BH - 1, 16),
    "fit2_stop_block": stop_block,
}
d_r = P.unit(P.EAR_AZ, P.EAR_EL)
c_r = V(*d_r) * P.R
fit["fit5_ear_seat_lid"] = lid & (Pos(c_r.X, c_r.Y, c_r.Z) * Box(34, 34, 34))
fit["fit5_ear_right"] = ear_r
fit["fit5_button_patch_lower"] = lower & box(-22, 22, -BIG, -55, -28, 0)
for k, v in fit.items():
    export_fit(k, v)

# assemblies (printed parts + simplified envelopes)
asm_keys = list(PARTS) + ["dowel_pin_3x30", "magnet_lid_0", "magnet_lid_1", "magnet_belt_0", "magnet_belt_1",
                          "steel_weight", "board_envelope", "reed_sensor_59155", "reed_actuator_57155"]
LID_GROUP = {"lid_lavender", "lid_liner_lavender", "ear_left_pink", "ear_right_pink", "magnet_lid_0", "magnet_lid_1",
             "reed_actuator_57155"}
for name, deg in (("m7_assembly_closed", 0.0), ("m7_assembly_open110", P.OPEN_DEG)):
    children = []
    for k in asm_keys:
        s = PARTS.get(k) or ENV.get(k)
        s = lid_open(s, deg) if (k in LID_GROUP and deg) else s
        s.label = k
        children.append(s)
    export_step(Compound(children=children), os.path.join(OUT, f"{name}.step"))

json.dump(report, open(os.path.join(OUT, "build_report.json"), "w"), indent=1)
print("done")
