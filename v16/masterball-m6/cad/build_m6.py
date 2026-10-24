"""Generate PokéDock Master Ball M6 printable parts (STEP + STL) with build123d.

usage: python build_m6.py <out_dir>
Writes <out_dir>/step/*.step, <out_dir>/stl/*.stl and <out_dir>/purchased/*.stl (envelopes of
purchased parts used only for interference checks; never printed).
"""
import json
import math
import os
import sys

import trimesh

from build123d import (Axis, Box, Cone, Cylinder, Plane, Polyline, Pos, Sphere, Spline, Vector,
                       export_step, export_stl, extrude, make_face, offset, revolve, scale)

sys.path.insert(0, os.path.dirname(__file__))
import m6_params as P  # noqa: E402

OUT = sys.argv[1]
BIG = 300.0


def V(*a):
    return Vector(*a)


def zslab(z0, z1):
    return Pos(0, 0, (z0 + z1) / 2) * Box(BIG, BIG, z1 - z0)


def yslab(y0, y1):
    return Pos(0, (y0 + y1) / 2, 0) * Box(BIG, y1 - y0, BIG)


def cyl_between(r, p0, p1):
    p0, p1 = V(*p0), V(*p1)
    d = p1 - p0
    return Plane(origin=(p0 + p1) * 0.5, z_dir=d.normalized()).location * Cylinder(r, d.length)


def cyl_y(r, y0, y1, x=0.0, z=0.0):
    return cyl_between(r, (x, y0, z), (x, y1, z))


def cyl_z(r, z0, z1, x=0.0, y=0.0):
    return cyl_between(r, (x, y, z0), (x, y, z1))


def local_plane(n, up_hint=(0, 0, 1)):
    """Plane at the ball centre whose z axis is n and x axis is horizontal-tangent."""
    n = V(*n).normalized()
    xd = V(*up_hint).cross(n)
    if xd.length < 1e-6:
        xd = V(1, 0, 0)
    return Plane(origin=(0, 0, 0), x_dir=xd.normalized(), z_dir=n)


def local_box(pl, x0, x1, y0, y1, z0, z1):
    return pl.location * Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def local_cyl(pl, r, x, y, z0, z1):
    return pl.location * Pos(x, y, (z0 + z1) / 2) * Cylinder(r, z1 - z0)


def polar_xz(r, ang_deg):
    a = math.radians(ang_deg)
    return r * math.cos(a), r * math.sin(a)


def polar_xy(r, ang_deg):
    a = math.radians(ang_deg)
    return r * math.cos(a), r * math.sin(a)


def opening():
    return cyl_y(P.OPENING_R, -80, -58.5)


