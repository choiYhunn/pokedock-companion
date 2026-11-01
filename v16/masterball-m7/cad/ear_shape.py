"""Ear profile of the M7 lid (shared by build_m7.py and appearance_gate.py)."""
import m7_params as P

EAR_SHAPE = (1.6, 0.6)      # r = r0 * (1 - (z/H)^a)^b : convex flank, smooth round tip, no joints (photo gumdrop ear)


def ear_profile():
    """Half profile (r, z) of the ear, from the base edge to the tip, plus a 3 mm skirt below the seat."""
    r0, h = P.EAR_BASE_D / 2, P.EAR_H
    a, b = EAR_SHAPE
    pts = []
    for k in range(0, 41):
        z = h * (k / 40) ** 0.8 if k < 40 else h
        r = r0 * max(0.0, 1 - (z / h) ** a) ** b
        pts.append((r, z))
    pts[-1] = (0.0, h)
    return [(0, -3.0), (r0 + 0.6, -3.0)] + pts
