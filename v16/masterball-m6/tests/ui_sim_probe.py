"""Drive ui/M6_Device_Simulator.html in a real Chromium-family browser (installed Edge by default).

Checks circle clipping of every visible glyph run, physical legibility (ink height -> arc minutes at
30/50/70 cm) and the timer / alarm / gesture behaviour, and saves 466x466 captures.
usage: python ui_sim_probe.py <out_dir> [--channel msedge]
"""
import json
import math
import pathlib
import sys

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
SIM = (HERE.parent / "ui" / "M6_Device_Simulator.html").as_uri()
OUT = pathlib.Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
CHANNEL = sys.argv[sys.argv.index("--channel") + 1] if "--channel" in sys.argv else "msedge"
PX_MM = 36.75 / 466

GLYPHS_JS = """() => {
  const dev = document.getElementById('dev'), r0 = dev.getBoundingClientRect();
  const cx = r0.left + r0.width / 2, cy = r0.top + r0.height / 2, R = r0.width / 2, out = [];
  const walker = document.createTreeWalker(dev, NodeFilter.SHOW_TEXT);
  const ctx = document.createElement('canvas').getContext('2d');
  while (walker.nextNode()) {
    const n = walker.currentNode, el = n.parentElement;
    if (!n.textContent.trim() || el.closest('[hidden]') || getComputedStyle(el).display === 'none') continue;
    const range = document.createRange(); range.selectNodeContents(n);
    for (const r of range.getClientRects()) {
      if (!r.width) continue;
      const far = Math.max(...[[r.left, r.top], [r.right, r.top], [r.left, r.bottom], [r.right, r.bottom]].map(([x, y]) => Math.hypot(x - cx, y - cy)));
      const cs = getComputedStyle(el);
      const scale = el.getBoundingClientRect().height / Math.max(1, el.offsetHeight) || 1;
      ctx.font = `${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
      const m = ctx.measureText(n.textContent.trim());
      out.push({text: n.textContent.trim(), font_px: parseFloat(cs.fontSize) * scale, fontFamily: cs.fontFamily,
                ink_px: (m.actualBoundingBoxAscent + m.actualBoundingBoxDescent) * scale,
                overshoot_px: +(far - R).toFixed(1), role: el.dataset.t || el.className || el.parentElement.className});
    }
  }
  return out;
}"""


def arcmin(mm, d):
    return math.degrees(2 * math.atan(mm / 2 / d)) * 60


