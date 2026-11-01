"""CAD-based images of M7 (rendered from the exported STL meshes, not AI images).

usage: python render_m7.py <cad_out_dir> <vendor_parts_dir> <ui_png> <img_dir>
Shaded views use a painter's-algorithm rasteriser (PIL) on the real meshes and the official
Waveshare part meshes. The screen shows a firmware-simulator capture (public geometric TEST pack)
mapped onto the true 36.75 mm active area. Sections are planar cuts of the same meshes (matplotlib).
"""
import glob
import json
import math
import os
import sys

import matplotlib
import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Polygon as MPoly  # noqa: E402

sys.path.insert(0, os.path.dirname(__file__))
import m7_params as P  # noqa: E402

CAD, VEND, UI, IMG = sys.argv[1:5]
os.makedirs(IMG, exist_ok=True)
FONT = "C:/Windows/Fonts/malgun.ttf" if os.path.exists("C:/Windows/Fonts/malgun.ttf") else None

COL = {"lid_lavender": "#a58bd6", "lid_liner_lavender": "#b9a3e0", "ear_left_pink": "#f2a7c3",
       "ear_right_pink": "#f2a7c3", "belt_black": "#3a3640", "lower_shell_ivory": "#f3eee4",
       "deck_lavender": "#c8b6ea", "display_bezel_plum": "#4d3b6e", "display_cradle_plum": "#3d3548",
       "button_ring_black": "#3a3640", "button_white": "#fbfaf7", "stop_block_black": "#3a3640"}
PCOL = {"dowel_pin_3x30": "#b8bcc4", "magnet_lid_0": "#9aa0a8", "magnet_lid_1": "#9aa0a8", "magnet_belt_0": "#9aa0a8",
        "magnet_belt_1": "#9aa0a8", "steel_weight": "#8d939b", "buzzer_wt1205": "#2b2b2b",
        "buzzer_driver_board": "#2f7d4f", "usb_right_angle_adapter": "#1f1f1f", "usb_extension_plug": "#262626",
        "usb_panel_port_body": "#555a60", "reed_sensor_59155": "#d9c36a", "reed_actuator_57155": "#5a5f66"}
LID_GROUP = {"lid_lavender", "lid_liner_lavender", "ear_left_pink", "ear_right_pink", "magnet_lid_0", "magnet_lid_1",
             "reed_actuator_57155"}

printed = {k: trimesh.load(f"{CAD}/stl/{k}.stl") for k in COL}
purch = {os.path.basename(f)[:-4]: trimesh.load(f) for f in glob.glob(f"{CAD}/purchased/*.stl")}
purch.pop("board_envelope", None)
T = math.radians(P.POD_ROT_DEG)
N = np.array([0.0, -math.sin(math.radians(P.SCREEN_TILT_DEG)), math.cos(math.radians(P.SCREEN_TILT_DEG))])
U = np.array([0.0, math.cos(math.radians(P.SCREEN_TILT_DEG)), math.sin(math.radians(P.SCREEN_TILT_DEG))])


def u2b(v):
    return np.column_stack([v[:, 0] + P.POD_C[0], v[:, 1] * math.cos(T) - v[:, 2] * math.sin(T) + P.POD_C[1],
                            v[:, 1] * math.sin(T) + v[:, 2] * math.cos(T) + P.POD_C[2]])


def s2b(m):
    m = m.copy()
    v = m.vertices
    m.vertices = u2b(np.column_stack([-v[:, 1], 1.10 - v[:, 2], v[:, 0]]))
    return m


board = []
rows = json.load(open(f"{VEND}/parts.json"))
for f in sorted(glob.glob(f"{VEND}/*.stl")):
    m = trimesh.load(f, force="mesh")
    if len(m.faces) == 0:
        continue
    idx = int(os.path.basename(f)[:3]) - 1
    path = rows[idx]["path"] if 0 <= idx < len(rows) else ""
    if "TF_CARD" in path:
        continue
    col = "#101014" if ("TP" in path or "PMMA" in path or "DO0143" in path) else (
        "#1f5f3f" if "PCB" in path and "PCBA" not in path.split("/")[-1] else "#8c8f96")
    board.append((s2b(m), col))


