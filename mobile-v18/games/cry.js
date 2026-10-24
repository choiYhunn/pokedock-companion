// Game 1 — 울음소리 퀴즈. Cries stream from the PokeAPI cries repository (OGG). They are never
// committed here; the user may store them on this device from the offline manager.
import { POKEDEX, PARTNERS, cryUrl } from '../pokedex.js';
import { el, button, pokeImg, sample, freshDeck } from '../ui.js';

export function oggSupported() {
  try { return !!new Audio().canPlayType('audio/ogg; codecs="vorbis"'); } catch { return false; }
}

const blobs = new Map(); // id -> object URL for this session
async function loadCry(id) {
  if (blobs.has(id)) return blobs.get(id);
  const res = await fetch(cryUrl(id), { mode: 'cors', credentials: 'omit' });
  if (!res.ok) throw new Error('HTTP ' + res.status);
  const url = URL.createObjectURL(await res.blob());
  blobs.set(id, url);
  return url;
}

// Distractors: on hard prefer Pokémon sharing a type with the answer.
export function cryChoices(answer, pool, n, hard, rnd = Math.random) {
  const others = pool.filter((p) => p.id !== answer.id);
  let picks = [];
  if (hard) picks = sample(others.filter((p) => p.types.some((t) => answer.types.includes(t))), n - 1, rnd);
  picks = [...picks, ...sample(others.filter((p) => !picks.includes(p)), n - 1 - picks.length, rnd)];
  return sample([answer, ...picks], n, rnd);
}