# ------------------------------------------------------------------------------------------------
def build_lower():
    foot = Pos(0, 0, (P.BASE_Z + P.FOOT_TANGENT_Z) / 2) * Cone(P.FOOT_R_AT_BASE, -P.FOOT_TANGENT_Z, P.FOOT_TANGENT_Z - P.BASE_Z)
    outer = (Sphere(P.R) + foot) & zslab(P.BASE_Z, -P.BH)
    cavity = Sphere(P.RI) & zslab(P.FLOOR_TOP_Z, -P.BH + 1)
    part = outer - cavity
    collar = (cyl_z(P.R + 1, -10, -P.BH) - cyl_z(P.SPIGOT_R_IN, -11, 0)) & Sphere(P.R)
    spigot = cyl_z(P.SPIGOT_R_OUT, -P.BH - 0.01, P.SPIGOT_TOP_Z) - cyl_z(P.SPIGOT_R_IN, -P.BH - 1, P.SPIGOT_TOP_Z + 1)
    ring = (collar + spigot) - cyl_y(P.SPIGOT_FRONT_CLEAR_R, -80, -20)
    part = part + ring
    part = part - opening()
    # columns for the 3 x M3 shell screws (screwed from the base, under the feet)
    for ang in P.COLUMN_ANGLES:
        x, y = polar_xy(P.COLUMN_R_POS, ang)
        part = part + cyl_z(P.COLUMN_OD / 2, P.FLOOR_TOP_Z - 0.5, -P.BH, x, y)
    for ang in P.COLUMN_ANGLES:
        x, y = polar_xy(P.COLUMN_R_POS, ang)
        part = part - cyl_z(P.M3_CLEAR / 2, P.BASE_Z - 1, -P.BH + 1, x, y)
        part = part - cyl_z(P.M3_HEAD_BORE / 2, P.BASE_Z - 1, P.HEAD_SEAT_Z, x, y)
    # optional steel weight pocket
    d, h = P.WEIGHT_DISC
    part = part + (cyl_z(d / 2 + 0.3 + 1.6, P.FLOOR_TOP_Z - 0.5, P.FLOOR_TOP_Z + h + 1)
                   - cyl_z(d / 2 + 0.3, P.FLOOR_TOP_Z - 0.4, P.FLOOR_TOP_Z + h + 2))
    # lower backstop rib: plate is clamped against it by 2 x M2 screws into bezel inserts
    rib = (yslab(P.LOWER_RIB_Y0, P.LOWER_RIB_Y0 + P.RIB_T) & zslab(P.BASE_Z, -P.BH) & Sphere(P.RI + 0.6)) \
        - cyl_y(P.RIB_WINDOW_R, -80, 0)
    part = part + rib
    for key in ("bot_l", "bot_r"):
        x, z = polar_xz(P.INSERT_R, P.INSERT_ANG[key])
        part = part - cyl_y(P.M2_CLEAR / 2, P.LOWER_RIB_Y0 - 1, P.LOWER_RIB_Y0 + P.RIB_T + 1, x, z)
    # external USB-C port (Adafruit 4090) on a cantilever block, axis = outward radial at elevation -25.
    # Local frame: z = port axis (outward), x = ball x, +y = physically down/forward. The block sits
    # BELOW the PCB; both M2.5 screws are driven from the cavity side, past the receptacle.
    u = P.unit(180, P.USB_EL_DEG)
    pl = Plane(origin=(0, 0, 0), x_dir=(1, 0, 0), z_dir=u)
    pcb_w, pcb_d, pcb_t = P.USB_PCB
    cw, cl, ch = P.USB_CONN
    mouth = P.RI - 0.1
    pcb_edge = mouth - P.USB_CONN_PROTRUDE
    pcb_top = ch / 2               # PCB face carrying the receptacle (receptacle centred on axis)
    pcb_bot = pcb_top + pcb_t
    block = local_box(pl, -11, 11, pcb_bot, pcb_bot + 6.5, pcb_edge - pcb_d - 0.4, P.RI + 0.8) & Sphere(P.R - 0.6)
    part = part + block
    k = P.USB_SLOT_CLR
    part = part - local_box(pl, -cw / 2 - k, cw / 2 + k, -ch / 2 - k, ch / 2 + k, mouth - cl - 0.5, P.RI + 0.35)
    part = part - local_box(pl, -pcb_w / 2 - k, pcb_w / 2 + k, pcb_top - k, pcb_bot + 0.05, pcb_edge - 2.0, P.RI + 0.5)
    part = part - local_box(pl, -P.USB_HOLE[0] / 2, P.USB_HOLE[0] / 2, -P.USB_HOLE[1] / 2, P.USB_HOLE[1] / 2, P.RI - 1, P.R + 2)
    pw, ph, pdepth = P.USB_POCKET
    part = part - local_box(pl, -pw / 2, pw / 2, -ph / 2, ph / 2, P.R - pdepth, P.R + 3)
    for hx, hd in P.USB_HOLES:   # pilot d2.0 for M2.5 x 8 self-tapping (plastite)
        c = pcb_edge - hd
        part = part - (pl.location * Pos(hx, pcb_bot + 3.0, c) * Plane.XZ.location * Cylinder(1.0, 6.0))
    # buzzer pocket + sound holes
    n = P.unit(-140, P.BUZ_EL_DEG)
    pb = Plane(origin=(0, 0, 0), x_dir=V(0, 0, 1).cross(V(*n)).normalized(), z_dir=n)
    c_face = P.RI - 0.4
    boss = local_cyl(pb, P.BUZ_D / 2 + P.BUZ_FIT + 1.6, 0, 0, c_face - P.BUZ_H - P.BUZ_TOL - 0.5, P.RI + 0.6) & Sphere(P.R - 0.5)
    part = part + boss
    part = part - local_cyl(pb, P.BUZ_D / 2 + P.BUZ_FIT, 0, 0, c_face - P.BUZ_H - P.BUZ_TOL - 1, c_face)
    for k in range(7):
        rr, a = (0.0, 0.0) if k == 0 else (3.2, 60.0 * k)
        part = part - local_cyl(pb, 0.75, rr * math.cos(math.radians(a)), rr * math.sin(math.radians(a)), c_face - 0.5, P.R + 2)
    return part