def screen_mesh():
    """Active area disc textured with the UI capture (true scale)."""
    img = np.asarray(Image.open(UI).convert("RGB"), float) / 255.0
    nr, nt = 46, 160
    verts, cols, faces = [np.zeros(3)], [img[img.shape[0] // 2, img.shape[1] // 2]], []
    for i in range(1, nr + 1):
        r = P.ACTIVE_R * i / nr
        for j in range(nt):
            a = 2 * math.pi * j / nt
            verts.append(np.array([r * math.cos(a), r * math.sin(a), 0.0]))
    verts = np.array(verts)
    for i in range(1, nr + 1):
        base = 1 + (i - 1) * nt
        for j in range(nt):
            j2 = (j + 1) % nt
            if i == 1:
                faces.append([0, base + j, base + j2])
            else:
                pb = 1 + (i - 2) * nt
                faces.append([pb + j, base + j, base + j2])
                faces.append([pb + j, base + j2, pb + j2])
    faces = np.array(faces)
    cen = verts[faces].mean(1)
    px = ((cen[:, 0] / P.ACTIVE_R + 1) / 2 * (img.shape[1] - 1)).astype(int)
    py = ((1 - (cen[:, 1] / P.ACTIVE_R + 1) / 2) * (img.shape[0] - 1)).astype(int)
    fcol = img[py.clip(0, img.shape[0] - 1), px.clip(0, img.shape[1] - 1)]
    # disc frame: x -> ball x, y (image up) -> screen up U; lifted 0.05 mm above the glass
    b = np.array(P.POD_C) + N * 0.06
    w = b + verts[:, 0:1] * np.array([1.0, 0, 0]) + verts[:, 1:2] * U
    return trimesh.Trimesh(w, faces, process=False), fcol


def lid_tf(deg):
    return trimesh.transformations.rotation_matrix(math.radians(-deg), [1, 0, 0], [0, P.PIVOT_Y, P.PIVOT_Z])


def scene(deg, hide=(), explode=None, with_purch=False):
    items = []
    M = lid_tf(deg)
    for k, m in printed.items():
        if k in hide:
            continue
        mm = m.copy()
        if k in LID_GROUP and deg:
            mm.apply_transform(M)
        if explode and k in explode:
            mm.apply_translation(explode[k])
        items.append((mm, COL[k], None))
    if with_purch:
        for k, m in purch.items():
            mm = m.copy()
            if k in LID_GROUP and deg:
                mm.apply_transform(M)
            items.append((mm, PCOL.get(k, "#777777"), None))
    off = explode.get("pod", (0, 0, 0)) if explode else (0, 0, 0)
    for m, c in board:
        mm = m.copy()
        mm.apply_translation(off)
        items.append((mm, c, None))
    if deg or explode:
        sm, fcol = screen_mesh()
        sm.apply_translation(off)
        items.append((sm, None, fcol))
    return items


def hexrgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float) / 255.0


def render(items, eye_az, eye_el, path, size=(1300, 1100), dist=520.0, target=(0, 5, 0), fov=26.0, labels=()):
    ss = 2
    W, H = size[0] * ss, size[1] * ss
    az, el = math.radians(eye_az), math.radians(eye_el)
    fwd = -np.array([math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)])
    eye = np.array(target) - fwd * dist
    right = np.cross(fwd, [0, 0, 1.0])
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    f = (H / 2) / math.tan(math.radians(fov / 2))
    light = -fwd * 0.55 + up * 0.6 + right * -0.35
    light /= np.linalg.norm(light)
    polys = []
    for m, col, fcol in items:
        v = m.vertices - eye
        x, y, z = v @ right, v @ up, v @ fwd
        tri = m.faces
        fn = m.face_normals
        cen = m.triangles_center
        facing = np.einsum("ij,ij->i", fn, cen - eye) < 0
        if fcol is None:
            base = np.tile(hexrgb(col), (len(tri), 1))
        else:
            base = fcol
            facing = np.ones(len(tri), bool)
        lam = np.clip(fn @ light, 0, 1)
        hvec = (light - fwd)
        hvec /= np.linalg.norm(hvec)
        spec = np.clip(fn @ hvec, 0, 1) ** 24 * 0.18
        shade = base * (0.55 + 0.45 * lam[:, None]) + spec[:, None] if fcol is None else base * 0.97
        zt = z[tri]
        ok = facing & (zt.min(1) > 1)
        sx = W / 2 + f * x[tri] / z[tri]
        sy = H / 2 - f * y[tri] / z[tri]
        depth = zt.mean(1) if fcol is None else np.full(len(tri), -1e9)   # screen on top when it faces the eye
        if fcol is not None and np.dot(N, -fwd) <= 0.05:
            continue
        for i in np.nonzero(ok)[0]:
            polys.append((depth[i], sx[i], sy[i], shade[i]))
    polys.sort(key=lambda p: -p[0])
    im = Image.new("RGB", (W, H), (246, 244, 240))
    dr = ImageDraw.Draw(im)
    for _, sx, sy, c in polys:
        cc = tuple(int(min(1, max(0, t)) * 255) for t in c)
        dr.polygon(list(zip(sx, sy)), fill=cc, outline=cc)
    im = im.resize(size, Image.LANCZOS)
    if FONT:
        d2 = ImageDraw.Draw(im)
        ft = ImageFont.truetype(FONT, 22)
        d2.text((24, 18), "CAD 렌더링 (실제 STL 메시 + Waveshare 공식 STEP) — AI 이미지 아님", fill=(70, 70, 80), font=ft)
        d2.text((24, size[1] - 40), "화면 = 실제 크기 Ø36.75 mm에 펌웨어 시뮬레이터 캡처(공개 TEST 팩)", fill=(90, 90, 100), font=ImageFont.truetype(FONT, 18))
        for (txt, xy) in labels:
            d2.text(xy, txt, fill=(40, 40, 50), font=ImageFont.truetype(FONT, 20))
    im.save(path)
    print("wrote", path, len(polys), "triangles")


