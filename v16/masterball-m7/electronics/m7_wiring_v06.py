"""M7 v0.6 wiring drawing and pin tables, generated from electronics/harness_m7.json (single source).

usage: python m7_wiring_v06.py <img_dir> <pinmap_md>
Writes <img_dir>/m7_wiring_v06.png (block diagram: board connectors, the three harnesses, module,
speaker, reed) and <pinmap_md> (pin tables in Korean). Also re-checks the harness for the rules the
assembly relies on (crossed TX->RX, no 5 V on the module, nothing on J10-2, H1 solder-free).
"""
import json
import os
import pathlib
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
IMG, MD = sys.argv[1:3]
h = json.loads((HERE / "harness_m7.json").read_text(encoding="utf8"))
H = {x["id"]: x for x in h["harnesses"]}
fails = []


def rule(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        fails.append(name)


j = {r["j10_pin"]: r for r in H["H1"]["joints"] if r["j10_pin"]}
rule("H1 crossed: GPIO44 (our TX) -> module R", j[1]["module_pin"] == "R")
rule("H1 module powered from 3V3, never 5 V", j[3]["net"] == "3V3" and "5V" not in json.dumps(H["H1"]))
rule("H1 leaves J10-2 (GPIO43) open", j[2]["module_pin"] is None)
rule("H1 needs no solder", "no solder" in H["H1"]["build"])
rule("H2 + H3 = 4 helper solder joints in total", len(H["H2"]["joints"]) + len(H["H3"]["joints"]) == 4)

if os.path.exists("C:/Windows/Fonts/malgun.ttf"):
    matplotlib.rcParams["font.family"] = "Malgun Gothic"
    matplotlib.rcParams["axes.unicode_minus"] = False
fig, ax = plt.subplots(figsize=(15, 9), dpi=120)
ax.set_xlim(0, 150)
ax.set_ylim(0, 90)
ax.axis("off")


def blk(x, y, w, hh, title, lines, fc):
    ax.add_patch(FancyBboxPatch((x, y), w, hh, boxstyle="round,pad=0.6", fc=fc, ec="#333", lw=1.2))
    ax.text(x + w / 2, y + hh - 2.2, title, ha="center", va="top", fontsize=11, weight="bold")
    for i, t in enumerate(lines):
        ax.text(x + 1.5, y + hh - 6.5 - i * 3.4, t, ha="left", va="top", fontsize=8.6, family="Malgun Gothic")


blk(2, 44, 34, 42, "Waveshare ESP32-S3-Touch-AMOLED-1.43", [
    "J10 (SH1.0 4핀, USB-C 옆)", "  1 RXD = GPIO44 → 소리 TX", "  2 TXD = GPIO43 (부팅 로그) (비움)",
    "  3 3V3 (MP1605 2 A)", "  4 GND", "", "J1 (1.27 mm 2×7, 뒷면)", "  6 GND", "  10 IO17 (뚜껑, 내부 풀업)",
    "  1·3·4·8 사용 안 함", "", "J4 USB-C → 4432 → 4218 → 뒤 포트"], "#ece6f8")
blk(46, 60, 30, 24, "H1 소리 케이블 (납땜 없음)", [
    "Adafruit 4397: SH 4핀 → 암 소켓 4", "Adafruit 3955: PH 4핀 → 수 핀 4", "", "J10-1 ─ R    J10-3 ─ +",
    "J10-4 ─ -    J10-2 (비움)   T (비움)", "색이 아니라 멀티미터로 확인"], "#fde8e8")
blk(86, 56, 30, 28, "DFRobot DFR0534", [
    "Gravity (PH2.0 4핀): T R - +", "  R ← GPIO44 (9600 8N1)", "  + ← 3V3,  - ← GND", "  T 연결 안 함",
    "SP+ / SP- 패드 (H3)", "8 MB, MP3/WAV, 볼륨 0–30", "사운드 브래킷에 M3 PT 2개"], "#e3ecfb")
blk(124, 62, 24, 20, "스피커", ["PUI AS02808MR-LW152-R", "Ø28 × 5.5, 8 Ω", "1 W (최대 1.5 W)", "리드 152 mm",
                               "왼쪽 아래 벽 + 그릴"], "#eaeaea")
blk(46, 20, 30, 26, "H2 뚜껑 센서 리드 (도우미 2점)", [
    "Littelfuse 59155-1-S-02-A", "  리드 300 mm, 26 AWG", "Harwin M50-3000745 (2×7 소켓)", "  10번 ← 리드 A (IO17)",
    "  6번 ← 리드 B (GND)", "  1번 모서리 흰 점"], "#e6f4ea")
blk(86, 22, 30, 22, "뚜껑 쪽", ["Littelfuse 57155-000 자석", "닫힘 간극 1.7 mm", "작동 2.0–4.2 mm (S)", "닫힘 LOW / 열림 HIGH"], "#f6f1df")
blk(124, 30, 24, 22, "H3 스피커 리드 (도우미 2점)", ["스피커 + → SP+", "스피커 - → SP-", "열수축 + 브래킷 슬롯"], "#eaeaea")
for (x0, y0, x1, y1, c) in ((36, 76, 46, 74, "#d62728"), (76, 72, 86, 72, "#d62728"), (116, 68, 124, 70, "#2ca02c"),
                            (36, 56, 46, 36, "#1f77b4"), (76, 33, 86, 33, "#1f77b4"), (116, 60, 124, 46, "#2ca02c")):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="-", color=c, lw=2.4))
