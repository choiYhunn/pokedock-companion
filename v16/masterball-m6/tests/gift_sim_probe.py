"""Gift-content probe: drives ui/M6_Device_Simulator.html with a PDK pack and checks the whole
placeholder -> character flow, every partner, every stage (home / focus / alarm / sleep), overlays,
the private-message slot, circle clipping, text overlap and the browser frame rate.

usage: python gift_sim_probe.py <out_dir> [pack.bin] [message_slot.bin] [--private]
Without a pack it builds the public TEST pack (original geometric shapes). With --private the
screenshots contain the owner's private artwork: keep that out_dir outside the repository.
"""
import base64
import json
import math
import pathlib
import subprocess
import sys

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
SIM = (HERE.parent / "ui" / "M6_Device_Simulator.html").as_uri()
args = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = pathlib.Path(args[0])
OUT.mkdir(parents=True, exist_ok=True)
PRIVATE = "--private" in sys.argv
if len(args) >= 2:
    pack = pathlib.Path(args[1]).read_bytes()
    msg = pathlib.Path(args[2]).read_bytes() if len(args) >= 3 else None
else:
    subprocess.run([sys.executable, "-X", "utf8", str(HERE / "make_test_pack.py"), str(OUT)], check=True)
    pack = (OUT / "test_pack.bin").read_bytes()
    msg = (OUT / "test_message_slot.bin").read_bytes()
PX_MM = 36.75 / 466
res = {"checks": {}, "fail": [], "private": PRIVATE}


def check(name, cond, detail=""):
    res["checks"][name] = bool(cond)
    if not cond:
        res["fail"].append(f"{name} {detail}")


RECT_JS = """() => { const d = document.getElementById('dev').getBoundingClientRect(), c = document.getElementById('spr');
  if (!c || c.offsetParent === null) return null; const r = c.getBoundingClientRect();
  const cx = d.left + d.width / 2, cy = d.top + d.height / 2, R = d.width / 2;
  const far = Math.max(...[[r.left, r.top], [r.right, r.top], [r.left, r.bottom], [r.right, r.bottom]].map(([x, y]) => Math.hypot(x - cx, y - cy)));
  const txt = [...document.querySelectorAll('#dev .lbl, #dev .pill, #dev .unit')].filter(e => e.offsetParent !== null && e.textContent.trim())
    .map(e => { const b = e.getBoundingClientRect(); return {t: e.textContent.trim(), top: b.top - r.top, overlap: !(b.bottom <= r.top || b.top >= r.bottom || b.right <= r.left || b.left >= r.right)}; });
  return {x: r.left - cx, y: r.top - cy, w: r.width, h: r.height, overshoot: far - R, stage: +c.dataset.stage, anim: +c.dataset.anim, zoom: +c.dataset.zoom,
          ov: (document.getElementById('ov') || {}).textContent || '', text: txt}; }"""

