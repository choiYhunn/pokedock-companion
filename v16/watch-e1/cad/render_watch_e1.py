"""Quick look renders of the PRELIMINARY E1 desk watch (head + back + board glass, on the base slab).

usage: python render_watch_e1.py <out dir with e1_*.stl> <vendor parts dir> <png>
"""
import glob
import math
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import trimesh  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

OUT, PARTS, PNG = sys.argv[1], sys.argv[2], sys.argv[3]
TILT = 15.0
BASE_H = 12.0


def place(m):
    """board frame (glass +z, USB -x) -> desk frame: -x down, glass facing +y_world, leaning back TILT."""
    m = m.copy()
    r1 = trimesh.transformations.rotation_matrix(math.radians(-90), [1, 0, 0])      # glass normal +z -> +y? (then fix)
    m.apply_transform(r1)
    r2 = trimesh.transformations.rotation_matrix(math.radians(-90), [0, 1, 0])      # board -x (USB) -> world -z (down)
    m.apply_transform(r2)
    r3 = trimesh.transformations.rotation_matrix(math.radians(-TILT), [1, 0, 0])
    m.apply_transform(r3)
    m.apply_translation([0, 0, BASE_H + 30.0 + 22.0 * 0])
    return m


meshes = []
head = place(trimesh.load(os.path.join(OUT, "e1_head.stl")))
back = place(trimesh.load(os.path.join(OUT, "e1_back.stl")))
glass = place(trimesh.load(sorted(glob.glob(os.path.join(PARTS, "001_*.stl")))[0]))
base = trimesh.load(os.path.join(OUT, "e1_base_placeholder.stl"))
dz = BASE_H - min(head.bounds[0][2], back.bounds[0][2]) - 6.0   # stem sinks 6 mm into the base
for m in (head, back, glass):
    m.apply_translation([0, 0, dz])
for m, col in ((base, "#d9c8ef"), (back, "#6b3fa0"), (head, "#9b6fd0"), (glass, "#141018")):
    meshes.append((m, col))

fig = plt.figure(figsize=(12, 6), dpi=120)
for k, (elev, azim, title) in enumerate(((14, 110, "front 3/4"), (5, 180, "side (lean back 15 deg)"))):
    ax = fig.add_subplot(1, 2, k + 1, projection="3d")
    for m, col in meshes:
        f = m.faces[:: max(1, len(m.faces) // 6000)]
        pc = Poly3DCollection(m.vertices[f], facecolor=col, edgecolor="none", alpha=1.0)
        n = m.face_normals[:: max(1, len(m.faces) // 6000)]
        light = np.clip(n @ np.array([0.3, -0.6, 0.75]), 0.15, 1.0)
        rgb = np.array(matplotlib.colors.to_rgb(col))
        pc.set_facecolor(np.c_[np.outer(light, rgb), np.ones(len(light))])
        ax.add_collection3d(pc)
    ax.set_xlim(-45, 45); ax.set_ylim(-45, 45); ax.set_zlim(0, 90)
    ax.set_box_aspect((1, 1, 1)); ax.view_init(elev, azim); ax.set_axis_off(); ax.set_title(title)
fig.suptitle("PokeDock E1 desk watch - PRELIMINARY CAD (not printed, not fitted)")
fig.tight_layout()
fig.savefig(PNG)
print("wrote", PNG)
