"""M7 interface module (built by a helper; the owner only plugs it in): netlist, placement, drawings.

usage: python interface_module_m7.py <img_dir> <json_out>
Board: 2.54 mm perfboard cut to 12 x 9 holes (~30 x 23 mm), point-to-point insulated wiring underneath.
Owner side: J1 socket (plug onto the board header, pin 1 marked), two screw terminals (buzzer, lid reed).
The netlist is checked against electronics/harness_m7.json and tests/m7_electrical_check.py facts.
"""
import json
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

IMG, OUT = sys.argv[1:3]
os.makedirs(IMG, exist_ok=True)
FONT = "Malgun Gothic"
plt.rcParams["font.family"] = FONT
plt.rcParams["axes.unicode_minus"] = False

PARTS = {   # ref: (description, MPN, placement (col,row) of each pin on the 12 x 9 grid, pin names)
    "TB1": ("부저 단자 (나사식 2P, 5.00 mm)", "Phoenix Contact 1935161", [(1, 0), (3, 0)], ["BZ+", "BZ-"]),
    "TB2": ("뚜껑 리드 센서 단자 (나사식 2P)", "Phoenix Contact 1935161", [(7, 0), (9, 0)], ["LID", "GND"]),
    "D1": ("플라이백 다이오드 (띠 = 캐소드 = +5 V 쪽)", "onsemi 1N4148", [(1, 2), (4, 2)], ["K", "A"]),
    "Q1": ("N-MOSFET on SOT-23 브레이크아웃 (실크 1=G 2=S 3=D)", "AOS AO3400A + Adafruit 1230", [(5, 4), (6, 4), (7, 4)], ["G", "S", "D"]),
    "R1": ("게이트 저항 100 Ω", "Yageo CFR-25JT-52-100R", [(2, 6), (5, 6)], ["1", "2"]),
    "R2": ("게이트 풀다운 100 kΩ", "Yageo CFR-25JT-52-100K", [(6, 6), (9, 6)], ["1", "2"]),
    "F1": ("PTC 0.75 A (극성 없음)", "Bourns MF-R075", [(0, 4), (2, 4)], ["1", "2"]),
    "P1": ("배선 패드: J1 소켓으로 가는 4가닥", "-", [(1, 8), (4, 8), (7, 8), (10, 8)], ["+5V_IN", "GND", "IO16", "LID_IN"]),
}
NETS = {
    "+5V_IN (J1-4)": ["P1.+5V_IN", "F1.1"],
    "+5V": ["F1.2", "TB1.BZ+", "D1.K"],
    "BZ_DRAIN": ["Q1.D", "TB1.BZ-", "D1.A"],
    "GATE": ["R1.2", "Q1.G", "R2.1"],
    "IO16 (J1-8)": ["P1.IO16", "R1.1"],
    "GND (J1-6)": ["P1.GND", "Q1.S", "R2.2", "TB2.GND"],
    "LID / IO17 (J1-10)": ["P1.LID_IN", "TB2.LID"],
}
PIGTAIL = [  # module pad -> J1 socket pin (Harwin M50-3000745, 2x7 1.27 mm female), wire, length
    ("+5V_IN", "J1-4", "빨강 28 AWG", 160), ("GND", "J1-6", "검정 28 AWG", 160),
    ("IO16", "J1-8", "노랑 28 AWG", 160), ("LID_IN", "J1-10", "흰색 28 AWG", 160)]
FIELD = [  # owner-side wires into the screw terminals (prepared by the helper: stripped 5 mm, tinned)
    ("WT-1205 부저 +/− 리드 (도우미가 부저에 납땜, 수축튜브)", "TB1", 140),
    ("Littelfuse 59155 리드 2가닥 (리드선 그대로, 끝 5 mm 피복 벗김)", "TB2", 220)]

# --- consistency with the harness: the same J1 pins / nets --------------------------------------
H = json.load(open(os.path.join(os.path.dirname(__file__), "harness_m7.json"), encoding="utf8"))
hp = {w["to_pin"]: w["net"] for w in H["harness"] if w.get("to_pin", "").startswith("J1-")}
want = {"J1-4": "USB_5V", "J1-6": "GND", "J1-8": "IO16", "J1-10": "IO17"}
ok_harness = all(hp.get(k) == v for k, v in want.items())
pads = {p for n in NETS.values() for p in n}
ok_parts = all(any(p.startswith(r + ".") for p in pads) for r in PARTS)
ok_ptc = "F1.1" in NETS["+5V_IN (J1-4)"] and "TB1.BZ+" in NETS["+5V"]
ok_diode = "D1.K" in NETS["+5V"] and "D1.A" in NETS["BZ_DRAIN"]
ok_gate = "R2.1" in NETS["GATE"] and "R2.2" in NETS["GND (J1-6)"]
checks = {"harness_pins": ok_harness, "every_part_connected": ok_parts, "ptc_in_5v_path": ok_ptc,
          "diode_cathode_to_5v": ok_diode, "gate_pulldown": ok_gate}

# --- schematic -----------------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 7), dpi=130)
ax.set_xlim(0, 120)
ax.set_ylim(0, 70)
ax.axis("off")


def blk(x, y, w, h, t, fc="#f3eefc"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4", fc=fc, ec="#4d3b6e"))
    ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=9)


def line(pts, c="#222", lw=1.6):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=c, lw=lw)


