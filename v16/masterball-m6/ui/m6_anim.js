// JS mirror of core/anim_director.hpp + core/pdk_format.h for the browser simulator.
// tests/anim_parity_test.mjs compares it with the C++ on thousands of samples.
'use strict';
(function (root) {
  const PDK = {IDLE: 0, SLEEP: 1, GREET: 2, JUMP: 3, DANCE: 4, TOUCH: 5, CHEER: 6, CELEBRATE: 7, ALARM: 8, EGG: 9};
  const OV = {NONE: 0, HEART: 1, SPARKLE: 2, ZZZ: 3, EXCLAIM: 4};
  const STAGE = {HOME: 0, FOCUS: 1, ALARM: 2};
  const C = {panelR: 233, homeAnchorY: 30, homeTopLimit: -88, homeBox: 248, focusRestTop: 140, focusTopLimit: 136, focusRingR: 207,
    alarmAnchorY: -150, smallMaxH: 64, smallMaxW: 96, sleepAfterMs: 60000};
  const floats = (dex) => dex === 94 || dex === 468 || dex === 385;
  const isGengar = (dex) => dex === 94;
  const ONE_SHOT = {[PDK.GREET]: 1300, [PDK.TOUCH]: 900, [PDK.JUMP]: 800, [PDK.CELEBRATE]: 1800, [PDK.DANCE]: 1800, [PDK.EGG]: 2600};
  const oneShotMs = (a) => ONE_SHOT[a] || 0;
  // C++ std::lround rounds half away from zero; Math.round rounds half up.
  const lround = (x) => (x < 0 ? -Math.round(-x) : Math.round(x));
  const itrunc = (x) => (x < 0 ? Math.ceil(x) : Math.floor(x));  // C++ integer division
  const wave = (t, period) => Math.sin(2 * Math.PI * (t % period) / period);
  const hop = (t, len, h) => (t < 0 || t >= len ? 0 : -lround(h * Math.sin(Math.PI * t / len)));
  const easeOutBack = (x) => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
  const fade = (t, len) => (t < itrunc(len / 2) ? 255 : t >= len ? 0 : 255 - itrunc(255 * (t - itrunc(len / 2)) / (len - itrunc(len / 2))));

  function poseFor(anim, t, dex) {
    const p = {dx: 0, dy: 0, zoom: 100, overlay: OV.NONE, overlayDy: 0, overlayOpa: 0};
    switch (anim) {
      case PDK.IDLE:
        if (floats(dex)) p.dy = lround(6 * wave(t, 3000)); else p.dy = lround(2 * wave(t, 2400));
        break;
      case PDK.SLEEP:
        p.dy = 8 + lround(3 * wave(t, 4000)); p.overlay = OV.ZZZ;
        p.overlayDy = -itrunc((t % 3000) * 36 / 3000);
        p.overlayOpa = t % 3000 < 2400 ? 255 : 255 - itrunc((t % 3000 - 2400) * 255 / 600);
        break;
      case PDK.GREET:
        if (isGengar(dex)) {
          const x = t < 700 ? t / 700 : 1;
          p.dx = lround(150 * (1 - easeOutBack(x)));
          if (t >= 700) p.dx += lround(4 * wave(t - 700, 300) * (t < 1300 ? (1300 - t) / 600 : 0));
        } else {
          const x = t < 600 ? t / 600 : 1;
          p.dy = lround(-50 * (1 - easeOutBack(x)));
        }
        if (t >= 700) { p.overlay = OV.SPARKLE; p.overlayOpa = fade(t - 700, 600); p.overlayDy = -itrunc((t - 700) / 30); }
        break;
      case PDK.TOUCH:
        if (isGengar(dex)) {
          const decay = t < 900 ? (900 - t) / 900 : 0;
          p.dx = lround(8 * wave(t, 160) * decay); p.dy = hop(t, 300, 8);
        } else {
          p.dy = hop(t, 450, 20) + (t >= 450 && t < 600 ? 2 : 0);
        }
        p.overlay = OV.HEART; p.overlayDy = -itrunc(t * 40 / 900); p.overlayOpa = fade(t, 900);
        break;
      case PDK.JUMP: p.dy = hop(t, 800, 30); break;
      case PDK.CHEER: p.dx = lround(5 * wave(t, 4000)); p.dy = hop(t % 2000, 300, 4); break;
      case PDK.CELEBRATE:
        p.dy = hop(t, 600, 28) + hop(t - 600, 600, 28);
        p.overlay = OV.SPARKLE; p.overlayDy = -itrunc(t * 30 / 1800); p.overlayOpa = fade(t, 1800);
        break;
      case PDK.ALARM:
        p.dy = -lround(8 * Math.abs(wave(t, 500))); p.dx = lround(3 * wave(t, 120));
        p.overlay = OV.EXCLAIM; p.overlayOpa = t % 500 < 300 ? 255 : 0;
        break;
      case PDK.DANCE: case PDK.EGG:
        p.dx = lround(14 * wave(t, 800)); p.dy = -lround(10 * Math.abs(wave(t, 400)));
        if (anim === PDK.EGG) { p.overlay = OV.HEART; p.overlayDy = -itrunc((t % 1300) * 40 / 1300); p.overlayOpa = fade(t % 1300, 1300); }
        break;
    }
    return p;
  }

  class Director {
    constructor() { this.shotAnim = PDK.IDLE; this.loopAnim = PDK.IDLE; this.shotStart = 0; this.loopStart = 0; this.lastTouch = 0; this.wakeGuard = 0; }
    trigger(anim, now) { if (oneShotMs(anim) <= 0) return; if (anim === PDK.TOUCH && now < this.wakeGuard) return; this.shotAnim = anim; this.shotStart = now; }
    sleeping(i) { const last = Math.max(i.lastTouch || 0, this.lastTouch); return i.night && !i.focus && !i.ringing && i.now - last >= C.sleepAfterMs; }
    touched(i) { const was = this.sleeping(i); this.lastTouch = i.now; if (was) { this.trigger(PDK.GREET, i.now); this.wakeGuard = i.now + 300; } }
    decide(i) {
      const stage = i.ringing ? STAGE.ALARM : i.focus ? STAGE.FOCUS : STAGE.HOME;
      let loop = PDK.IDLE;
      if (stage === STAGE.ALARM) loop = PDK.ALARM; else if (stage === STAGE.FOCUS) loop = PDK.CHEER; else if (this.sleeping(i)) loop = PDK.SLEEP;
      if (loop !== this.loopAnim) { this.loopAnim = loop; this.loopStart = i.now; }
      const live = this.shotAnim !== PDK.IDLE && stage !== STAGE.ALARM && i.now - this.shotStart < oneShotMs(this.shotAnim) && i.now >= this.shotStart;
      if (!live) this.shotAnim = PDK.IDLE;
      const anim = live ? this.shotAnim : loop, t = live ? i.now - this.shotStart : i.now - this.loopStart;
      return {stage, anim, t, pose: poseFor(anim, t, i.dex)};
    }
  }

  function baseZoom(st, w, h) {
    if (w <= 0 || h <= 0) return 256;
    if (st === STAGE.HOME) { const m = Math.max(w, h); let s = itrunc(C.homeBox / m); s = Math.min(3, Math.max(1, s)); return 256 * s; }
    let z = 256;
    if (h > C.smallMaxH) z = itrunc(256 * C.smallMaxH / h);
    if (w > C.smallMaxW && itrunc(256 * C.smallMaxW / w) < z) z = itrunc(256 * C.smallMaxW / w);
    return z;
  }
  function place(st, w, h, p) {
    const zoom = itrunc(baseZoom(st, w, h) * p.zoom / 100);
    const sw = itrunc((w * zoom + 255) / 256), sh = itrunc((h * zoom + 255) / 256);
    const ay = st === STAGE.HOME ? C.homeAnchorY : st === STAGE.FOCUS ? C.focusRestTop + itrunc(sh / 2) : C.alarmAnchorY;
    let cx = p.dx, cy = ay + p.dy;
    const top = st === STAGE.HOME ? C.homeTopLimit : st === STAGE.FOCUS ? C.focusTopLimit : -C.panelR;
    if (cy - itrunc(sh / 2) < top) cy = top + itrunc(sh / 2);
    const rmax = st === STAGE.FOCUS ? C.focusRingR : C.panelR - 4;
    for (let g = 0; g < 400; g++) {
      const fx = Math.abs(cx) + itrunc(sw / 2) + 1, fy = Math.abs(cy) + itrunc(sh / 2) + 1;
      if (fx * fx + fy * fy <= rmax * rmax) break;
      if (cx) cx += cx > 0 ? -1 : 1;
      if (Math.abs(cy) > 0 && (cy < 0 || cy - itrunc(sh / 2) > top)) cy += cy > 0 ? -1 : 1; else if (!cx) break;
    }
    return {x: cx - itrunc(sw / 2), y: cy - itrunc(sh / 2), w: sw, h: sh, zoom};
  }

  // ---- PDK1 pack decoding (same rules as core/pdk_format.h) ----
  const u16 = (b, o) => b[o] | (b[o + 1] << 8);
  const u32 = (b, o) => (b[o] | (b[o + 1] << 8) | (b[o + 2] << 16) | (b[o + 3] << 24)) >>> 0;
  function readPack(bytes) {
    const b = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
    if (b.length < 8 || String.fromCharCode(b[0], b[1], b[2], b[3]) !== 'PDK1' || u16(b, 4) !== 1) return null;
    const n = u16(b, 6);
    if (8 + 20 * n > b.length) return null;
    const clips = [];
    for (let i = 0; i < n; i++) {
      const o = 8 + 20 * i;
      clips.push({dex: u16(b, o), anim: b[o + 2], frames: b[o + 3], w: u16(b, o + 4), h: u16(b, o + 6), ms: u16(b, o + 8) || 100,
        paletteN: u16(b, o + 10), paletteOff: u32(b, o + 12), framesOff: u32(b, o + 16)});
    }
    return {b, clips};
  }
  function findClip(pack, dex, anim) {
    if (!pack) return null;
    return pack.clips.find((c) => c.dex === dex && c.anim === anim) || pack.clips.find((c) => c.dex === dex && c.anim === PDK.IDLE) || null;
  }
  function decodeFrame(pack, clip, idx) {  // -> RGBA Uint8ClampedArray (w*h*4), or null on a bad stream
    const b = pack.b, npx = clip.w * clip.h, out = new Uint8ClampedArray(npx * 4);
    let f = clip.framesOff;
    for (let k = 0; k < idx % clip.frames; k++) f += 4 + u32(b, f);
    const len = u32(b, f);
    if (len % 2 || f + 4 + len > b.length) return null;
    let o = 0;
    for (let i = f + 4; i < f + 4 + len; i += 2) {
      const run = b[i], v = b[i + 1];
      if (!run || o + run > npx) return null;
      const pi = clip.paletteOff + 3 * (v < clip.paletteN ? v : 0), c = u16(b, pi), a = b[pi + 2];
      const r = ((c >> 11) & 31) * 255 / 31, g = ((c >> 5) & 63) * 255 / 63, bl = (c & 31) * 255 / 31;
      for (let k = 0; k < run; k++, o++) { out[o * 4] = r; out[o * 4 + 1] = g; out[o * 4 + 2] = bl; out[o * 4 + 3] = a; }
    }
    return o === npx ? out : null;
  }

  root.M6Anim = {PDK, OV, STAGE, C, poseFor, Director, baseZoom, place, oneShotMs, readPack, findClip, decodeFrame};
  if (typeof module !== 'undefined') module.exports = root.M6Anim;
})(typeof window !== 'undefined' ? window : globalThis);
