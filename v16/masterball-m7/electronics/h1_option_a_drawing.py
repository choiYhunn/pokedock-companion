"""H1 option A drawing: Adafruit 4424 with its PH end re-pinned for the DFR0534 (no solder, no crimp).

usage: python h1_option_a_drawing.py <img_dir>
Writes <img_dir>/h1_option_a_wiring.png and checks the mapping in harness_m7.json:
GND -> '-', 3V3 -> '+', GPIO44 -> 'R', 'T' cavity empty, GPIO43 contact out of the housing and capped.
Positions on the module side follow the silk letters of the official DFRobot dimension drawing V1.0
(Gravity socket on the left short edge, top to bottom: T, R, -, +; the VCC/GND/RX/TX/BUSY holes along the
top edge). Pin-1 numbers of J10 and of the Gravity socket are not published, so the drawing never uses
them: the SH end is identified by measurement (docs/07 S3a) and the PH end by the module silk.
"""
import json
import os
import pathlib
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
IMG = sys.argv[1]
h = json.loads((HERE / "harness_m7.json").read_text(encoding="utf8"))
H1 = next(x for x in h["harnesses"] if x["id"] == "H1")
A = H1["option_a_preferred"]
fails = []


def rule(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        fails.append(name)


rule("option A part is Adafruit 4424", A["part"]["mpn"] == "4424")
rework = A["rework"]
rule("mapping GND -> '-', 3V3 -> '+', GPIO44 -> 'R'", "GND -> '-'" in rework and "3V3 -> '+'" in rework and "GPIO44 -> 'R'" in rework)
rule("'T' cavity stays empty and GPIO43 stays out of the housing", "'T' cavity stays empty" in rework and "GPIO43" in rework)
rule("pre-power checks listed (reverse 3V3/GND, adjacent shorts)", any("reverse" in s for s in A["pre_power_checks"])
     and any("adjacent" in s for s in A["pre_power_checks"]))

if os.path.exists("C:/Windows/Fonts/malgun.ttf"):
    matplotlib.rcParams["font.family"] = "Malgun Gothic"
    matplotlib.rcParams["axes.unicode_minus"] = False
fig, ax = plt.subplots(figsize=(15, 9.5), dpi=120)
ax.set_xlim(0, 150)
ax.set_ylim(0, 95)
ax.axis("off")

# DFR0534 (official drawing orientation: Gravity socket on the left edge)
mx, my = 98, 32
ax.add_patch(FancyBboxPatch((mx, my), 44, 34, boxstyle="round,pad=0.8", fc="#1d3f8f", ec="#111"))
ax.text(mx + 22, my + 36.5, "DFR0534 (윗면, DFRobot 치수도 V1.0 방향)", ha="center", fontsize=10, weight="bold")
for i, t in enumerate(["VCC", "GND", "RX", "TX", "BUSY"]):
    ax.add_patch(plt.Circle((mx + 10 + i * 6, my + 30), 1.4, fc="#d9b44a", ec="#222"))
    ax.text(mx + 10 + i * 6, my + 26.5, t, ha="center", fontsize=7, color="w")
ax.text(mx + 22, my + 2.2, "아랫줄: ONE DACR DACL SP- SP+ (스피커는 H3)", ha="center", fontsize=7.5, color="w")
silk = ["T", "R", "-", "+"]
ys = [my + 23, my + 18, my + 13, my + 8]
ax.add_patch(Rectangle((mx - 1, my + 5), 6, 21, fc="#e8e8e8", ec="#333"))
for t, y in zip(silk, ys):
    ax.text(mx + 7.5, y, t, fontsize=12, weight="bold", color="w", va="center")
ax.text(mx + 2, my + 27.5, "Gravity\n소켓", ha="center", fontsize=7.5, color="w")

# PH plug (re-pinned) mating the socket
px = mx - 10
ax.add_patch(Rectangle((px, my + 5), 8.5, 21, fc="#f5f5f5", ec="#333", lw=1.5))
ax.text(px + 4.2, my + 3, "4424 PH 플러그\n(재배열 후)", ha="center", va="top", fontsize=8)
wires = {"T": ("비움 (접점 없음)", "#bbbbbb"), "R": ("GPIO44 = J10-1", "#e8a317"),
         "-": ("GND = J10-4", "#222222"), "+": ("3V3 = J10-3", "#d62728")}
for t, y in zip(silk, ys):
    lab, col = wires[t]
    if t == "T":
        ax.text(px + 4.2, y, "X", ha="center", va="center", fontsize=11, color="#999")
        continue
    ax.plot([px - 40, px + 3], [y, y], color=col, lw=3.2)
    ax.text(px - 40, y + 1.2, lab, fontsize=9, color=col if col != "#222222" else "#000")

# SH end at J10 (unchanged plug, identified by measurement)
sx = 14
ax.add_patch(FancyBboxPatch((sx - 10, 30), 22, 38, boxstyle="round,pad=0.8", fc="#ece6f8", ec="#333"))
ax.text(sx + 1, 70.5, "보드 J10 (USB-C 바로 옆, 옆으로 꽂음)", ha="center", fontsize=10, weight="bold")
ax.add_patch(Rectangle((sx + 9, 38), 5, 22, fc="#f5f5f5", ec="#333", lw=1.5))
ax.text(sx + 11.5, 36.5, "4424 SH 플러그\n(손대지 않음)", ha="center", va="top", fontsize=8)
for (lab, col, y) in (("J10-1 GPIO44", "#e8a317", 56), ("J10-2 GPIO43 (ROM 로그)", "#7f7f7f", 51),
                      ("J10-3 3V3", "#d62728", 46), ("J10-4 GND", "#222222", 41)):
    ax.text(sx - 8.5, y, lab, fontsize=8, va="center")
    ax.plot([sx + 14, sx + 24], [y, y], color=col, lw=3.2)
# route lines from SH side to PH side
for y0, y1, col in ((56, ys[1], "#e8a317"), (46, ys[3], "#d62728"), (41, ys[2], "#222222")):
    ax.plot([sx + 24, px - 40], [y0, y1], color=col, lw=2.2, ls="--")
# GPIO43 capped and folded back
ax.plot([sx + 14, sx + 19, sx + 19, sx + 27], [51, 51, 76, 76], color="#7f7f7f", lw=3.2)
ax.add_patch(Rectangle((sx + 27, 74.6), 9, 2.8, fc="#555", ec="#000"))
ax.text(sx + 38, 76, "GPIO43 선 (PH 쪽 끝): 접점을 하우징에서 빼서 Ø1.5 수축튜브로 끝 5 mm 넘게 감쌈 →\n"
        "케이블 쪽으로 접어 Ø3 수축튜브(또는 타이)로 함께 고정. 하우징의 'T' 자리는 비움", fontsize=8, va="center")
# strain relief
for x, lab in ((px - 14, "타이 ①: PH 플러그 뒤 20 mm,\n하단 쉘 마운트"), (sx + 30, "타이 ②: J10에서 40 mm,\n덱 구멍 아래")):
    ax.add_patch(Rectangle((x - 1.2, 38), 2.4, 22, fc="none", ec="#2ca02c", lw=2, ls=":"))
    ax.text(x, 33, lab, ha="center", va="top", fontsize=8, color="#2ca02c")

checks = ("전원 넣기 전·후 확인 (멀티미터)\n"
          "P1 케이블만: 4선 끝-끝 도통 OK, PH 접점끼리 6쌍 모두 개방(인접 단락 없음)\n"
          "P2 SH만 J10에 꽂고 전원 ON (PH는 모듈에서 분리): '+' 자리 - '-' 자리 = +3.25~3.35 V\n"
          "    → 음수(-3.3 V)면 3V3/GND 역결선: 즉시 전원 OFF, 재배열 다시.  'R' 자리 3.3 V, 배선 시험 중 0 V\n"
          "P3 전원 OFF, 모듈에 꽂음: 모듈 VCC-GND 패드 100 Ω 이상 → 전원 ON: VCC +3.3 V, TX 패드는 어디에도 연결 없음")
ax.text(4, 2, checks, fontsize=8.6, va="bottom", family="Malgun Gothic",
        bbox=dict(boxstyle="round", fc="#fff8e1", ec="#d4a017"))
ax.set_title("H1 A안: Adafruit 4424 PH 접점 재배열 (납땜 0, 압착 0) — 모듈 실크 글자 기준 최종 위치", fontsize=12.5)
fig.tight_layout()
os.makedirs(IMG, exist_ok=True)
fig.savefig(os.path.join(IMG, "h1_option_a_wiring.png"))
plt.close(fig)
print(f"{'FAIL' if fails else 'PASS'}: H1 option A drawing written ({len(fails)} rule failures)")
sys.exit(1 if fails else 0)