def m_outline(grow=0.0):
    pts = [(-13, -8.5), (-13, 8.5), (-7.5, 8.5), (0, 0.5), (7.5, 8.5), (13, 8.5), (13, -8.5), (8.5, -8.5),
           (8.5, 2.5), (0, -5.5), (-8.5, 2.5), (-8.5, -8.5)]
    f = make_face(Polyline(*pts, close=True))
    return offset(f, amount=grow) if grow else f


def m_prism(grow, c0, c1):
    n = P.unit(0, P.M_EL)
    pl = Plane(origin=V(*n) * c0, x_dir=(1, 0, 0), z_dir=n)
    return extrude(pl.location * m_outline(grow), amount=c1 - c0)


def lobe_frame(side):
    n = V(*P.unit(side * P.LOBE_AZ, P.LOBE_EL))
    th = V(0, 0, 1).cross(n).normalized()
    return Plane(origin=n * (P.R - P.LOBE_SEAT_SAG), x_dir=th, z_dir=n)


def build_upper():
    outer = Sphere(P.R) & zslab(P.BH, P.R + 1)
    cavity = Sphere(P.RI) & zslab(P.BH - 1, P.R)
    part = outer - cavity
    part = part - cyl_z(P.COUNTERBORE_R, P.BH - 1, P.SPIGOT_TOP_Z + 0.4)
    part = part - (Pos(0, 0, P.BH + 0.2) * Cone(P.COUNTERBORE_R + 0.4, P.COUNTERBORE_R, 0.4))  # elephant-foot relief
    part = part - opening()
    for ang in P.COLUMN_ANGLES:
        x, y = polar_xy(P.COLUMN_R_POS, ang)
        part = part + (cyl_z(P.COLUMN_OD / 2, P.BH, P.R, x, y) & Sphere(P.RI + 0.6))
    for ang in P.COLUMN_ANGLES:
        x, y = polar_xy(P.COLUMN_R_POS, ang)
        part = part - cyl_z(P.M3_INSERT_HOLE / 2, P.BH - 1, P.BH + P.UPPER_BOSS_DEPTH, x, y)
    rib = (yslab(P.UPPER_RIB_Y0, P.UPPER_RIB_Y0 + P.RIB_T) & zslab(P.BH, P.R) & Sphere(P.RI + 0.6)) \
        - cyl_y(P.RIB_WINDOW_R, -80, 0)
    part = part + rib
    # lobe seats: flat facet, 2 locating pin holes, centre M2 screw from inside on a boss
    for side in (-1, 1):
        pl = lobe_frame(side)
        part = part + (pl.location * Pos(0, 0, -(P.R - P.LOBE_SEAT_SAG) + 63.0 + 1.8) * Cylinder(4.0, 3.6))
        part = part - (pl.location * Pos(0, 0, 3) * Cylinder(14.0, 6.0))
        for px in (-6.0, 6.0):
            part = part - (pl.location * Pos(px, 0, -2.0) * Cylinder(1.8, 4.4))
        part = part - (pl.location * Pos(0, 0, -3.0) * Cylinder(1.2, 8.0))
    part = part - m_prism(P.M_POCKET_GROW, P.M_PLANE_D, P.R + 3)
    return part


def build_belt():
    part = (Sphere(P.R) & zslab(-P.BH, P.BH)) - cyl_z(P.COUNTERBORE_R, -P.BH - 1, P.BH + 1)
    part = part - (Pos(0, 0, -P.BH + 0.2) * Cone(P.COUNTERBORE_R + 0.4, P.COUNTERBORE_R, 0.4))  # elephant-foot relief
    return part - opening()