with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge")
    pg = b.new_page(viewport={"width": 1200, "height": 900})
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(SIM)
    pg.wait_for_timeout(1200)
    E = lambda js: pg.evaluate(js)  # noqa: E731

    def shot(name):
        pg.locator("#dev").screenshot(path=str(OUT / f"gift_{name}.png"))

    def spr():
        pg.wait_for_timeout(120)
        return E(RECT_JS)

    # 1. no pack: neutral placeholder, no partner canvas
    E("PD.S.trusted=true; PD.S.utcOffsetMs = Date.UTC(2026,10,1,0,20,0) - Date.now(); PD.render()")  # 09:20 KST
    check("no pack: placeholder text", "이미지 필요" in pg.inner_text("#dev"))
    check("no pack: no partner canvas", spr() is None)
    shot("00_no_pack_placeholder")
    # 2. load pack -> character replaces the placeholder
    ok = E(f"PD.loadPack('{base64.b64encode(pack).decode()}')")
    check("pack parsed", ok)
    r = spr()
    check("pack: partner drawn", r is not None)
    check("pack: placeholder gone", "이미지 필요" not in pg.inner_text("#dev"))
    shot("01_home_gengar")
    # 3. every partner at home: crisp integer zoom, inside the circle, never over the clock
    sizes = {}
    for _ in range(8):
        pg.wait_for_timeout(1500)  # let the greet finish
        r = spr()
        dex = E("PD.S.partner")
        sizes[dex] = r
        check(f"home {dex}: inside circle", r and r["overshoot"] <= -3, json.dumps(r))
        check(f"home {dex}: integer zoom", r and r["zoom"] % 256 == 0, json.dumps(r and r["zoom"]))
        check(f"home {dex}: not over the clock", r and not any(t["overlap"] and ":" in t["t"] for t in r["text"]), json.dumps(r and r["text"]))
        if not PRIVATE or dex == 94:
            shot(f"02_home_{dex}")
        E("PD.menuAct(3,false)")
    check("back to Gengar after 8 partners", E("PD.S.partner") == 94)
    pg.wait_for_timeout(1500)
    # 4. touch -> heart; 5 taps -> egg + private message slot
    E("PD.tap()")
    r = spr()
    check("tap plays touch", r and r["anim"] == 5, json.dumps(r))
    check("touch shows a heart", r and r["ov"] == "♥", json.dumps(r and r["ov"]))
    shot("03_touch_heart")
    pg.wait_for_timeout(3200)  # outside the 3 s tap window of the first tap
    if msg:
        check("message slot accepted", E(f"PD.loadMessageSlot('{base64.b64encode(msg).decode()}')"))
    E("for (let i = 0; i < 5; i++) PD.tap()")
    r = spr()
    check("5 taps: egg dance", r and r["anim"] == 9, json.dumps(r))
    if msg and not PRIVATE:
        check("5 taps: private message from the slot", "테스트 메시지" in pg.inner_text("#dev"))
    shot("04_egg_message")
    E("PD.S.msgUntil=0; PD.render()")
    pg.wait_for_timeout(2700)
    # 5. focus: cheering partner below the minutes label
    E("PD.longPress()")
    pg.wait_for_timeout(300)
    r = spr()
    check("focus: cheer loop on the focus stage", r and r["stage"] == 1 and r["anim"] == 6, json.dumps(r))
    check("focus: inside circle", r and r["overshoot"] <= -3, json.dumps(r))
    check("focus: never over the minutes or the label", r and not any(t["overlap"] for t in r["text"]), json.dumps(r and r["text"]))
    shot("05_focus_cheer")
    E("PD.advance(25*60000+1000)")
    r = spr()
    check("focus complete: celebrate", r and r["anim"] == 7, json.dumps(r))
    shot("06_celebrate")
    E("PD.tap()")
    pg.wait_for_timeout(2000)
    # 6. alarm: the partner takes the title's place
    E("PD.S.alarm={en:true,min:(PD.absMin()+1)%1440}; PD.S.armed=PD.absMin(); PD.render()")
    E("PD.advance(61000)")
    pg.wait_for_timeout(300)
    r = spr()
    check("alarm rings", E("PD.S.ringing"))
    check("alarm: partner on the alarm stage", r and r["stage"] == 2 and r["anim"] == 8, json.dumps(r))
    check("alarm: title replaced by the partner", "일어날 시간" not in pg.inner_text("#dev"))
    check("alarm: partner never over the time or hint", r and not any(t["overlap"] for t in r["text"]), json.dumps(r and r["text"]))
    check("alarm: inside circle", r and r["overshoot"] <= -3, json.dumps(r))
    shot("07_alarm")
    E("PD.longPress()")
    # 7. night: asleep after a minute without touch (per-mood sleep clip when the pack has one)
    E("PD.S.utcOffsetMs += (23*60+30)*60000 - (((PD.absMin()%1440)+1440)%1440)*60000; PD.S.lastTouch=PD.S.mono; PD.render()")
    E("PD.advance(61000)")
    pg.wait_for_timeout(300)
    r = spr()
    check("night idle: sleeping", r and r["anim"] == 1, json.dumps(r))
    check("sleep shows Zzz", r and r["ov"] == "Zzz", json.dumps(r and r["ov"]))
    shot("08_sleep")
    E("PD.tap()")
    pg.wait_for_timeout(300)
    r = spr()
    check("touch wakes the sleeping partner (greet)", r and r["anim"] == 2, json.dumps(r))
    # 8. browser frame rate while animating (desktop; NOT a device measurement)
    pg.wait_for_timeout(2500)
    res["browser_fps"] = round(E("PD.S.perf.fps"), 1)
    res["browser_decode_ms_avg"] = round(E("PD.S.perf.decodeMs / Math.max(1, PD.S.perf.decodes)"), 3)
    check("browser draws >= 30 fps", res["browser_fps"] >= 30, str(res["browser_fps"]))
    res["home_rects"] = sizes
    res["page_errors"] = errors
    check("no JS errors", not errors, str(errors))
    b.close()

res["verdict"] = "PASS" if not res["fail"] else "FAIL"
(OUT / "gift_sim_probe.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf8")
for k, v in res["checks"].items():
    print(("PASS " if v else "FAIL ") + k)
for dex, r in sizes.items():
    if r:
        print(f"  {dex}: {r['w']:.0f}x{r['h']:.0f} px = {r['w'] * PX_MM:.1f}x{r['h'] * PX_MM:.1f} mm, zoom {r['zoom'] / 256:g}x")
print("browser fps", res["browser_fps"], "decode ms", res["browser_decode_ms_avg"])
print("VERDICT", res["verdict"], res["fail"][:8])
sys.exit(0 if not res["fail"] else 1)
