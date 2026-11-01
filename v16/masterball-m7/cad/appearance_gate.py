"""Appearance approval gate (independent of the mechanical checks).

usage: python appearance_gate.py <cad_out_dir> <img_dir> <appearance_dir>
1. Measures the CAD proportions that define the look and compares them with targets read off the
   approved concept photo (pixel measurements, ball width 652 px = 138 mm; see TARGETS notes).
2. Lists what cannot match the photo for structural reasons.
3. Builds review_sheet.png from the four CAD renders (open, closed, user eye height, side).
4. Gate status: automated proportions PASS/FAIL **and** the owner's visual approval in
   <appearance_dir>/APPROVAL.json. The final print stays locked until both are true.
A metric PASS is "within the photo tolerance", not "looks right": only the owner approves the look.
"""
import json
import math
import os
import sys

import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
import ear_shape as EP  # noqa: E402
import m7_params as P  # noqa: E402

CAD, IMG, APP = sys.argv[1:4]
os.makedirs(APP, exist_ok=True)
D = 2 * P.R
ld = lambda k: trimesh.load(f"{CAD}/stl/{k}.stl")  # noqa: E731
ear = ld("ear_right_pink")
pod = trimesh.util.concatenate([ld("display_cradle_plum"), ld("display_bezel_plum")])

# tip roundness: circle fitted to the profile near the tip, relative to the base radius
prof = np.array([p for p in EP.ear_profile() if p[1] >= 0])
tip = prof[prof[:, 0] <= 0.45 * P.EAR_BASE_D / 2]
xs = np.concatenate([tip[:, 0], -tip[:, 0]])
ys = np.concatenate([tip[:, 1], tip[:, 1]])
A = np.column_stack([xs, ys, np.ones_like(xs)])
c = np.linalg.lstsq(A, -(xs ** 2 + ys ** 2), rcond=None)[0]
tip_r = math.sqrt(c[0] ** 2 / 4 + c[1] ** 2 / 4 - c[2])

M = {  # name: (CAD value, target, tol, unit, how the target was read from the photo)
    "glass_over_D": (46.0 / D, 0.34, 0.02, "", "photo glass ring ~233 px / ball 652 px (real board: 0.333)"),
    "active_over_D": (36.75 / D, 0.27, 0.02, "", "true size kept (official STEP); photo ~0.27"),
    "bezel_over_D": (2 * P.BEZEL_OR / D, 0.45, 0.04, "", "dark surround around the glass ~62 mm"),
    "pod_width_over_D": (float(pod.bounds[1][0] - pod.bounds[0][0]) / D, 0.51, 0.06, "", "cradle incl. side brackets ~70 mm"),
    "band_height_over_D": (2 * P.BH / D, 0.076, 0.012, "", "dark band ~47 px at the front, perspective-corrected ~10.5 mm"),
    "button_over_D": (P.BTN_D / D, 0.171, 0.02, "", "white button ~112 px"),
    "ring_over_D": (P.BTN_RING_OD / D, 0.246, 0.025, "", "dark ring ~160 px"),
    "ring_top_to_band_top_mm": (P.BH - (P.BTN_Z + P.BTN_RING_OD / 2), 0.0, 1.5, "mm", "ring top meets the band top / rim"),
    "button_proud_mm": (P.BTN_PROUD, 5.0, 1.5, "mm", "button clearly 3D, domed"),
    "ear_base_over_D": (P.EAR_BASE_D / D, 0.20, 0.03, "", "ear base ~125 px on the (smaller-scale) lid"),
    "ear_height_over_base": (P.EAR_H / P.EAR_BASE_D, 0.70, 0.15, "", "ear ~0.6-0.85 of its base (foreshortened)"),
    "ear_tip_radius_over_base_radius": (tip_r / (P.EAR_BASE_D / 2), 0.45, 0.15, "", "round gumdrop tip, not a point"),
    "ear_above_ball_top_mm": (float(ear.bounds[1][2]) - P.R, 4.0, 3.0, "mm", "ears rise above the silhouette"),
    "screen_centre_above_rim_mm": (P.POD_C[2] - P.BH, 11.0, 4.0, "mm", "screen centre clearly above the rim"),
    "screen_tilt_deg": (P.SCREEN_TILT_DEG, 60.0, 6.0, "deg", "photo reads ~60-65 from a low camera; owner spec caps it at 55"),
    "lid_over_lower_height": ((P.R - P.BH) / (P.BH - P.BASE_Z), 1.0, 0.08, "", "two near-equal halves"),
    "lavender_inner_wall_mm": (P.TRAY_LIP_TOP - P.DECK_TOP_Z, 12.0, 4.0, "mm", "lavender interior wall visible when open"),
}
rows, npass = [], 0
for k, (v, t, tol, u, note) in M.items():
    ok = abs(v - t) <= tol
    npass += ok
    rows.append({"metric": k, "cad": round(v, 3), "photo_target": t, "tol": tol, "unit": u, "pass": bool(ok), "how": note})
