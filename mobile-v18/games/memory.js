// Game 5 — 카드 짝맞추기. 4×3 (6 pairs) or 4×4 (8 pairs), free or timed. Best = fewest moves.
import { POKEDEX, PARTNERS } from '../pokedex.js';
import { el, button, pokeImg, sample, shuffle } from '../ui.js';

export function makeBoard(size, rnd = Math.random) {
  const pairs = size === '4x4' ? 8 : 6;
  // favour partners so the board feels familiar, then fill from the wider Pokédex
  const picks = sample(PARTNERS, Math.min(pairs, 5), rnd);
  const rest = sample(POKEDEX.filter((p) => !picks.includes(p)), pairs - picks.length, rnd);
  return shuffle([...picks, ...rest].flatMap((p) => [p, p]), rnd).map((p, k) => ({ k, id: p.id, name: p.name, open: false, done: false }));
}

// Pure turn logic so it can be tested without the DOM.
export function flip(game, k) {
  const c = game.cards[k];
  if (!c || c.open || c.done || game.pending.length >= 2) return { game, event: 'ignore' };
  const cards = game.cards.map((x) => (x.k === k ? { ...x, open: true } : x));
  const pending = [...game.pending, k];
  if (pending.length < 2) return { game: { ...game, cards, pending }, event: 'flip' };
  const [a, b] = pending.map((i) => cards[i]);
  const moves = game.moves + 1;
  if (a.id === b.id) {
    const done = cards.map((x) => (x.k === a.k || x.k === b.k ? { ...x, done: true } : x));
    return { game: { ...game, cards: done, pending: [], moves, matched: game.matched + 1 }, event: 'match' };
  }
  return { game: { ...game, cards, pending, moves }, event: 'miss' };
}
export function settle(game) {
  return { ...game, cards: game.cards.map((x) => (x.done ? x : { ...x, open: false })), pending: [] };
}

export default {
  id: 'memory', title: '카드 짝맞추기', eyebrow: 'MEMORY MATCH', tagline: '같은 친구 두 장을 찾아 줘', icon: 175, color: '#f9e9e3',
  desc: '뒤집힌 카드를 두 장씩 열어 같은 포켓몬을 찾아 줘. 적은 횟수로 끝낼수록 좋은 기록이야.',
  pausable: true,
  lowerIsBetter: true, unit: '회', format: (v) => `${v}번 만에`,
  options: [
    { key: 'size', label: '판 크기', default: '4x3', choices: [{ v: '4x3', label: '4×3', hint: '6쌍 · 가볍게' }, { v: '4x4', label: '4×4', hint: '8쌍 · 집중해서' }] },
    { key: 'mode', label: '모드', default: 'free', choices: [{ v: 'free', label: '자유', hint: '시간 제한 없이' }, { v: 'timed', label: '제한시간', hint: '4×3은 60초, 4×4는 90초' }] },
  ],
  recordKey: (o) => `${o.size}-${o.mode}`,
  mount(host, opts, api) {
    let game = { cards: makeBoard(opts.size), pending: [], moves: 0, matched: 0 };
    const pairs = game.cards.length / 2;
    const limit = opts.mode === 'timed' ? (opts.size === '4x4' ? 90 : 60) : 0;
    let elapsed = 0, last = performance.now(), dead = false, paused = false, busy = false;
    const grid = el('div', 'memory-grid ' + (opts.size === '4x4' ? 'g16' : 'g12'), '', { role: 'grid', 'aria-label': '카드 판' });
    const status = el('p', 'quiz-feedback', '', { 'aria-live': 'polite' });
    const buttons = game.cards.map((c) => {
      const b = button('', 'mem-card', () => onFlip(c.k), { 'aria-label': `카드 ${c.k + 1}, 뒤집기` });
      const inner = el('span', 'mem-inner');
      const back = el('span', 'mem-back', '', { 'aria-hidden': 'true' });
      const front = el('span', 'mem-front');
      front.append(pokeImg(c.id, { cls: 'mem-img' }), el('small', '', c.name));
      inner.append(back, front);
      b.append(inner);
      grid.append(b);
      return b;
    });
    host.replaceChildren(grid, status);

    const fmt = (s) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;
    const hud = () => api.hud([['짝', `${game.matched}/${pairs}`], ['횟수', game.moves], [limit ? '남은 시간' : '시간', fmt(limit ? Math.max(0, limit - elapsed) : elapsed)]]);
    function paint() {
      game.cards.forEach((c, k) => {
        const b = buttons[k];
        b.classList.toggle('open', c.open || c.done);
        b.classList.toggle('done', c.done);
        b.disabled = c.done;
        b.setAttribute('aria-label', c.open || c.done ? `${c.name}${c.done ? ' (짝 완료)' : ''}` : `카드 ${k + 1}, 뒤집기`);
      });
      hud();
    }
    function onFlip(k) {
      if (busy || paused || dead) return;
      const r = flip(game, k);
      if (r.event === 'ignore') return;
      game = r.game;
      api.sfx(r.event === 'match' ? 'match' : 'flip');
      paint();
      if (r.event === 'match') {
        status.textContent = `${game.cards[k].name} 짝 완성!`;
        api.env.discover(game.cards[k].id);
        if (game.matched === pairs) end(true);
      } else if (r.event === 'miss') {
        busy = true;
        setTimeout(() => { if (dead) return; game = settle(game); busy = false; paint(); }, 750);
      }
    }
    function end(cleared) {
      dead = true;
      cancelAnimationFrame(raf);
      api.finish({
        score: game.moves, record: cleared ? game.moves : null, headline: cleared ? `${game.moves}번 만에 완성!` : '시간이 다 됐어요',
        eyebrow: 'MEMORY MATCH', pokemon: game.cards.find((c) => c.done)?.id || 175,
        lines: [`걸린 시간 ${fmt(elapsed)}`, `찾은 짝 ${game.matched}/${pairs}`, cleared ? '' : '제한시간 안에 다 찾지 못해 기록에 넣지 않았어요.'].filter(Boolean),
      });
    }
    let raf = 0, shown = 0;
    const loop = (t) => {
      if (dead) return;
      if (!paused) {
        elapsed += Math.min(1, (t - last) / 1000);
        if (limit && elapsed >= limit) { elapsed = limit; hud(); return end(false); }
      }
      last = t;
      if (Math.floor(elapsed) !== shown) { shown = Math.floor(elapsed); hud(); }
      raf = requestAnimationFrame(loop);
    };
    paint();
    raf = requestAnimationFrame(loop);
    return {
      pause() { paused = true; },
      resume() { paused = false; last = performance.now(); },
      destroy() { dead = true; cancelAnimationFrame(raf); },
    };
  },
};