render(scene(0), -32, 18, f"{IMG}/render_closed_front34.png")
render(scene(P.OPEN_DEG), -28, 26, f"{IMG}/render_open110_front34.png", target=(0, 15, 8), dist=600)
render(scene(P.OPEN_DEG), 0, 34, f"{IMG}/render_open110_user_view.png", target=(0, 0, 5), dist=560)
render(scene(P.OPEN_DEG), -90, 8, f"{IMG}/render_open110_side.png", target=(0, 25, 15), dist=700)
render(scene(0), 150, 20, f"{IMG}/render_closed_back_hinge.png")
render(scene(0, hide=LID_GROUP | {"deck_lavender"}, with_purch=True), -20, 62, f"{IMG}/render_internal_no_lid_no_deck.png",
       target=(0, 5, -20), dist=560)
render(scene(P.OPEN_DEG, explode={"lid_lavender": (0, 40, 70), "lid_liner_lavender": (0, 40, 40), "ear_left_pink": (-12, 40, 92),
                                  "ear_right_pink": (12, 40, 92), "belt_black": (0, 0, 0), "lower_shell_ivory": (0, 0, -55),
                                  "deck_lavender": (0, 0, -22), "display_bezel_plum": (0, -45, 20), "display_cradle_plum": (0, 0, 10),
                                  "button_ring_black": (0, -25, -10), "button_white": (0, -38, -10), "pod": (0, -45, 20)}),
       -35, 22, f"{IMG}/render_exploded.png", dist=900, target=(0, 10, 10))


# ---------------------------------------------------------------- sections (matplotlib)
def section(meshes, origin, normal, axes):
    out = []
    for name, m, col, ls in meshes:
        s = m.section(plane_origin=origin, plane_normal=normal)
        if s is None:
            continue
        for ent in s.discrete:
            pts = ent[:, axes]
            out.append((name, pts, col, ls))
    return out


