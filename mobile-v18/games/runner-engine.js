// Pure simulation for 팬텀 런: no DOM, no timing source, injectable randomness. The renderer in
// runner.js draws whatever state this produces, so collisions are testable without images.
export const RUNNER = Object.freeze({
  H: 360, ghostX: 0.2, ghostR: 26, hitScale: 0.72, lives: 3, invuln: 1.2,
  baseSpeed: 170, speedPerSec: 7, maxSpeed: 430, follow: 560, keySpeed: 380,
});

export function createRunner(width, rnd = Math.random) {
  const H = RUNNER.H;
  return {
    w: Math.max(420, width), h: H, t: 0, alive: 0, speed: RUNNER.baseSpeed, rnd,
    ghost: { x: Math.max(420, width) * RUNNER.ghostX, y: H / 2, r: RUNNER.ghostR },
    items: [], spawnT: 1.0, score: 0, dist: 0, combo: 0, bestCombo: 0, lives: RUNNER.lives, invuln: 0,
    stars: 0, berries: 0, hits: 0, over: false, events: [],
  };
}

export const circleHit = (a, b, scale = 1) => {
  const dx = a.x - b.x, dy = a.y - b.y, r = (a.r + b.r) * scale;
  return dx * dx + dy * dy < r * r;
};

export const multiplier = (combo) => 1 + Math.floor(combo / 5) * 0.5;

function spawn(s) {
  const p = Math.max(0, Math.min(1, s.t / 90));
  const roll = s.rnd();
  const orbChance = 0.34 + 0.22 * p;
  const kind = roll < orbChance ? 'orb' : roll < orbChance + 0.12 ? 'berry' : 'star';
  const r = kind === 'orb' ? 20 + s.rnd() * 10 : kind === 'berry' ? 15 : 13;
  const y = r + 8 + s.rnd() * (s.h - 2 * r - 16);
  s.items.push({ kind, x: s.w + r + 10, y, y0: y, r, phase: s.rnd() * Math.PI * 2, wobble: kind === 'orb' && s.rnd() < 0.4 * p ? 26 : 0 });
  s.spawnT = Math.max(0.3, 0.92 - s.t * 0.011) * (0.7 + s.rnd() * 0.6);
}

// input: { targetY: number|null (pointer, world units), dir: -1|0|1 (keys) }
export function stepRunner(s, dt, input = {}) {
  if (s.over) return s;
  dt = Math.min(0.05, Math.max(0, dt));
  s.events.length = 0;
  s.t += dt;
  s.alive += dt;
  s.speed = Math.max(110, Math.min(RUNNER.maxSpeed, RUNNER.baseSpeed + RUNNER.speedPerSec * s.t));
  const g = s.ghost;
  if (input.targetY != null) {
    const d = input.targetY - g.y, m = RUNNER.follow * dt;
    g.y += Math.max(-m, Math.min(m, d));
  } else if (input.dir) g.y += input.dir * RUNNER.keySpeed * dt;
  g.y = Math.max(g.r, Math.min(s.h - g.r, g.y));
  s.invuln = Math.max(0, s.invuln - dt);

  s.spawnT -= dt;
  if (s.spawnT <= 0) spawn(s);

  s.dist += (s.speed * dt) / 40;
  const keep = [];
  for (const it of s.items) {
    it.x -= s.speed * dt * (it.kind === 'orb' ? 1.12 : 1);
    if (it.wobble) it.y = it.y0 + Math.sin(s.t * 3 + it.phase) * it.wobble;
    if (circleHit(g, it, it.kind === 'orb' ? RUNNER.hitScale : 1)) {
      if (it.kind === 'orb') {
        if (s.invuln > 0) { keep.push(it); continue; }
        s.lives--; s.hits++; s.combo = 0; s.invuln = RUNNER.invuln;
        s.events.push('hit');
        if (s.lives <= 0) { s.over = true; s.events.push('over'); }
        continue; // the orb pops
      }
      s.combo++;
      s.bestCombo = Math.max(s.bestCombo, s.combo);
      const pts = (it.kind === 'berry' ? 25 : 10) * multiplier(s.combo);
      s.score += pts;
      if (it.kind === 'berry') s.berries++; else s.stars++;
      s.events.push(it.kind);
      continue;
    }
    if (it.x > -it.r - 10) keep.push(it);
  }
  s.items = keep;
  return s;
}

export const totalScore = (s) => Math.floor(s.score + s.dist);