DEVIATIONS = [
    ("힌지", "사진은 안쪽에 보이는 브래킷 힌지. 그 구조로는 110°가 나오지 않고 화면과 겹침 → 뒷면 바깥 축(앞에서 안 보임)", "구조상 불가"),
    ("바닥", "사진은 완전한 구. 열린 뚜껑에서 넘어지지 않으려면 평면 Ø75 + 발 8개 필요", "구조상 불가"),
    ("띠 윗면", "사진은 띠 위에 밝은 테두리. 뚜껑이 앉는 면이라 검정 띠 윗면(약 7.6 mm)이 보임. 안쪽은 라벤더 테두리로 대체", "부분 일치"),
    ("화면 각도", "사진은 낮은 카메라라 화면이 60–65°처럼 보임. 사용자 지정 50° 유지", "사양 우선"),
    ("귀 위치", "사진(열린 뚜껑)의 귀 위치는 물리적으로 앞-위쪽(고도 약 35°)에 해당해 생성 이미지 특유의 불일치가 있음. 닫힌 모습에서 고양이 귀로 보이도록 고도 58°에 둠", "해석 차이"),
    ("배선", "사진에는 전선과 보드가 보임. 요구사항(배선 숨김)에 따라 모두 덕 아래로", "의도적 차이"),
    ("화면 크기", "사진의 유리 비율 0.34 ≈ 실제 0.333. 사진이 커 보이는 건 카메라가 가깝고 받침대가 크기 때문 → 받침대 Ø62 + 측면 브래킷으로 반영", "일치"),
]
approval_path = os.path.join(APP, "APPROVAL.json")
if not os.path.exists(approval_path):
    json.dump({"approved": False, "chosen_ear_variant": None, "approved_by": None, "date": None,
               "how_to_approve": "Look at review_sheet.png, img/*.png and variant_B/*.png. Choose the ear variant A (on top) or B (photo position), set approved=true with your name/date and commit."},
              open(approval_path, "w", encoding="utf8"), indent=1, ensure_ascii=False)
approval = json.load(open(approval_path, encoding="utf8"))
metrics_ok = npass == len(rows)
chosen = str(approval.get("chosen_ear_variant") or "").upper()
gate = "APPROVED" if (metrics_ok and approval.get("approved") and chosen in ("A", "B")) else ("PENDING_OWNER_VISUAL_APPROVAL" if metrics_ok else "FAIL_METRICS")
out = {"gate": gate, "metrics_pass": f"{npass}/{len(rows)}", "metrics": rows,
       "structural_deviations": [{"item": a, "detail": b, "class": c} for a, b, c in DEVIATIONS],
       "owner_approval": approval, "final_print_unlocked": gate == "APPROVED"}
json.dump(out, open(os.path.join(APP, "APPEARANCE_GATE.json"), "w", encoding="utf8"), indent=1, ensure_ascii=False)

# review sheet -------------------------------------------------------------------------------------
views = [("render_open110_front34.png", "열림 110° (3/4)"), ("render_closed_front34.png", "닫힘 (3/4)"),
         ("render_open110_user_view.png", "사용자 눈높이 (정면 34°)"), ("render_open110_side.png", "측면")]
W, H = 1300, 1100
sheet = Image.new("RGB", (W * 2 // 2, H * 2 // 2 + 520), (250, 249, 246))
font = "C:/Windows/Fonts/malgun.ttf"
ft = ImageFont.truetype(font, 22) if os.path.exists(font) else ImageFont.load_default()
fs = ImageFont.truetype(font, 17) if os.path.exists(font) else ImageFont.load_default()
for i, (f, cap) in enumerate(views):
    im = Image.open(os.path.join(IMG, f)).convert("RGB").resize((W // 2, H // 2))
    x, y = (i % 2) * (W // 2), (i // 2) * (H // 2)
    sheet.paste(im, (x, y))
    ImageDraw.Draw(sheet).text((x + 16, y + 40), cap, fill=(30, 30, 40), font=ft)
dr = ImageDraw.Draw(sheet)
y = H + 10
dr.text((16, y), f"외관 게이트: {gate}  |  사진 비율 지표 {npass}/{len(rows)} 허용범위 안  |  본 출력 잠금 해제: {gate == 'APPROVED'}", fill=(120, 20, 40) if gate != "APPROVED" else (20, 110, 40), font=ft)
y += 36
for r in rows:
    dr.text((16, y), f"{'OK ' if r['pass'] else 'NG '} {r['metric']}: CAD {r['cad']} / 사진 {r['photo_target']} ±{r['tol']} {r['unit']}", fill=(30, 30, 40), font=fs)
    y += 24
    if y > sheet.size[1] - 30:
        break
sheet.save(os.path.join(APP, "review_sheet.png"))
print(json.dumps({"gate": gate, "metrics_pass": out["metrics_pass"]}, ensure_ascii=False))
for r in rows:
    print(("PASS " if r["pass"] else "FAIL ") + f"{r['metric']}: {r['cad']} (target {r['photo_target']} +-{r['tol']})")
sys.exit(0 if metrics_ok else 1)