blk(2, 28, 18, 26, "Waveshare\nSKU 30106\nJ1 (2×7, 1.27)\n\n4: USB_5V\n6: GND\n8: IO16\n10: IO17", "#e8e4f0")
blk(24, 30, 12, 22, "J1 소켓\nHarwin\nM50-3000745\n(14핀 중\n4핀 사용)", "#fff7e0")
for i, (lab, y) in enumerate((("+5V_IN", 50), ("GND", 44), ("IO16", 38), ("IO17", 32))):
    line([(36.5, y), (46, y)], c=("#d62728", "#222", "#c9a400", "#888")[i])
    ax.text(38, y + 0.8, lab, fontsize=8)
blk(46, 47, 10, 6, "F1 PTC\nMF-R075")
line([(56.5, 50), (66, 50), (66, 58)], c="#d62728")
blk(60, 58, 14, 8, "TB1 부저 단자\nBZ+  |  BZ-")
blk(80, 58, 12, 8, "WT-1205\n부저", "#e8f3ea")
line([(74.5, 62), (79.5, 62)])
blk(62, 36, 10, 8, "D1 1N4148\nK→+5V")
line([(66, 50), (66, 44.5)], c="#d62728")
blk(84, 30, 12, 10, "Q1 AO3400A\nD  G  S")
line([(72, 62), (72, 52), (88, 52), (88, 40.5)], c="#1f77b4")
ax.text(76, 53, "BZ_DRAIN", fontsize=8, color="#1f77b4")
line([(72.5, 40), (88, 40)], c="#1f77b4")
blk(56, 20, 10, 6, "R1 100 Ω")
line([(46, 38), (50, 38), (50, 23), (55.5, 23)], c="#c9a400")
line([(66.5, 23), (90, 23), (90, 29.5)], c="#7f3fbf")
blk(74, 10, 10, 6, "R2 100 kΩ")
line([(79, 23), (79, 16.5)], c="#7f3fbf")
line([(79, 9.5), (79, 6), (100, 6)], c="#222")
line([(94, 29.5), (94, 6)], c="#222")
line([(46, 44), (46, 6), (79, 6)], c="#222")
blk(100, 10, 16, 8, "TB2 리드 단자\nLID | GND")
line([(46, 32), (40, 32), (40, 2), (104, 2), (104, 9.5)], c="#888")
line([(112, 9.5), (112, 6), (100, 6)], c="#222")
blk(100, 22, 16, 8, "Littelfuse 59155\n리드 센서 (NO)", "#e8f3ea")
line([(108, 21.5), (108, 18.5)])
ax.set_title("M7 인터페이스 모듈 회로도 — 부저 구동(M6 회로 그대로) + 뚜껑 센서 입력. 도우미가 납땜, 사용자는 꽂고 조이기만", fontsize=11)
fig.tight_layout()
fig.savefig(os.path.join(IMG, "module_schematic.png"))
plt.close(fig)

# --- placement on the 12 x 9 perfboard -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 7.5), dpi=130)
for c in range(12):
    for r in range(9):
        ax.plot(c, r, "o", ms=4, color="#c9b98f")
ax.add_patch(Rectangle((-0.6, -0.6), 12.2, 9.2, fill=False, ec="#8a6d2f", lw=2))
cols = {"TB1": "#2ca02c", "TB2": "#2ca02c", "D1": "#444", "Q1": "#1f77b4", "R1": "#c9a400", "R2": "#7f3fbf",
        "F1": "#d62728", "P1": "#555"}
for ref, (desc, mpn, pins, names) in PARTS.items():
    xs = [p[0] for p in pins]
    ys = [p[1] for p in pins]
    ax.add_patch(Rectangle((min(xs) - 0.4, min(ys) - 0.4), max(xs) - min(xs) + 0.8, max(ys) - min(ys) + 0.8,
                           fill=False, ec=cols[ref], lw=2))
    for (x, y), nm in zip(pins, names):
        ax.plot(x, y, "s", ms=7, color=cols[ref])
        ax.text(x, y - 0.55 if ref != "P1" else y + 0.45, nm, ha="center", fontsize=7, color=cols[ref])
    ax.text(min(xs) - 0.4, max(ys) + 0.55 if ref != "P1" else min(ys) - 0.9, ref, fontsize=9, color=cols[ref], weight="bold")
ax.invert_yaxis()
ax.set_aspect("equal")
ax.set_xticks(range(12))
ax.set_yticks(range(9))
ax.set_title("부품 배치 (위에서 본 면, 2.54 mm 격자 12×9, 약 30×23 mm)\n배선은 아래면 피복선 점대점: 연결은 회로도·넷 표 기준, 단자는 위쪽 가장자리, 피그테일은 아래쪽", fontsize=10)
fig.tight_layout()
fig.savefig(os.path.join(IMG, "module_perfboard_layout.png"))
plt.close(fig)

out = {"board": "2.54 mm perfboard 12 x 9 holes (~30 x 23 mm), height <= 12 mm incl. terminals (CAD envelope 30 x 24 x 12)",
       "parts": {k: {"desc": v[0], "mpn": v[1], "pins": dict(zip(v[3], v[2]))} for k, v in PARTS.items()},
       "nets": NETS, "pigtail_to_J1": [{"pad": a, "j1_pin": b, "wire": c, "len_mm": d} for a, b, c, d in PIGTAIL],
       "owner_side_terminals": [{"what": a, "terminal": b, "len_mm": c} for a, b, c in FIELD],
       "checks": checks}
json.dump(out, open(OUT, "w", encoding="utf8"), indent=1, ensure_ascii=False)
print(json.dumps(checks))
sys.exit(0 if all(checks.values()) else 1)
