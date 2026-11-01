"""Print-ready files for Bambu Studio: every part rotated to its print orientation and dropped on the bed.

usage: python make_print_package.py <cad_out_dir> <print_dir>
Writes <print_dir>/01_fitkit_first/*.stl, <print_dir>/02_final/*.stl, one .3mf per plate (geometry +
orientation only: layer height, walls, supports are set in Bambu Studio per PRINT_SETTINGS_KO.md) and
print_manifest.json (extent, volume, mass estimate, overhang area per part).
"""
import json
import math
import os
import sys

import numpy as np
import trimesh

sys.path.insert(0, os.path.dirname(__file__))
import print_orient as PO  # noqa: E402

CAD, OUTD = sys.argv[1:3]
PLATES = {
    "01_fitkit_first": {     # any PLA colour, same printer / profile as the final parts
        "FK1_display_cradle": ["fit1_display_bezel", "fit1_display_plate"],
        "FK2_hinge_stop": ["fit2_hinge_belt", "fit2_hinge_lid", "fit2_stop_block"],
        "FK3_closing_magnet_joint": ["fit3_joint_belt", "fit3_joint_lower", "fit4_magnet_lid", "fit4_magnet_belt"],
        "FK4_lid_sensor": ["fit6_sensor_belt", "fit6_sensor_lid"],
        "FK5_ear_button": ["fit5_ear_seat_lid", "fit5_ear_right", "fit5_button_patch_lower"],
    },
    "02_final": {            # one plate per colour: no AMS needed
        "C1_purple_lid": ["lid_lavender"],
        "C2_ivory_lower_shell": ["lower_shell_ivory"],
        "C3_black_belt_ring_stop": ["belt_black", "button_ring_black", "stop_block_black"],
        "C4_pink_ears": ["ear_left_pink", "ear_right_pink"],
        "C5_white_button": ["button_white"],
        "C6_inner_cover_lavender": ["deck_lavender", "lid_liner_lavender"],
        "C7_plum_display": ["display_bezel_plum", "display_cradle_plum"],
    },
}
manifest = {}


def src(name):
    for sub in ("stl", "fitkit"):
        p = os.path.join(CAD, sub, f"{name}.stl")
        if os.path.exists(p):
            return p
    raise FileNotFoundError(name)


for folder, plates in PLATES.items():
    os.makedirs(os.path.join(OUTD, folder), exist_ok=True)
    for plate, names in plates.items():
        placed, x = [], 0.0
        for nm in names:
            m = trimesh.load(src(nm), force="mesh")
            m.merge_vertices()
            mo = PO.on_bed(PO.orient(nm, m))
            mo.export(os.path.join(OUTD, folder, f"{nm}.stl"))
            lo, hi = mo.bounds
            ext = hi - lo
            fn, cz = mo.face_normals, mo.triangles_center[:, 2]
            over = (fn[:, 2] < -math.cos(math.radians(45))) & (cz > 0.4)
            pet = False   # all PLA
            manifest[nm] = {"plate": plate, "extent_mm": [round(float(v), 1) for v in ext], "watertight": bool(mo.is_watertight),
                            "volume_cm3": round(float(mo.volume) / 1000, 1),
                            "part_mass_g_100pct": round(float(mo.volume) / 1000 * (1.27 if pet else 1.24), 1),
                            "overhang_gt45_mm2": round(float(mo.area_faces[over].sum()), 0),
                            "fits_A1mini_180": bool(np.all(ext <= 178))}
            p2 = mo.copy()
            p2.apply_translation([x + ext[0] / 2, 0, 0])
            x += ext[0] + 8.0
            placed.append((nm, p2))
        sc = trimesh.Scene()
        for nm, p2 in placed:
            p2.apply_translation([-(x - 8.0) / 2, 0, 0])
            sc.add_geometry(p2, geom_name=nm)
        lo, hi = sc.bounds
        manifest[f"PLATE {plate}"] = {"plate_extent_mm": [round(float(v), 1) for v in (hi - lo)],
                                      "fits_A1mini_180": bool(np.all((hi - lo)[:2] <= 178)),
                                      "fits_256": bool(np.all((hi - lo)[:2] <= 250))}
        sc.export(os.path.join(OUTD, folder, f"{plate}.3mf"))
        print(plate, manifest[f"PLATE {plate}"])
json.dump(manifest, open(os.path.join(OUTD, "print_manifest.json"), "w"), indent=1)
bad = [k for k, v in manifest.items() if not k.startswith("PLATE") and (not v["watertight"] or not v["fits_A1mini_180"])]
print("parts not watertight or too big:", bad)
sys.exit(1 if bad else 0)
