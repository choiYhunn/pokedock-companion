"""Print orientation of every M7 part and fit-kit coupon (shared by verify_m7.py and make_print_package.py).

Each entry maps a part to a rotation that puts its print face on the bed (bed = min z after rotation).
"""
import math

import numpy as np
import trimesh

import m7_params as P

N = np.array([0.0, -math.sin(math.radians(P.SCREEN_TILT_DEG)), math.cos(math.radians(P.SCREEN_TILT_DEG))])
ROT = {
    "lid_lavender": None,               # rim on the bed; inside dome above the liner needs tree support
    "lower_shell_ivory": None,          # flat base on the bed
    "belt_black": None,                 # spigot bottom on the bed; ledge ring needs support (hidden face)
    "lid_liner_lavender": ("x", 180),   # engraved visible face on the bed
    "display_cradle_plum": None,        # foot slab on the bed
    "stop_block_black": None,           # shelf face on the bed, heel sector up
    "rim_ring_lavender": None,          # flat ring
    "inner_cover_lavender": ("x", 180),        # visible top face on the bed (smooth PEI finish)
    "display_bezel_plum": ("normal_down", None),   # front face on the bed
    "button_ring_plum": ("x", 90),     # front face on the bed
    "button_white": ("x", 90),
    "ear_left_pink": ("ear", -1),       # flat base on the bed
    "ear_right_pink": ("ear", 1),
    # fit-kit coupons: same orientation as the part they are cut from
    "fit1_display_bezel": ("normal_down", None), "fit1_display_plate": None,
    "fit2_hinge_belt": None, "fit2_hinge_lid": None, "fit3_joint_belt": None, "fit3_joint_lower": None,
    "fit4_magnet_lid": None, "fit4_magnet_belt": None, "fit5_ear_seat_lid": ("ear", 1),
    "fit6_sensor_belt": None, "fit6_sensor_lid": None, "fit2_stop_block": None,
    "fit5_ear_right": ("ear", 1), "fit5_button_patch_lower": None,
    "sound_bracket_black": ("spk", None),   # ring face (toward the speaker) on the bed, standoffs up
    "fit7_sound_bracket": ("spk", None), "fit7_speaker_seat_lower": None,
}
MATERIAL = {
    "lid_lavender": "PLA matte lavender", "lid_liner_lavender": "PLA matte lavender",
    "ear_left_pink": "PLA matte pink", "ear_right_pink": "PLA matte pink",
    "belt_black": "PLA matte black", "button_ring_plum": "PLA matte black",
    "lower_shell_ivory": "PLA matte ivory", "button_white": "PLA matte white",
    "inner_cover_lavender": "PLA matte lavender (lighter shade ok)", "display_bezel_plum": "PLA matte dark purple",
    "display_cradle_plum": "PLA matte dark purple (PETG optional, not required)", "stop_block_black": "PLA matte black",
    "sound_bracket_black": "PLA any colour (hidden inside)",
}


def orient(name, m):
    m = m.copy()
    r = ROT.get(name)
    if r is not None:
        if r[0] == "x":
            m.apply_transform(trimesh.transformations.rotation_matrix(math.radians(r[1]), [1, 0, 0]))
        elif r[0] == "normal_down":
            m.apply_transform(trimesh.geometry.align_vectors(N, [0, 0, -1]))
        elif r[0] == "spk":
            d = np.array(P.unit(P.SPK_AZ, P.SPK_EL))
            m.apply_transform(trimesh.geometry.align_vectors(d, [0, 0, -1]))
        elif r[0] == "ear":
            d = np.array(P.unit(r[1] * P.EAR_AZ, P.EAR_EL))
            m.apply_transform(trimesh.geometry.align_vectors(d, [0, 0, 1]))
    return m


def on_bed(m):
    """Centre on x/y and drop to z = 0."""
    m = m.copy()
    lo, hi = m.bounds
    m.apply_translation([-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2]])
    return m