ax.text(75, 4, "전원: 보드 USB-C(J4)만 사용. 5 V를 따로 빼지 않음(J1-4 미사용) → PTC 불필요. 소리 모듈은 3V3 레일(MP1605, 2 A)에서 전원.\n"
               "사용자는 납땜하지 않음: H1은 꽂고 잇기만, H2·H3(납땜 4점)은 도우미/학교/외주. 모든 연결은 전원을 뺀 상태에서.",
        ha="center", fontsize=9.5)
ax.set_title("PokéDock M7 v0.6 배선도 — 하네스 3개 (harness_m7.json에서 생성)", fontsize=13)
fig.tight_layout()
os.makedirs(IMG, exist_ok=True)
fig.savefig(os.path.join(IMG, "m7_wiring_v06.png"))
plt.close(fig)

md = ["# M7 v0.6 핀맵 (자동 생성: electronics/m7_wiring_v06.py ← harness_m7.json)", "",
      "공식 회로도 대조는 `tests/m7_electrical_check.py`가 합니다. 이 표를 손으로 고치지 말고 JSON을 고친 뒤 다시 생성합니다.", "",
      "## 보드 커넥터", "", "| 커넥터 | 핀 | 신호 | M7 사용 |", "|---|---|---|---|"]
for k, v in h["board_connectors"]["J10"]["pins"].items():
    md.append(f"| J10 | {k} | {v} | {'예' if k != '2' else '아니오 (비움)'} |")
for k, v in h["board_connectors"]["J1"]["pins_used"].items():
    md.append(f"| J1 | {k} | {v} | 예 |")
for k, v in h["board_connectors"]["J1"]["pins_not_used"].items():
    md.append(f"| J1 | {k} | {v} | 아니오 |")
md += ["", "## 하네스", ""]
for x in h["harnesses"]:
    md.append(f"### {x['id']} {x['name']}")
    md.append(f"- 제작: {x['build']}")
    md.append("- 부품: " + "; ".join(f"{p['mfr']} {p['mpn']}" + (f" ({p['what']})" if p.get("what") else "") for p in x["parts"]))
    for r in x.get("joints", []):
        md.append("- 연결: " + ", ".join(f"{k}={v}" for k, v in r.items()))
    for key in ("identify", "strain_relief", "reverse_risk", "length_mm"):
        if key in x:
            md.append(f"- {key}: {x[key]}")
    md.append("")
md += ["## 보호", "", h["protection_note"], "", "## 배선 경로", "", h["routing"], ""]
pathlib.Path(MD).write_text("\n".join(md), encoding="utf8")
print(f"{'FAIL' if fails else 'PASS'}: wiring drawing + pin map written ({len(fails)} rule failures)")
sys.exit(1 if fails else 0)
