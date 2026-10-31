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

    # ---- clock without a phone: tap the pill, set 2026-11-02 07:58 one field at a time ----------
    BUTTONS_JS = """() => { const d = document.getElementById('dev').getBoundingClientRect(), cx = d.left + d.width / 2,
      cy = d.top + d.height / 2, R = d.width / 2;
      return [...document.querySelectorAll('#dev [data-e],#dev [data-n],#dev [data-m]')].map(b => { const r = b.getBoundingClientRect();
        // rounded buttons: test the rounded-rectangle outline, sampled every 2 degrees
        const rad = Math.min(r.width, r.height) / 2, pts = [];
        for (const [ox, oy, a0] of [[r.right - rad, r.top + rad, -90], [r.right - rad, r.bottom - rad, 0], [r.left + rad, r.bottom - rad, 90], [r.left + rad, r.top + rad, 180]])
          for (let a = a0; a <= a0 + 90; a += 2) pts.push(Math.hypot(ox + rad * Math.cos(a * Math.PI / 180) - cx, oy + rad * Math.sin(a * Math.PI / 180) - cy));
        return {text: b.textContent.trim() || b.getAttribute('aria-label'), w: r.width, h: r.height, overshoot: +(Math.max(...pts) - R).toFixed(1)}; }); }"""

    def buttons_inside(name):
        for b in E(BUTTONS_JS):
            check(f"{name} button '{b['text']}' inside circle", b["overshoot"] <= -2.0, str(b))
            check(f"{name} button '{b['text']}' >= 64 px", min(b["w"], b["h"]) >= 64, str(b))

    def click(sel):
        bb = pg.locator(sel).bounding_box()
        pg.mouse.click(bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2)
        pg.wait_for_timeout(60)

    click("#dev [data-p]")
    check("pill opens clock editor", E("!!PD.S.edit && !PD.S.edit.alarm"))
    check("editor starts at the firmware date", E("PD.S.edit.t.year===2026 && PD.S.edit.t.month===10 && PD.S.edit.t.day===31"))
    shot("clock_edit_year")
    buttons_inside("clock editor")
    click("#dev [data-n='1']")                       # year ok -> month
    click("#dev [data-e='1']")                       # 11
    shot("clock_edit_month")
    click("#dev [data-n='1']")
    for _ in range(2):
        click("#dev [data-e='1']")                   # day 31 -> 1 -> 2 (wraps inside November: 30 days)
    check("Nov 31 impossible: day wraps", E("PD.S.edit.t.month===11 && PD.S.edit.t.day===2"), json.dumps(E("PD.S.edit.t")))
    click("#dev [data-n='1']")
    for _ in range(7):
        click("#dev [data-e='1']")                   # hour 0 -> 7
    shot("clock_edit_hour")
    click("#dev [data-n='1']")
    click("#dev [data-e='-1']"); click("#dev [data-e='-1']")  # minute 0 -> 58
    check("minute wraps down without touching hour", E("PD.S.edit.t.hour===7 && PD.S.edit.t.minute===58"))
    shot("clock_edit_minute")
    check("last page says 저장", "저장" in pg.inner_text("#dev"))
    click("#dev [data-n='1']")
    check("saved clock is trusted", E("PD.S.trusted") and not E("!!PD.S.edit"))
    check("home shows 07:58", "07:58" in pg.inner_text("#dev"), pg.inner_text("#dev"))
    check("time pill gone", "시간 맞춰줘" not in pg.inner_text("#dev"))
    # alarm time on the device: hold 알람 in the menu, set 08:00, it rings two minutes later
    E("PD.S.menu=true; PD.render()")
    buttons_inside("menu")
    E("PD.menuAct(1,true)")
    check("hold 알람 opens alarm editor", E("!!PD.S.edit && PD.S.edit.alarm"))
    E("PD.S.edit.t.hour=8; PD.S.edit.t.minute=59; PD.render()")  # fields wrap on their own: 08:59 + 1 min -> 08:00
    click("#dev [data-n='1']"); click("#dev [data-e='1']")
    shot("alarm_edit_minute")
    buttons_inside("alarm editor")
    click("#dev [data-n='1']")
    check("alarm saved 08:00 on", E("PD.S.alarm.en && PD.S.alarm.min===480"))
    E("PD.advance(60000)")
    check("device-set alarm not early", not E("PD.S.ringing"))
    E("PD.advance(61000)")
    check("device-set alarm rings at 08:00", E("PD.S.ringing"))
    E("if (PD.S.ringing) PD.longPress(); PD.S.alarm={en:false,min:450}; PD.S.lastFired=-1; PD.S.armed=-1; PD.render()")
    # cancel on the first page leaves the clock alone
    before = E("PD.absMin()")
    E("PD.openClock()")
    click("#dev [data-e='1']"); click("#dev [data-n='-1']")
    check("취소 keeps the clock", not E("!!PD.S.edit") and abs(E("PD.absMin()") - before) <= 1)
    check("editing never started focus", E("PD.S.phase") == "idle")

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
    E("PD.S.usb=3700; PD.render()")
    check("weak USB pill", "전원 약함" in pg.inner_text("#dev"))
    shot("power_warning")
    E("PD.S.usb=4850; PD.render()")
    E("PD.S.lastTouch=PD.S.mono; PD.S.screen=true; PD.render()")
    # one evaluate: a screenshot stall can otherwise let the simulator's real-time clock jump past the
    # 3 s tap window between two separate calls (harness race, not device behaviour)
    # start from the plain home screen: on a finished focus ("수고했어!") the first tap only clears it
    E("if (PD.S.phase === 'done') PD.tap()")
    check("home before the 5-tap egg", E("PD.S.phase") == "idle")
    E("for (let i = 0; i < 5; i++) PD.tap()")
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
        close_range = scr in ("menu", "pairing", "message") or "_edit_" in scr  # used at arm's length
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
