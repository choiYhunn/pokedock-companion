// Common game shell: hub list, per-game setup (difficulty / length), HUD, pause, background
// handling, result screen and record keeping. Each game only implements mount(host, opts, api).
import { el, button, pokeImg } from '../ui.js';
import { sfx, setSoundEnabled, unlockAudio } from '../sfx.js';

export function createArcade(env, games) {
  const $ = (id) => document.getElementById(id);
  const root = $('arcade'), body = $('arcade-body'), hud = $('arcade-hud'), title = $('arcade-title'), eyebrow = $('arcade-eyebrow');
  const pauseBtn = $('arcade-pause'), soundBtn = $('arcade-sound'), backBtn = $('arcade-back');
  let current = null; // {game, opts, instance, paused, ended}
  let screen = 'closed'; // closed | hub | setup | play | result
  let lastFocus = null;

  const recordText = (game, value) => (value == null ? '기록 없음' : game.format ? game.format(value) : `${value}${game.unit || '점'}`);

  function setHeader(t, e) { title.textContent = t; eyebrow.textContent = e; }
  function renderSound() {
    const on = env.getState().sound;
    soundBtn.textContent = on ? '♪' : '×';
    soundBtn.setAttribute('aria-pressed', String(on));
    soundBtn.setAttribute('aria-label', on ? '게임 소리 끄기' : '게임 소리 켜기');
    soundBtn.title = soundBtn.getAttribute('aria-label');
  }

  function open(gameId) {
    if (screen === 'closed') lastFocus = document.activeElement;
    root.hidden = false;
    document.body.classList.add('arcade-open');
    renderSound();
    if (gameId && games[gameId]) setup(gameId);
    else hub();
  }

  function close() {
    stopCurrent();
    root.hidden = true;
    screen = 'closed';
    document.body.classList.remove('arcade-open');
    env.onClose?.();
    lastFocus?.focus?.();
  }

  function stopCurrent() {
    if (current?.instance) { try { current.instance.destroy?.(); } catch { /* ignore */ } }
    current = null;
    hud.replaceChildren();
    pauseBtn.hidden = true;
  }

  function hub() {
    stopCurrent();
    screen = 'hub';
    setHeader('포켓몬 놀이터', 'POKÉDOCK ARCADE');
    const s = env.getState();
    const grid = el('div', 'arcade-grid');
    for (const g of Object.values(games)) {
      const best = s.games[g.id]?.best || {};
      const values = Object.values(best);
      const top = values.length ? (g.lowerIsBetter ? Math.min(...values) : Math.max(...values)) : null;
      const card = button('', 'game-card', () => setup(g.id), { 'aria-label': `${g.title} 열기` });
      card.style.setProperty('--gc', g.color || '#efe5f6');
      const art = el('span', 'game-card-art');
      art.append(pokeImg(g.icon, { cls: 'game-card-img' }));
      const text = el('span', 'game-card-text');
      text.append(el('span', 'eyebrow', g.eyebrow), el('b', '', g.title), el('small', '', g.tagline));
      const meta = el('span', 'game-card-meta', g.hubMeta ? g.hubMeta(s) : top == null ? '첫 도전!' : `최고 ${recordText(g, top)}`);
      card.append(art, text, meta);
      grid.append(card);
    }
    const note = el('p', 'arcade-note', '기록은 이 기기에만 저장돼요. 서버나 다른 사람과의 비교 기록은 없어요.');
    body.replaceChildren(grid, note);
    backBtn.setAttribute('aria-label', '놀이터 닫기');
    body.scrollTop = 0;
    grid.querySelector('button')?.focus({ preventScroll: true });
  }

  function setup(gameId) {
    stopCurrent();
    const g = games[gameId];
    screen = 'setup';
    setHeader(g.title, g.eyebrow);
    backBtn.setAttribute('aria-label', '게임 목록으로');
    const s = env.getState();
    const saved = s.games[g.id]?.lastOpts || {};
    const opts = {};
    const wrap = el('div', 'game-setup');
    const hero = el('div', 'setup-hero');
    hero.style.setProperty('--gc', g.color || '#efe5f6');
    hero.append(pokeImg(g.icon, { cls: 'setup-img' }));
    const copy = el('div', 'setup-copy');
    copy.append(el('p', '', g.desc));
    hero.append(copy);
    wrap.append(hero);
    for (const o of g.options || []) {
      const group = el('div', 'seg-group', '', { role: 'radiogroup', 'aria-label': o.label });
      const label = el('span', 'eyebrow', o.label);
      const row = el('div', 'seg');
      opts[o.key] = o.choices.some((c) => c.v === saved[o.key]) ? saved[o.key] : o.default;
      const hint = el('small', 'seg-hint');
      const paint = () => {
        for (const b of row.children) {
          const on = b.dataset.v === String(opts[o.key]);
          b.classList.toggle('selected', on);
          b.setAttribute('aria-checked', String(on));
        }
        hint.textContent = o.choices.find((c) => c.v === opts[o.key])?.hint || '';
        bestLine.textContent = g.noRecord ? '' : '최고 기록 · ' + recordText(g, s.games[g.id]?.best?.[g.recordKey(opts)]);
      };
      for (const c of o.choices) {
        const b = button(c.label, '', () => { opts[o.key] = c.v; paint(); }, { role: 'radio', 'data-v': String(c.v) });
        row.append(b);
      }
      group.append(label, row, hint);
      wrap.append(group);
      group.paint = paint;
    }
    const bestLine = el('p', 'setup-best');
    const problem = g.precheck?.(env) || null;
    const start = button(problem ? '이 기기에서는 플레이할 수 없어요' : '시작하기', 'btn solid setup-start', () => {
      unlockAudio();
      play(g, { ...opts });
    });
    if (problem) start.disabled = true;
    wrap.append(bestLine);
    if (problem) wrap.append(el('p', 'setup-problem', problem));
    if (g.extraSetup) wrap.append(g.extraSetup(env));
    wrap.append(start);
    body.replaceChildren(wrap);
    for (const grp of wrap.querySelectorAll('.seg-group')) grp.paint();
    if (!g.options?.length) bestLine.textContent = g.noRecord ? '' : '최고 기록 · ' + recordText(g, s.games[g.id]?.best?.[g.recordKey(opts)]);
    start.focus({ preventScroll: true });
  }

  function play(g, opts) {
    stopCurrent();
    screen = 'play';
    const host = el('div', 'game-host');
    body.replaceChildren(host);
    body.scrollTop = 0;
    env.update((s) => { s.games[g.id] = { plays: 0, best: {}, lastDay: '', ...(s.games[g.id] || {}), lastOpts: opts }; });
    const run = { game: g, opts, paused: false, ended: false, instance: null };
    current = run;
    const api = {
      env,
      sfx: (n) => sfx(n),
      hud(items) {
        if (current !== run) return;
        hud.replaceChildren(...items.map(([k, v]) => { const c = el('span', 'hud-chip'); c.append(el('small', '', k), el('b', '', String(v))); return c; }));
      },
      finish(result) {
        if (current !== run || run.ended) return;
        run.ended = true;
        showResult(g, opts, result);
      },
      get paused() { return run.paused; },
    };
    pauseBtn.hidden = !g.pausable;
    run.instance = g.mount(host, opts, api) || {};
  }

  function pause(reason) {
    if (!current || current.paused || current.ended || screen !== 'play') return;
    current.paused = true;
    current.instance.pause?.();
    const layer = el('div', 'pause-layer', '', { role: 'dialog', 'aria-label': '일시정지' });
    const box = el('div', 'pause-box');
    box.append(el('b', '', reason === 'hidden' ? '잠깐 쉬는 중이에요' : '일시정지'), el('p', '', '준비되면 이어서 놀자!'));
    const resume = button('계속하기', 'btn solid', () => { layer.remove(); current.paused = false; current.instance.resume?.(); });
    const restart = button('처음부터', 'btn light', () => play(current.game, current.opts));
    const quit = button('그만하기', 'btn text-btn', () => setup(current.game.id));
    box.append(resume, restart, quit);
    layer.append(box);
    body.append(layer);
    resume.focus();
  }

  function showResult(g, opts, r) {
    screen = 'result';
    pauseBtn.hidden = true;
    const value = r.record === undefined ? r.score : r.record;
    const rec = env.recordGame(g.id, g.recordKey(opts), value ?? null, !!g.lowerIsBetter); // null = play counted, no record
    const box = el('div', 'game-result');
    if (r.pokemon) box.append(pokeImg(r.pokemon, { cls: 'result-img' }));
    box.append(el('span', 'eyebrow', r.eyebrow || 'RESULT'), el('div', 'result-score', r.headline || recordText(g, value)));
    if (rec.isBest && rec.prev != null) box.append(el('span', 'result-badge', '✦ 새 최고 기록!'));
    else if (rec.isBest) box.append(el('span', 'result-badge', '✦ 첫 기록!'));
    else if (rec.prev != null) box.append(el('small', 'result-prev', '최고 기록 ' + recordText(g, g.lowerIsBetter ? Math.min(rec.prev, value) : Math.max(rec.prev, value))));
    for (const line of r.lines || []) box.append(el('p', '', line));
    if (r.extra) box.append(r.extra);
    const actions = el('div', 'result-actions');
    actions.append(button('다시 하기', 'btn solid', () => play(g, opts)), button('다른 게임', 'btn light', hub));
    box.append(actions);
    body.replaceChildren(box);
    body.scrollTop = 0;
    if (rec.isBest) sfx('match');
    env.afterGame?.(g.id);
    actions.querySelector('button').focus({ preventScroll: true });
  }

  backBtn.addEventListener('click', () => {
    if (screen === 'play') { if (current?.game.pausable && !current.paused) return pause('button'); return setup(current.game.id); }
    if (screen === 'setup' || screen === 'result') return hub();
    close();
  });
  pauseBtn.addEventListener('click', () => pause('button'));
  soundBtn.addEventListener('click', () => {
    env.update((s) => { s.sound = !s.sound; });
    setSoundEnabled(env.getState().sound);
    renderSound();
    if (env.getState().sound) sfx('tick');
  });
  document.addEventListener('visibilitychange', () => {
    if (document.hidden && screen === 'play') {
      if (current?.game.pausable) pause('hidden');
      else current?.instance?.hidden?.();
    }
  });
  root.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') { e.stopPropagation(); backBtn.click(); }
  });

  return { open, close, get screen() { return screen; }, pause };
}
