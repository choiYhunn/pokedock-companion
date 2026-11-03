"""Print-ready files for Bambu Studio: every part rotated to its print orientation and dropped on the bed.

usage: python make_print_package.py <cad_out_dir> <print_dir>
Writes <print_dir>/01_fitkit_first/*.stl, <print_dir>/02_final/*.stl, one .3mf per plate (geometry +
orientation only: layer height, walls, supports are set in Bambu Studio per PRINT_SETTINGS_KO.md) and
print_manifest.json (extent, volume, mass estimate, overhang area per part).
"""
import hashlib
import json
import math
import shutil
import os
import sys

import numpy as np
import trimesh

sys.path.insert(0, os.path.dirname(__file__))
import print_orient as PO  # noqa: E402

CAD, OUTD = sys.argv[1:3]
ONLY = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None   # e.g. variant B lid/ears
PLATES = {
    "01_fitkit_first": {     # any PLA colour, same printer / profile as the final parts
        "FK1_display_cradle": ["fit1_display_bezel", "fit1_display_plate"],
        "FK2_hinge_stop": ["fit2_hinge_belt", "fit2_hinge_lid", "fit2_stop_block"],
        "FK3_closing_magnet_joint": ["fit3_joint_belt", "fit3_joint_lower", "fit4_magnet_lid", "fit4_magnet_belt"],
        "FK4_lid_sensor": ["fit6_sensor_belt", "fit6_sensor_lid"],
        "FK5_ear_button": ["fit5_ear_seat_lid", "fit5_ear_right", "fit5_button_patch_lower"],
        "FK6_sound_seat_bracket": ["fit7_speaker_seat_lower", "fit7_sound_bracket"],   # v0.6 speaker + DFR0534
    },
    "02_final": {            # one plate per colour: no AMS needed
        "C1_purple_lid": ["lid_lavender"],
        "C2_ivory_lower_shell": ["lower_shell_ivory"],
        "C3_black_belt_stop": ["belt_black", "stop_block_black"],
        "C4_pink_ears": ["ear_left_pink", "ear_right_pink"],
        "C5_white_button": ["button_white"],
        "C6_inner_cover_lavender": ["inner_cover_lavender"],
        "C6b_lavender_rim_ring_liner": ["rim_ring_lavender", "lid_liner_lavender"],
        "C7_plum_display_button_ring": ["display_bezel_plum", "display_cradle_plum", "button_ring_plum"],
        "C8_internal_sound_bracket": ["sound_bracket_black"],   # hidden inside: any PLA colour
    },
}
manifest = {}


def src(name):
    for sub in ("stl", "fitkit"):
        p = os.path.join(CAD, sub, f"{name}.stl")
        if os.path.exists(p):
            return p
    raise FileNotFoundError(name)


# The final print stays locked until the owner approves the look (appearance/APPROVAL.json, gate APPROVED).
gate_file = os.path.join(os.path.dirname(os.path.abspath(OUTD)), "appearance", "APPEARANCE_GATE.json")
gate = json.load(open(gate_file, encoding="utf8"))["gate"] if os.path.exists(gate_file) else "MISSING"
if gate != "APPROVED":
    PLATES["02_final_LOCKED_until_appearance_approval"] = PLATES.pop("02_final")
if ONLY:
    PLATES = {f: {k: v for k, v in pl.items() if k in ONLY} for f, pl in PLATES.items()}
    PLATES = {f: pl for f, pl in PLATES.items() if pl}
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
manifest["APPEARANCE_GATE"] = gate

# Per-part approval: a final plate stays in 02_final only while every exterior part on it is byte-identical
# to the owner-approved print file (appearance/APPROVAL.json approved_print_sha256). Changed parts move
# the whole plate to 02_final_PENDING_owner_approval (never silently replaced).
appr = json.load(open(os.path.join(os.path.dirname(gate_file), "APPROVAL.json"), encoding="utf8")) if os.path.exists(gate_file) else {}
hashes, internal = appr.get("approved_print_sha256", {}), set(appr.get("internal_parts_no_appearance_approval", []))
pending = {}
final = os.path.join(OUTD, "02_final")
if gate == "APPROVED" and hashes and os.path.isdir(final):
    for plate, names in PLATES.get("02_final", {}).items():
        changed = []
        for nm in names:
            sha = hashlib.sha256(open(os.path.join(final, f"{nm}.stl"), "rb").read()).hexdigest()
            manifest[nm]["sha256"] = sha
            if nm in internal:
                manifest[nm]["appearance"] = "internal (no appearance approval needed)"
            elif hashes.get(nm) == sha:
                manifest[nm]["appearance"] = "approved " + appr.get("date", "")
            else:
                manifest[nm]["appearance"] = "CHANGED since the approved print file: owner approval pending"
                changed.append(nm)
        if changed:
            pending[plate] = changed
    if pending:
        pend = os.path.join(OUTD, "02_final_PENDING_owner_approval")
        os.makedirs(pend, exist_ok=True)
        for plate in pending:
            for f in [f"{plate}.3mf"] + [f"{nm}.stl" for nm in PLATES["02_final"][plate]]:
                shutil.move(os.path.join(final, f), os.path.join(pend, f))
        msg = ["승인 대기: 아래 판의 부품이 의뢰인이 승인한 출력 파일(" + appr.get("approved_commit", "?") + ")과 다릅니다.",
               "출력하지 마세요. 승인 전에는 승인본(git " + appr.get("approved_commit", "?") + " 의 print/02_final)도 새 전자 구성과 맞지 않습니다.", ""]
        for plate, names in pending.items():
            msg.append(f"{plate}: " + ", ".join(names))
        msg += ["", "바뀐 곳 비교: img/v06_appearance_changes_before_after.png, img/render_closed_left_low_speaker.png",
                "승인하면: python appearance/record_approval.py 를 실행해 새 해시를 기록하고 tests/run_m7.sh 를 다시 돌립니다."]
        open(os.path.join(pend, "README_PENDING_KO.txt"), "w", encoding="utf8").write("\n".join(msg) + "\n")
manifest["APPEARANCE_PENDING_PLATES"] = pending
if gate != "APPROVED":
    msg = ["본 출력 잠금: 외관 승인 게이트가 " + gate + " 상태입니다.",
           "appearance/review_sheet.png, img/, appearance/variant_B/ 를 보고 귀 위치(A/B)를 고른 뒤",
           "appearance/APPROVAL.json 에 approved=true, chosen_ear_variant, 이름, 날짜를 적고 tests/run_m7.sh 를 다시 실행하면 잠금이 풀립니다.",
           "이 폴더의 파일은 검토용입니다. 승인 전에는 출력하지 마세요."]
    open(os.path.join(OUTD, "02_final_LOCKED_until_appearance_approval", "README_LOCKED_KO.txt"), "w", encoding="utf8").write("\n".join(msg) + "\n")
json.dump(manifest, open(os.path.join(OUTD, "print_manifest.json"), "w"), indent=1)
bad = [k for k, v in manifest.items() if isinstance(v, dict) and "watertight" in v and (not v["watertight"] or not v["fits_A1mini_180"])]
print("parts not watertight or too big:", bad)
sys.exit(1 if bad else 0)
