"""Assembly drawings for M6: shaded 3/4 view, exploded view, and dimensioned mid-plane sections.

usage: python render_m6.py <cad_out_dir> <vendor_parts_dir> <img_dir>
"""
import glob
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import trimesh  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

sys.path.insert(0, os.path.dirname(__file__))
import m6_params as P  # noqa: E402

CAD, VEND, IMG = sys.argv[1:4]
os.makedirs(IMG, exist_ok=True)
COL = {"upper_shell_purple": "#7a52b3", "lower_shell_ivory": "#f1ece0", "belt_black": "#26222d",
       "bezel_black": "#2e2a36", "display_plate_petg": "#9fb4c8", "lobe_left_pink": "#e979ad",
       "lobe_right_pink": "#e979ad", "m_inlay_white": "#ffffff"}
parts = {k: trimesh.load(f"{CAD}/stl/{k}.stl") for k in COL}
purch = {os.path.basename(f)[:-4]: trimesh.load(f) for f in glob.glob(f"{CAD}/purchased/*.stl")}


def to_ball(m):
    m = m.copy()
    v = m.vertices.copy()
    m.vertices = np.column_stack([-v[:, 1], P.GLASS_Y + (1.10 - v[:, 2]), v[:, 0]])
    return m


board = []
for f in glob.glob(f"{VEND}/*.stl"):
    m = trimesh.load(f)
    if len(m.faces):
        board.append(to_ball(m))
board = trimesh.util.concatenate(board)


def draw(ax, mesh, color, offset=(0, 0, 0), alpha=1.0, light=np.array([-0.4, -0.8, 0.6])):
    m = mesh.copy()
    tri = m.triangles + np.asarray(offset)
    shade = 0.45 + 0.55 * np.clip(m.face_normals @ (light / np.linalg.norm(light)), 0, 1)
    rgb = np.array(matplotlib.colors.to_rgb(color))
    fc = np.clip(rgb[None, :] * shade[:, None], 0, 1)
    pc = Poly3DCollection(tri, facecolors=fc, edgecolors="none", alpha=alpha)
    ax.add_collection3d(pc)


def setup(ax, lim=80, elev=12, azim=-62):
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_zlim(-lim, lim)
    ax.set_box_aspect((1, 1, 1)); ax.view_init(elev=elev, azim=azim); ax.set_axis_off()


def draw_all(ax, items, light=np.array([-0.4, -0.8, 0.6])):
    """One collection so matplotlib depth-sorts every triangle together."""
    tris, cols = [], []
    for mesh, color, off in items:
        t = mesh.triangles + np.asarray(off)
        shade = 0.45 + 0.55 * np.clip(mesh.face_normals @ (light / np.linalg.norm(light)), 0, 1)
        rgb = np.array(matplotlib.colors.to_rgb(color))
        tris.append(t)
        cols.append(np.clip(rgb[None, :] * shade[:, None], 0, 1))
    ax.add_collection3d(Poly3DCollection(np.concatenate(tris), facecolors=np.concatenate(cols), edgecolors="none"))


# 1 assembled 3/4 view
fig = plt.figure(figsize=(8, 8), dpi=130)
ax = fig.add_subplot(111, projection="3d")
glass = trimesh.creation.cylinder(radius=P.ACTIVE_R, height=0.2, transform=trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))
glass.apply_translation([0, P.GLASS_Y - 0.15, 0])
draw_all(ax, [(m, COL[k], (0, 0, 0)) for k, m in parts.items()] + [(glass, "#fbf7ee", (0, 0, 0))])
setup(ax, 75, 14, -70)
ax.set_title("PokéDock M6 - assembled (CAD, not a photo)", fontsize=10)
fig.savefig(f"{IMG}/m6_assembled_34.png", bbox_inches="tight"); plt.close(fig)

# 2 exploded view
EXP = {"upper_shell_purple": (0, 0, 70), "lobe_left_pink": (-14, -10, 100), "lobe_right_pink": (14, -10, 100),
       "m_inlay_white": (0, -22, 92), "belt_black": (0, 0, 25), "bezel_black": (0, -70, 0),
       "display_plate_petg": (0, -30, 0), "lower_shell_ivory": (0, 0, -35)}
