"""Line-of-sight and closed-lid clearance checks for the M7 screen (shared by verify_m7.py / optimize_pod.py).

Eye envelope = a person seated at a desk: eye 350-500 mm above the desk top, 450-700 mm in front of the
ball, up to 150 mm to either side (ball on the desk in front of the keyboard/monitor). Rays run from
sample points on the true 36.75 mm active area (0.05 mm above the glass) to each eye point; anything
printed in between (bezel lip included) blocks the ray.
"""
import math

import numpy as np
import trimesh

import m7_params as P

EYES = [(lat, dist, h) for lat in (-150.0, 0.0, 150.0) for dist in (450.0, 550.0, 700.0) for h in (350.0, 420.0, 500.0)]


def screen_frame(dy=0.0, dz=0.0):
    t = math.radians(P.SCREEN_TILT_DEG)
    n = np.array([0.0, -math.sin(t), math.cos(t)])
    u = np.array([0.0, math.cos(t), math.sin(t)])
    c = np.array(P.POD_C) + np.array([0.0, dy, dz])
    return c, n, u


def active_points(dy=0.0, dz=0.0, nr=10, nt=32):
    c, n, u = screen_frame(dy, dz)
    x = np.array([1.0, 0, 0])
    rr = np.sqrt(np.linspace(0.0, 1.0, nr)) * (P.ACTIVE_R - 0.05)
    th = np.linspace(0, 2 * math.pi, nt, endpoint=False)
    return np.array([c + n * 0.05 + r * (math.cos(a) * x + math.sin(a) * u) for r in rr for a in th])


def eye_point(lat, dist, h):
    return np.array([lat, -dist, P.BASE_Z + h])


def visible_fraction(occluder, pts, eye):
    d = eye - pts
    L = np.linalg.norm(d, axis=1, keepdims=True)
    d = d / L
    ray = trimesh.ray.ray_triangle.RayMeshIntersector(occluder)
    locs, idx, _ = ray.intersects_location(pts + d * 0.02, d, multiple_hits=False)
    blocked = np.zeros(len(pts), bool)
    if len(idx):
        dist = np.linalg.norm(locs - pts[idx], axis=1)
        blocked[idx[dist < L[idx, 0] - 1.0]] = True
    return 1.0 - blocked.mean()


def view_report(occluder, dy=0.0, dz=0.0):
    pts = active_points(dy, dz)
    out = {}
    for lat, dist, h in EYES:
        el = math.degrees(math.atan2(h - (P.POD_C[2] + dz - P.BASE_Z), dist))
        out[f"lat{lat:+.0f}_d{dist:.0f}_h{h:.0f} (el {el:.0f})"] = round(visible_fraction(occluder, pts, eye_point(lat, dist, h)), 4)
    return out


def lowest_full_view_height(occluder, dist=550.0, dy=0.0, dz=0.0):
    """Lowest eye height above the desk (mm, straight in front) that still sees the whole active area."""
    pts = active_points(dy, dz, nr=8, nt=24)
    lo = None
    for h in range(60, 501, 10):
        if visible_fraction(occluder, pts, eye_point(0.0, dist, float(h))) >= 0.999:
            lo = h
            break
    return lo


def min_clearance(a_meshes, b_mesh, n=6000):
    """Smallest distance (mm) from surface samples of a_meshes to mesh b (positive = apart)."""
    pts = np.vstack([trimesh.sample.sample_surface_even(m, n)[0] for m in a_meshes])
    _, d, _ = trimesh.proximity.closest_point(b_mesh, pts)
    inside = b_mesh.contains(pts)
    d[inside] = -d[inside]
    return float(d.min())