def draw_section(path, title, x_plane, deg_overlay=None, xlim=None, ylim=None, notes=(), with_board=True):
    fig, ax = plt.subplots(figsize=(11, 9), dpi=130)
    ms = [(k, m, COL[k], "-") for k, m in printed.items()] + [(k, m, PCOL.get(k, "#777"), "-") for k, m in purch.items()]
    if with_board:
        ms += [("board", m, c, "-") for m, c in board]
    for name, pts, col, ls in section(ms, [x_plane, 0, 0], [1, 0, 0], [1, 2]):
        ax.add_patch(MPoly(pts, closed=True, facecolor=col, edgecolor="#222", lw=0.4, alpha=0.95))
    if deg_overlay is not None:
        M = lid_tf(deg_overlay)
        mov = []
        for k in LID_GROUP & set(printed):
            mm = printed[k].copy()
            mm.apply_transform(M)
            mov.append((k, mm, COL[k], "--"))
        for name, pts, col, ls in section(mov, [x_plane, 0, 0], [1, 0, 0], [1, 2]):
            ax.add_patch(MPoly(pts, closed=True, facecolor="none", edgecolor="#6b4fa8", lw=0.9, ls="--"))
    ax.plot([P.PIVOT_Y], [P.PIVOT_Z], "r+", ms=14, mew=2)
    for t, xy in notes:
        ax.annotate(t, xy=xy[:2], xytext=xy[2:], fontsize=9, arrowprops=dict(arrowstyle="->", lw=0.6), fontproperties=None)
    ax.set_aspect("equal")
    ax.set_xlabel("y (mm, + = 뒤/힌지)" if FONT else "y (mm)")
    ax.set_ylabel("z (mm)")
    if xlim:
        ax.set_xlim(*xlim)
    if ylim:
        ax.set_ylim(*ylim)
    else:
        ax.autoscale_view()
    ax.grid(alpha=0.25)
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    print("wrote", path)


if FONT:
    matplotlib.rcParams["font.family"] = "Malgun Gothic"
    matplotlib.rcParams["axes.unicode_minus"] = False
c = P.POD_C
draw_section(f"{IMG}/section_full_x0_closed_and_open110.png",
             "x = 0 단면: 닫힘(채움) + 110° 열림 뚜껑(점선), 화면 50°, 지름 138 mm", 0.0, P.OPEN_DEG,
             xlim=(-80, 150), ylim=(-70, 150),
             notes=[("힌지 축 y70 z7.5 (Ø3 핀)", (70, 7.5, 95, -20)), ("화면 유리 (50°)", (c[1], c[2], -60, 60)),
                    ("덱 (배선 가림)", (20, -9, 40, -40)), ("강철 와셔 3장 Ø60×12", (0, -52, -50, -68)),
                    ("라이너 (서포트 자국 가림)", (0, 45, -40, 95))])
draw_section(f"{IMG}/section_hinge_x0_lug_heel.png", "힌지 중심 단면 x = 0: 스토퍼 러그(뚜껑)와 힐(벨트), 110°에서 면 접촉",
             0.0, P.OPEN_DEG, xlim=(50, 90), ylim=(-12, 28),
             notes=[("러그 (닫힘)", (72, 12.5, 78, 22)), ("힐 접촉면 -48.6°", (74, 2.6, 82, -6))])
draw_section(f"{IMG}/section_hinge_x11_knuckle.png", "힌지 단면 x = 11: 벨트 너클(압입 Ø2.9)과 뚜껑 노치 R4.6", 11.0, 60.0,
             xlim=(50, 90), ylim=(-12, 28))
draw_section(f"{IMG}/section_display_x0.png", "디스플레이 단면 x = 0: 유리-립 0.6 mm(무하중), 스탠드오프-플레이트 M2, 덱 관통",
             0.0, None, xlim=(-50, 30), ylim=(-30, 45),
             notes=[("립 0.6 mm 간극", (c[1] - 1, c[2] + 19, -48, 40)), ("M2 스탠드오프 → 플레이트", (-3, 0, 5, 35)),
                    ("USB-C ㄱ자 어댑터", (-25, -12, -45, -25))])
draw_section(f"{IMG}/section_display_x16_header.png", "x = 16 단면: 2×7 헤더 창과 배선 구멍", 16.0, None, xlim=(-50, 30), ylim=(-30, 45))