fig = plt.figure(figsize=(10, 10), dpi=120)
ax = fig.add_subplot(111, projection="3d")
draw_all(ax, [(m, COL[k], EXP[k]) for k, m in parts.items()] + [(board, "#3b6e4f", (0, -50, 0))]
         + [(purch[k], "#1f6fb2", (0, 0, -35)) for k in ("usb_breakout", "buzzer")])
setup(ax, 120, 18, -58)
ax.set_title("M6 exploded: upper(+lobes, M) / belt / bezel+board+plate / lower (+USB-C, buzzer)", fontsize=10)
fig.savefig(f"{IMG}/m6_exploded.png", bbox_inches="tight"); plt.close(fig)


# 3 sections
def section(ax, mesh, origin, normal, color, lw=1.0, fill=None):
    s = mesh.section(plane_origin=origin, plane_normal=normal)
    if s is None:
        return
    p2, _ = s.to_2D(to_2D=np.linalg.inv(_frame(origin, normal)))
    for poly in p2.polygons_full if fill else []:
        xs, ys = poly.exterior.xy
        ax.fill(xs, ys, color=fill, alpha=0.85, lw=0)
        for h in poly.interiors:
            xs, ys = h.xy
            ax.fill(xs, ys, color="white", lw=0)
    for e in p2.discrete:
        ax.plot(e[:, 0], e[:, 1], color=color, lw=lw)


def _frame(origin, normal):
    n = np.asarray(normal, float)
    if abs(n[0]) > 0.9:   # x-normal plane: horizontal axis = y, vertical = z
        X, Y = np.array([0, 1.0, 0]), np.array([0, 0, 1.0])
    else:                 # z-normal plane: horizontal = x, vertical = y
        X, Y = np.array([1.0, 0, 0]), np.array([0, 1.0, 0])
    T = np.eye(4)
    T[:3, 0], T[:3, 1], T[:3, 2], T[:3, 3] = X, Y, n, origin
    return T


for name, origin, normal, xl, yl, lim in [
        ("m6_section_x0_side.png", [0, 0, 0], [1, 0, 0], "y (mm, screen faces -y)", "z (mm)", (-75, 75, -65, 75)),
        ("m6_section_z0_top.png", [0, 0, 0.01], [0, 0, 1], "x (mm)", "y (mm)", (-75, 75, -75, 75)),
        ("m6_section_x0_front_detail.png", [0, 0, 0], [1, 0, 0], "y (mm)", "z (mm)", (-73, -45, -32, 32))]:
    fig, ax = plt.subplots(figsize=(9, 9), dpi=140)
    for k, m in parts.items():
        section(ax, m, origin, normal, "#222", 0.8, COL[k] if COL[k] != "#ffffff" else "#dddddd")
    section(ax, board, origin, normal, "#1d5c3a", 0.6, "#5aa877")
    for k, m in purch.items():
        if k == "usb_plug_path":
            section(ax, m, origin, normal, "#1f6fb2", 0.8)
            continue
        section(ax, m, origin, normal, "#1f6fb2", 0.8, "#9cc3e6")
    ax.set_aspect("equal"); ax.set_xlim(lim[0], lim[1]); ax.set_ylim(lim[2], lim[3])
    ax.set_xlabel(xl); ax.set_ylabel(yl); ax.grid(alpha=0.25)
    ax.set_title(f"M6 section {name[11:-4]}: printed parts filled by colour, board green, purchased blue", fontsize=9)
    if "detail" in name:
        for y, txt in [(P.BEZEL_FRONT_Y, "bezel face -71.4"), (P.GLASS_Y, "glass front -69.3"),
                       (P.PLATE_FRONT_Y, "plate / standoff -59.08"), (P.PLATE_BACK_Y, "rib contact -56.58")]:
            ax.axvline(y, color="#c33", lw=0.5, ls="--"); ax.text(y + 0.2, 29, txt, rotation=90, fontsize=7, color="#c33", va="top")
    fig.savefig(f"{IMG}/{name}", bbox_inches="tight"); plt.close(fig)
print("rendered to", IMG)
