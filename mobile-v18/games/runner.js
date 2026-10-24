// Game 3 — 팬텀 런: Canvas 2D side-scroller. Hold and drag (or ↑/↓, W/S) to float Gengar through the
// night sky, collect stars and berries, dodge shadow orbs. Physics live in runner-engine.js.
import { artUrl } from '../pokedex.js';
import { el } from '../ui.js';
import { createRunner, stepRunner, totalScore, multiplier, RUNNER } from './runner-engine.js';

function drawStar(g, x, y, r) {
  g.beginPath();
  for (let k = 0; k < 10; k++) {
    const a = -Math.PI / 2 + (k * Math.PI) / 5, rr = k % 2 ? r * 0.45 : r;
    g.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr);
  }
  g.closePath();
  g.fillStyle = '#f6d36b'; g.fill();
  g.strokeStyle = '#d8a93c'; g.lineWidth = 2; g.stroke();
}
function drawBerry(g, x, y, r) {
  g.fillStyle = '#6aa6dc'; g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill();
  g.fillStyle = '#ffffff88'; g.beginPath(); g.arc(x - r * 0.35, y - r * 0.35, r * 0.3, 0, Math.PI * 2); g.fill();
  g.fillStyle = '#6dbb7a'; g.beginPath(); g.ellipse(x + r * 0.2, y - r * 1.05, r * 0.45, r * 0.22, -0.5, 0, Math.PI * 2); g.fill();
}
function drawOrb(g, x, y, r, t) {
  const grd = g.createRadialGradient(x - r * 0.3, y - r * 0.3, r * 0.2, x, y, r * 1.25);
  grd.addColorStop(0, '#6c4f8c'); grd.addColorStop(0.6, '#3a2950'); grd.addColorStop(1, '#3a295000');
  g.fillStyle = grd; g.beginPath(); g.arc(x, y, r * 1.25, 0, Math.PI * 2); g.fill();
  g.strokeStyle = '#b89ad8aa'; g.lineWidth = 2; g.beginPath(); g.arc(x, y, r * 0.8, t * 4, t * 4 + 2.2); g.stroke();
}
function drawFallbackGhost(g, x, y, r) {
  g.fillStyle = '#8a6bb1'; g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill();
  g.fillStyle = '#f2a0a6'; g.beginPath(); g.ellipse(x - r * 0.35, y - r * 0.2, r * 0.22, r * 0.14, 0.4, 0, Math.PI * 2); g.ellipse(x + r * 0.35, y - r * 0.2, r * 0.22, r * 0.14, -0.4, 0, Math.PI * 2); g.fill();
  g.fillStyle = '#fff'; g.beginPath(); g.ellipse(x, y + r * 0.3, r * 0.55, r * 0.2, 0, 0, Math.PI); g.fill();
}