export default {
  id: 'cry', title: '울음소리 퀴즈', eyebrow: 'LISTEN & GUESS', tagline: '소리만 듣고 누구인지 맞혀 봐', icon: 25, color: '#f7efd9',
  desc: '포켓몬의 울음소리를 듣고 네 친구 중 주인공을 골라 줘. 연속으로 맞히면 콤보가 쌓여!',
  options: [
    { key: 'diff', label: '난도', default: 'normal', choices: [
      { v: 'easy', label: '쉬움', hint: '파트너 8종 · 그림과 이름 보기 · 다시 듣기 자유' },
      { v: 'normal', label: '보통', hint: `도감 ${POKEDEX.length}종 · 이름 보기 · 다시 듣기 자유` },
      { v: 'hard', label: '어려움', hint: '같은 타입끼리 헷갈리게 · 다시 듣기 1번' },
    ] },
    { key: 'len', label: '문제 수', default: 5, choices: [{ v: 5, label: '5문제' }, { v: 10, label: '10문제' }] },
  ],
  recordKey: (o) => `${o.diff}-${o.len}`, unit: '개', format: (v) => `${v}개 정답`,
  precheck: () => (oggSupported() ? null : '이 브라우저는 울음소리 파일 형식(OGG)을 재생하지 못해요. 최신 Chrome이나 Safari에서 다시 시도해 줘.'),
  extraSetup() {
    return el('p', 'setup-note', '울음소리는 인터넷에서 불러와요. 오프라인으로 하려면 설정 → 오프라인 콘텐츠에서 울음소리를 이 기기에 저장해 줘.');
  },
  mount(host, opts, api) {
    const env = api.env;
    const pool = opts.diff === 'easy' ? PARTNERS : POKEDEX;
    const deck = freshDeck(pool, opts.len, env.getState().seen);
    const audio = new Audio();
    audio.preload = 'auto';
    let i = 0, correct = 0, combo = 0, bestCombo = 0, skipped = 0, failsInRow = 0, replays = 0, locked = false, dead = false;
    const wrong = [];
    const replayLimit = opts.diff === 'hard' ? 1 : Infinity;

    const hudUpdate = () => api.hud([['문제', `${Math.min(i + 1, deck.length)}/${deck.length}`], ['정답', correct], ['콤보', combo]]);

    async function playCurrent(stage, status) {
      const id = deck[i].id;
      status.textContent = '불러오는 중…';
      try {
        const url = await loadCry(id);
        if (dead) return;
        audio.src = url;
        await audio.play();
        status.textContent = opts.diff === 'hard' ? `다시 듣기 ${Math.max(0, replayLimit + 1 - replays)}번 남음` : '';
        stage.classList.add('playing');
        setTimeout(() => stage.classList.remove('playing'), 900);
        failsInRow = 0;
      } catch (e) {
        if (dead) return;
        if (e?.name === 'NotAllowedError') { replays = Math.max(0, replays - 1); status.textContent = '브라우저가 자동 재생을 막았어요. ♪ 버튼을 눌러 들어 줘.'; return; }
        failsInRow++;
        status.textContent = navigator.onLine === false ? '오프라인이라 이 울음소리를 불러오지 못했어요.' : '울음소리를 불러오지 못했어요.';
        showSkip();
      }
    }

    let skipBtn = null;
    function showSkip() {
      if (skipBtn) return;
      skipBtn = button('이 문제 건너뛰기', 'btn light', () => { if (locked) return; locked = true; skipped++; i++; render(); });
      host.querySelector('.cry-panel')?.append(skipBtn);
      if (failsInRow >= 3) api.finish(summary('울음소리를 연달아 불러오지 못해 게임을 멈췄어요. 인터넷 연결을 확인해 줘.'));
    }

    function summary(note) {
      const answered = deck.length - skipped;
      return {
        score: correct, record: answered === deck.length ? correct : null, headline: `${correct} / ${answered}`,
        eyebrow: 'CRY QUIZ', pokemon: deck[0]?.id,
        lines: [
          `최고 콤보 ${bestCombo}`, skipped ? `건너뛴 문제 ${skipped}개 (기록에는 반영하지 않았어요)` : '',
          wrong.length ? '다시 들어 볼 친구: ' + wrong.map((p) => p.name).join(', ') : '모두 맞혔어! 귀가 정말 좋구나 ♡', note || '',
        ].filter(Boolean),
      };
    }

    function render() {
      if (i >= deck.length) return api.finish(summary());
      locked = false; replays = 0; skipBtn = null;
      hudUpdate();
      const answer = deck[i];
      const panel = el('div', 'cry-panel');
      const stage = button('', 'cry-stage', () => {
        if (locked) return;
        if (replays >= replayLimit + 1) return;
        replays++;
        playCurrent(stage, status);
      }, { 'aria-label': '울음소리 듣기' });
      stage.append(el('span', 'cry-wave', '♪'), el('span', 'cry-label', '누구의 울음소리일까?'));
      const status = el('p', 'cry-status', '', { 'aria-live': 'polite' });
      const choices = el('div', 'choice-grid' + (opts.diff === 'easy' ? ' with-art' : ''));
      const feedback = el('p', 'quiz-feedback', '', { 'aria-live': 'polite' });
      for (const c of cryChoices(answer, pool, 4, opts.diff === 'hard')) {
        const b = button('', 'choice', () => {
          if (locked) return;
          locked = true;
          audio.pause();
          const ok = c.id === answer.id;
          for (const x of choices.children) { x.disabled = true; if (Number(x.dataset.id) === answer.id) x.classList.add('correct'); }
          if (ok) { correct++; combo++; bestCombo = Math.max(bestCombo, combo); api.sfx('correct'); }
          else { combo = 0; wrong.push(answer); b.classList.add('wrong'); api.sfx('wrong'); }
          env.discover(answer.id);
          env.markSeen(answer.id);
          feedback.textContent = ok ? (combo >= 3 ? `${combo}콤보! ${answer.name} 정답!` : `정답! ${answer.name}`) : `아쉬워! 정답은 ${answer.name}`;
          stage.replaceChildren(pokeImg(answer.id, { cls: 'cry-reveal' }));
          hudUpdate();
          setTimeout(() => { if (!dead) { i++; render(); } }, 1300);
        }, { 'data-id': String(c.id) });
        if (opts.diff === 'easy') b.append(pokeImg(c.id, { cls: 'choice-img' }));
        b.append(el('span', '', c.name));
        choices.append(b);
      }
      panel.append(stage, status);
      host.replaceChildren(panel, choices, feedback);
      replays = 1;
      playCurrent(stage, status);
      // warm the next cry so the following question starts instantly
      if (deck[i + 1]) loadCry(deck[i + 1].id).catch(() => {});
    }
    render();
    return {
      hidden() { audio.pause(); },
      destroy() { dead = true; audio.pause(); audio.removeAttribute('src'); },
    };
  },
};