res = {"screens": {}, "behaviour": {}, "fail": []}
with sync_playwright() as p:
    b = p.chromium.launch(channel=CHANNEL)
    pg = b.new_page(viewport={"width": 1200, "height": 900})
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(SIM)
    pg.wait_for_timeout(1500)
    font_ok = pg.evaluate("document.fonts.check('700 80px Pretendard')")
    res["pretendard_loaded"] = font_ok
    E = lambda js: pg.evaluate(js)  # noqa: E731

    def shot(name):
        pg.locator("#dev").screenshot(path=str(OUT / f"m6_{name}.png"))
        g = pg.evaluate(GLYPHS_JS)
        res["screens"][name] = g
        return g

    def check(name, cond, detail=""):
        res["behaviour"][name] = bool(cond)
        if not cond:
            res["fail"].append(f"{name} {detail}")

    check("untrusted clock shows --:--", "--:--" in pg.inner_text("#dev"))
    check("untrusted clock pill", "시간 맞춰줘" in pg.inner_text("#dev"))
    shot("home_unsynced")
    E("PD.S.trusted=true; PD.S.utcOffsetMs = Date.UTC(2026,9,24,23,20,0) - Date.now(); PD.render()")  # 08:20 KST
    shot("home")
    check("home clock 08:20", "08:20" in pg.inner_text("#dev"), pg.inner_text("#dev"))
    # long press starts the 25 min preset
    dev = pg.locator("#dev")
    box = dev.bounding_box()
    cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    pg.mouse.move(cx, cy); pg.mouse.down(); pg.wait_for_timeout(700); pg.mouse.up()
    pg.wait_for_timeout(300)
    check("long press starts focus", E("PD.S.phase") == "running")
    check("F1 shows 25 + 분 남음", "25" in pg.inner_text("#dev") and "분 남음" in pg.inner_text("#dev"))
    shot("focus_minutes")
    E("PD.advance(1000)")
    check("24:59 => still 25 minutes (ceil)", "25" in pg.inner_text("#dev"))
    E("PD.advance(15*60000)")
    pg.wait_for_timeout(300)
    rem = E("Math.ceil(PD.remaining()/1000)")
    check("remaining after 15:01 ~ 599 s", 590 <= rem <= 600, str(rem))
    check("last 10 min switches to MM:SS", ":" in pg.inner_text("#dev .big"))
    shot("focus_mmss")
    pg.mouse.move(cx, cy); pg.mouse.down(); pg.wait_for_timeout(700); pg.mouse.up()
    frozen = E("PD.remaining()")
    E("PD.advance(120000)")
    check("pause freezes", E("PD.S.phase") == "paused" and E("PD.remaining()") == frozen)
    pg.mouse.move(cx, cy); pg.mouse.down(); pg.wait_for_timeout(700); pg.mouse.up()
    check("resume continues", E("PD.S.phase") == "running")
    # menu tap on timer while running must not reset (only long press cancels)
    E("PD.S.menu=true; PD.render()")
    shot("menu")
    E("PD.menuAct(0,false)")
    check("menu tap does not cancel running focus", E("PD.S.phase") == "running")
    E("PD.S.menu=false; PD.render()")
    E("PD.advance(11*60000)")
    check("completion once", E("PD.S.completed") == 1 and E("PD.S.phase") == "done")
    E("PD.advance(10*60000)")
    check("no second completion", E("PD.S.completed") == 1)
    shot("focus_done")
    E("PD.tap()")
    # daily alarm: set 08:50 and pass it
    m_now = E("PD.absMin() % 1440")
    target = (m_now + 2) % 1440
    E(f"PD.S.alarm={{en:true,min:{target}}}; PD.S.armed=PD.absMin(); PD.render()")
    E("PD.advance(60000)")
    check("alarm not early", not E("PD.S.ringing"))
    E("PD.advance(61000)")
    check("daily alarm fires at its minute", E("PD.S.ringing"))
    shot("alarm")
    E("PD.tap()")
    check("tap = snooze", not E("PD.S.ringing") and E("PD.S.snoozeUntil") > 0)
    E("PD.advance(5*60000+1000)")
    check("snooze re-rings after 5 min", E("PD.S.ringing"))
    E("PD.advance(121000)")
    check("ring auto-snoozes after 2 min", not E("PD.S.ringing"))
    E("PD.S.ringing=true; PD.longPress()")
    check("long press dismisses", not E("PD.S.ringing") and E("PD.S.snoozeUntil") < 0)
    E("PD.advance(24*3600*1000)")
    check("fires again next day", E("PD.S.ringing"))
    E("PD.longPress()")
    E("PD.S.usb=4200; PD.render()")
    check("weak USB pill", "전원 약함" in pg.inner_text("#dev"))
    shot("power_warning")
    E("PD.S.usb=4850; PD.render()")
    E("PD.S.lastTouch=PD.S.mono; PD.S.screen=true; PD.render()")
    for _ in range(5):
        E("PD.tap()")
    check("5 taps show hidden message", "오늘도" in pg.inner_text("#dev"), json.dumps(E("({ring:PD.S.ringing,screen:PD.S.screen,phase:PD.S.phase,taps:PD.S.taps,msg:PD.S.msgUntil,mono:PD.S.mono,pass:PD.S.passkey,menu:PD.S.menu})")))
    shot("message")
    E("PD.S.msgUntil=0; PD.menuAct(4,false)")
    shot("pairing")
    E("PD.S.passkey=0; PD.S.lastTouch=PD.S.mono; PD.advance(601000)")
    pg.wait_for_timeout(400)
    check("screen off after 10 min idle", E("PD.S.screen") is False)
    phase_before = E("PD.S.phase")
    E("PD.longPress()")
    check("first touch only wakes", E("PD.S.screen") and E("PD.S.phase") == phase_before)
    res["page_errors"] = errors
    check("no JS errors", not errors, str(errors))
    b.close()

# legibility + clipping evaluation
PRIMARY = {"clock", "big", "alarm"}
rows = []
for scr, glyphs in res["screens"].items():
    for g in glyphs:
        mm = g["ink_px"] * PX_MM
        a50 = arcmin(mm, 500)
        primary = g["role"] in PRIMARY and g["text"] != "--:--"  # dashes have no digit-height ink
        close_range = scr in ("menu", "pairing", "message")
        need = 30.0 if primary else (16.0 if close_range else 20.0)
        dist = 300 if close_range else 500
        a = arcmin(mm, dist)
        ok_size = a >= need
        ok_clip = g["overshoot_px"] <= -4.0
        rows.append({**g, "screen": scr, "ink_mm": round(mm, 2), "arcmin_30": round(arcmin(mm, 300), 1),
                     "arcmin_50": round(a50, 1), "arcmin_70": round(arcmin(mm, 700), 1),
                     "required_arcmin": need, "at_mm": dist, "size_ok": ok_size, "inside_circle": ok_clip})
        if not ok_size:
            res["fail"].append(f"legibility {scr} '{g['text']}' {a:.1f}' < {need}' at {dist / 10:.0f} cm")
        if not ok_clip:
            res["fail"].append(f"clipping {scr} '{g['text']}' overshoot {g['overshoot_px']} px")
res["legibility"] = rows
res["verdict"] = "PASS" if not res["fail"] else "FAIL"
(OUT / "ui_sim_probe.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf8")
for k, v in res["behaviour"].items():
    print(("PASS " if v else "FAIL ") + k)
for r in rows:
    print(f'{r["screen"]:14s} {r["text"][:16]:16s} {r["font_px"]:5.1f}px ink {r["ink_mm"]:5.2f}mm 50cm {r["arcmin_50"]:5.1f}\' '
          f'clip {r["overshoot_px"]:6.1f}  {"OK" if r["size_ok"] and r["inside_circle"] else "XX"}')
print("pretendard loaded:", res["pretendard_loaded"])
print("VERDICT", res["verdict"], res["fail"][:12])