export default {
  id: 'runner', title: '팬텀 런', eyebrow: 'SHADOW RUN', tagline: '별을 모으고 그림자 구슬은 피하기', icon: 94, color: '#e4dcf3',
  desc: '화면을 누른 채 위아래로 움직이면 팬텀이 따라와. 별(10점)과 열매(25점)를 모으고 그림자 구슬을 피해 줘. 연속으로 모으면 점수가 커져!',
  pausable: true, unit: '점',
  options: [{ key: 'pace', label: '속도', default: 'normal', choices: [{ v: 'gentle', label: '느긋하게', hint: '천천히 시작 · 하트 4개' }, { v: 'normal', label: '보통', hint: '하트 3개 · 점점 빨라져요' }] }],
  recordKey: (o) => o.pace,
  mount(host, opts, api) {
    const reduce = api.env.reduceMotion();
    const wrap = el('div', 'runner-wrap');
    const canvas = el('canvas', 'runner-canvas', '', { 'aria-label': '팬텀 런 게임 화면. 위아래 방향키나 드래그로 조작' , role: 'img' });
    const hint = el('div', 'runner-hint', '화면을 누르면 시작! 누른 채 위아래로 움직여 봐 · 키보드 ↑ ↓');
    wrap.append(canvas, hint);
    host.replaceChildren(wrap);
    const g = canvas.getContext('2d');
    const dpr = Math.min(window.devicePixelRatio || 1, (navigator.hardwareConcurrency || 4) <= 4 ? 1.5 : 2);
    let s, scale = 1, raf = 0, lastHud = '', last = 0, started = false, paused = false, dead = false, shake = 0;
    const input = { targetY: null, dir: 0 };
    const keys = new Set();
    const sprite = new Image();
    sprite.crossOrigin = 'anonymous';
    let spriteOk = false;
    sprite.onload = () => { spriteOk = true; };
    sprite.src = artUrl(94);
    const bgStars = Array.from({ length: 26 }, (_, k) => ({ x: (k * 97) % 1000 / 1000, y: (k * 53) % 1000 / 1000 * 0.75, r: 1 + (k % 3) }));

    function resize() {
      const box = wrap.getBoundingClientRect();
      const w = Math.max(280, box.width), h = Math.max(200, box.height);
      canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr);
      canvas.style.width = w + 'px'; canvas.style.height = h + 'px';
      scale = h / RUNNER.H;
      const worldW = w / scale;
      if (!s) {
        s = createRunner(worldW);
        if (opts.pace === 'gentle') { s.lives = 4; s.t = -15; } // negative time = slower ramp
      } else { s.w = Math.max(420, worldW); s.ghost.x = s.w * RUNNER.ghostX; }
      draw();
    }

    const worldY = (clientY) => (clientY - canvas.getBoundingClientRect().top) / scale;
    canvas.addEventListener('pointerdown', (e) => {
      e.preventDefault();
      canvas.setPointerCapture?.(e.pointerId);
      input.targetY = worldY(e.clientY);
      if (!started) begin();
    });
    canvas.addEventListener('pointermove', (e) => { if (e.buttons || e.pointerType === 'touch') input.targetY = worldY(e.clientY); });
    const release = () => { input.targetY = null; };
    canvas.addEventListener('pointerup', release);
    canvas.addEventListener('pointercancel', release);
    const onKey = (e) => {
      const up = ['ArrowUp', 'w', 'W'].includes(e.key), down = ['ArrowDown', 's', 'S'].includes(e.key);
      if (!up && !down && e.key !== ' ') return;
      e.preventDefault();
      if (e.type === 'keydown') { if (!started) begin(); if (up) keys.add('u'); if (down) keys.add('d'); }
      else { if (up) keys.delete('u'); if (down) keys.delete('d'); }
      input.dir = (keys.has('d') ? 1 : 0) - (keys.has('u') ? 1 : 0);
    };
    window.addEventListener('keydown', onKey);
    window.addEventListener('keyup', onKey);
    const ro = new ResizeObserver(resize);
    ro.observe(wrap);

    function begin() {
      started = true;
      hint.hidden = true;
      api.sfx('start');
      last = performance.now();
      raf = requestAnimationFrame(frame);
    }

    function frame(now) {
      if (dead || paused) return;
      const dt = (now - last) / 1000;
      last = now;
      stepRunner(s, dt, input);
      for (const ev of s.events) {
        if (ev === 'hit') { api.sfx('hit'); shake = reduce ? 0 : 0.25; if (navigator.vibrate) navigator.vibrate(40); }
        if (ev === 'star') api.sfx('collect');
        if (ev === 'berry') api.sfx('berry');
      }
      shake = Math.max(0, shake - dt);
      draw();
      const hudKey = `${totalScore(s)}|${s.combo}|${s.lives}`;
      if (hudKey !== lastHud) {
        lastHud = hudKey;
        api.hud([['점수', totalScore(s)], ['콤보', `${s.combo}${s.combo >= 5 ? ' ×' + multiplier(s.combo) : ''}`], ['하트', '♥'.repeat(Math.max(0, s.lives))]]);
      }
      if (s.over) return end();
      raf = requestAnimationFrame(frame);
    }

    function draw() {
      if (!s) return;
      const W = canvas.width, H = canvas.height;
      g.setTransform(1, 0, 0, 1, 0, 0);
      const sky = g.createLinearGradient(0, 0, 0, H);
      sky.addColorStop(0, '#d9cfe9'); sky.addColorStop(0.65, '#f4eef0'); sky.addColorStop(1, '#e2d5e6');
      g.fillStyle = sky; g.fillRect(0, 0, W, H);
      const k = dpr * scale;
      const ox = shake ? (Math.random() - 0.5) * 8 * dpr : 0;
      g.setTransform(k, 0, 0, k, ox, 0);
      // parallax: moon, twinkles, hills
      g.fillStyle = '#f8e2d5b8'; g.beginPath(); g.arc(s.w * 0.8, 70, 46, 0, Math.PI * 2); g.fill();
      g.fillStyle = '#ffffffcc';
      for (const b of bgStars) {
        const x = ((b.x * s.w - s.t * 12 * b.r) % s.w + s.w) % s.w;
        g.fillRect(x, b.y * s.h, b.r, b.r);
      }
      const hillShift = (s.t * 30) % 400;
      g.fillStyle = '#baa4d052';
      for (let x = -hillShift; x < s.w + 400; x += 400) { g.beginPath(); g.ellipse(x + 200, s.h + 20, 260, 70, 0, 0, Math.PI * 2); g.fill(); }
      for (const it of s.items) {
        if (it.kind === 'star') drawStar(g, it.x, it.y, it.r + 3);
        else if (it.kind === 'berry') drawBerry(g, it.x, it.y, it.r);
        else drawOrb(g, it.x, it.y, it.r, s.t);
      }
      const gh = s.ghost;
      const blink = s.invuln > 0 && Math.floor(s.invuln * 10) % 2 === 0;
      if (!blink) {
        g.save();
        g.translate(gh.x, gh.y + (reduce ? 0 : Math.sin(s.t * 5) * 2));
        g.rotate(input.targetY != null ? Math.max(-0.25, Math.min(0.25, (input.targetY - gh.y) / 300)) : 0);
        if (spriteOk) g.drawImage(sprite, -gh.r * 1.7, -gh.r * 1.7, gh.r * 3.4, gh.r * 3.4);
        else drawFallbackGhost(g, 0, 0, gh.r);
        g.restore();
      }
    }

    function end() {
      dead = true;
      api.finish({
        score: totalScore(s), headline: `${totalScore(s)}점`, eyebrow: 'SHADOW RUN', pokemon: 94,
        lines: [`별 ${s.stars}개 · 열매 ${s.berries}개 · 최고 콤보 ${s.bestCombo}`, `${Math.floor(s.alive)}초 동안 날았어!`, totalScore(s) >= 300 ? '팬텀: “크크, 우리 꽤 잘 맞는걸?”' : '팬텀: “한 번 더 날아 볼까?”'],
      });
    }

    resize();
    return {
      pause() { paused = true; cancelAnimationFrame(raf); input.targetY = null; keys.clear(); input.dir = 0; },
      resume() { paused = false; if (started) { last = performance.now(); raf = requestAnimationFrame(frame); } },
      destroy() {
        dead = true; cancelAnimationFrame(raf); ro.disconnect();
        window.removeEventListener('keydown', onKey); window.removeEventListener('keyup', onKey);
      },
      _state: () => s,
    };
  },
};