def build_bezel():
    fy, gy = P.BEZEL_FRONT_Y, P.GLASS_Y - P.LIP_GAP
    skirt = [(24.5 + 4.5 * math.sin(math.radians(t)), -64.0 - (fy + 64.0) * -math.cos(math.radians(t)))
             for t in range(0, 91, 10)]
    pts = [(P.WINDOW_R, fy + P.WINDOW_CHAMFER), (P.WINDOW_R + P.WINDOW_CHAMFER, fy)] + skirt[1:] + [
        (P.BEZEL_R, P.PLATE_FRONT_Y - 0.4), (P.BEZEL_R - 0.4, P.PLATE_FRONT_Y),  # 0.4 chamfer: first layer on bed
        (P.POCKET_R, P.PLATE_FRONT_Y), (P.POCKET_R, gy), (P.WINDOW_R, gy)]
    pts = [(24.5, fy) if i == 2 else p for i, p in enumerate(pts)]
    prof = make_face(Polyline(*pts, close=True))
    part = revolve(prof, axis=Axis.Y)
    for key, ang in P.INSERT_ANG.items():
        x, z = polar_xz(P.INSERT_R, ang)
        part = part - cyl_y(P.M2_PT_PILOT / 2, P.PLATE_FRONT_Y - 6.5, P.PLATE_FRONT_Y + 0.5, x, z)  # M2 PT screw pilot
    return part


def countersink(x, z):
    hole = cyl_y(P.M2_CLEAR / 2, P.PLATE_FRONT_Y - 1, P.PLATE_BACK_Y + 1, x, z)
    cone = Plane(origin=(x, P.PLATE_BACK_Y + 0.01, z), z_dir=(0, -1, 0)).location * Cone(2.1, P.M2_CLEAR / 2, 0.95, align=None)
    return hole + Pos(0, 0, 0) * cone


def build_plate():
    part = cyl_y(P.PLATE_R, P.PLATE_FRONT_Y, P.PLATE_BACK_Y)
    for x, z in P.STANDOFFS_XZ:
        part = part - countersink(x, z)
    for key, ang in P.INSERT_ANG.items():
        x, z = polar_xz(P.INSERT_R, ang)
        part = part - (countersink(x, z) if key.startswith("top") else cyl_y(P.M2_CLEAR / 2, P.PLATE_FRONT_Y - 1, P.PLATE_BACK_Y + 1, x, z))
    wx, wz = P.PLATE_WINDOW
    for sx in (-1, 1):
        part = part - (Pos(sx * P.HEADERS_X, (P.PLATE_FRONT_Y + P.PLATE_BACK_Y) / 2, 0) * Box(wx, 5, wz))
    for x, z in P.KEYS_XZ:
        part = part - cyl_y(1.6, P.PLATE_FRONT_Y - 1, P.PLATE_BACK_Y + 1, x, z)
    return part


def build_lobe(side):
    a, b, c = P.LOBE_AXES
    pl = lobe_frame(side)
    dome = scale(Sphere(1.0), by=(a, b, c)) & (Pos(0, 0, c) * Box(4 * a, 4 * b, 2 * c))
    for px in (-6.0, 6.0):
        dome = dome + (Pos(px, 0, -1.2) * Cylinder(1.5, 2.4))
    dome = dome - (Pos(0, 0, 3.0) * Cylinder(0.8, 6.0))
    return pl.location * dome


def build_m_inlay():
    return m_prism(-P.M_INLAY_SHRINK, P.M_PLANE_D, P.R + 2) & Sphere(P.R)


# ---- purchased-part envelopes (checks only) -----------------------------------------------------
def purchased():
    env = {}
    u = P.unit(180, P.USB_EL_DEG)
    pl = Plane(origin=(0, 0, 0), x_dir=(1, 0, 0), z_dir=u)
    pcb_w, pcb_d, pcb_t = P.USB_PCB
    cw, cl, ch = P.USB_CONN
    mouth = P.RI - 0.1
    edge = mouth - P.USB_CONN_PROTRUDE
    env["usb_breakout"] = local_box(pl, -pcb_w / 2, pcb_w / 2, ch / 2, ch / 2 + pcb_t, edge - pcb_d, edge) + \
        local_box(pl, -cw / 2, cw / 2, -ch / 2, ch / 2, mouth - cl, mouth)
    for hx, hd in P.USB_HOLES:
        side = "l" if hx < 0 else "r"
        env[f"usb_screw_{side}"] = pl.location * Pos(hx, ch / 2 + pcb_t + 3.2, edge - hd) * Plane.XZ.location * Cylinder(1.25, 6.4)
    env["usb_plug_path"] = local_box(pl, -6.2, 6.2, -3.3, 3.3, P.R - P.USB_POCKET[2] + 0.05, P.R + 25)
    n = P.unit(-140, P.BUZ_EL_DEG)
    pb = Plane(origin=(0, 0, 0), x_dir=V(0, 0, 1).cross(V(*n)).normalized(), z_dir=n)
    env["buzzer"] = local_cyl(pb, P.BUZ_D / 2 + P.BUZ_TOL / 2, 0, 0, P.RI - 0.4 - P.BUZ_H - P.BUZ_TOL, P.RI - 0.45)  # max-size part
    sx, sz = P.SOCKET_BOX
    env["socket_left"] = Pos(-P.HEADERS_X, sum(P.SOCKET_Y) / 2, 0) * Box(sx, P.SOCKET_Y[1] - P.SOCKET_Y[0], sz)
    env["socket_right"] = Pos(P.HEADERS_X, sum(P.SOCKET_Y) / 2, 0) * Box(sx, P.SOCKET_Y[1] - P.SOCKET_Y[0], sz)
    for i, ang in enumerate(P.COLUMN_ANGLES):
        x, y = polar_xy(P.COLUMN_R_POS, ang)
        env[f"m3x50_{i}"] = cyl_z(1.5, P.HEAD_SEAT_Z, P.HEAD_SEAT_Z + 50, x, y) + cyl_z(2.75, P.HEAD_SEAT_Z - 3, P.HEAD_SEAT_Z, x, y)
        env[f"m3_insert_{i}"] = cyl_z(2.0, P.BH, P.BH + 5.7, x, y)
    d, h = P.WEIGHT_DISC
    env["steel_disc"] = cyl_z(d / 2, P.FLOOR_TOP_Z, P.FLOOR_TOP_Z + h)
    return env


def export_clean_stl(shp, path, tol=0.02, ang=0.15):
    """Tessellate, drop zero-area pole slivers, merge, and refuse to write a non-watertight STL."""
    export_stl(shp, path, tolerance=tol, angular_tolerance=ang)
    m = trimesh.load(path, force="mesh")
    m.merge_vertices()
    m.update_faces(m.nondegenerate_faces())
    m.remove_unreferenced_vertices()
    m.merge_vertices()
    m.fix_normals()
    if not m.is_watertight:
        raise SystemExit(f"non-watertight STL: {path}")
    m.export(path)
    return m


def main():
    os.makedirs(f"{OUT}/step", exist_ok=True)
    os.makedirs(f"{OUT}/stl", exist_ok=True)
    os.makedirs(f"{OUT}/purchased", exist_ok=True)
    parts = {
        "upper_shell_purple": build_upper(),
        "lower_shell_ivory": build_lower(),
        "belt_black": build_belt(),
        "bezel_black": build_bezel(),
        "display_plate_petg": build_plate(),
        "lobe_left_pink": build_lobe(-1),
        "lobe_right_pink": build_lobe(1),
        "m_inlay_white": build_m_inlay(),
    }
    meta = {}
    for name, shp in parts.items():
        export_step(shp, f"{OUT}/step/{name}.step")
        mesh = export_clean_stl(shp, f"{OUT}/stl/{name}.stl")
        bb = shp.bounding_box()
        meta[name] = {"volume_mm3": round(shp.volume, 1), "valid": shp.is_valid,
                      "bbox": [round(v, 2) for v in (bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z)],
                      "stl_watertight": bool(mesh.is_watertight), "stl_faces": int(len(mesh.faces))}
        print(name, meta[name])
    for name, shp in purchased().items():
        export_clean_stl(shp, f"{OUT}/purchased/{name}.stl", ang=0.2)
    json.dump(meta, open(f"{OUT}/parts_meta.json", "w"), indent=1)


if __name__ == "__main__":
    main()
