// Game 4 — 실루엣 퀴즈 (V17's five-round quiz, extended): 5/10/20 questions, three difficulties,
// streaks, a wrong-answer review deck, least-recently-seen question order and image-failure skips.
import { POKEDEX, PARTNERS, byId } from '../pokedex.js';
import { el, button, pokeImg, sample, freshDeck } from '../ui.js';
import { cryChoices } from './cry.js';

const HARD_SECONDS = 10;

export default {
  id: 'silhouette', title: '실루엣 퀴즈', eyebrow: "WHO'S THAT?", tagline: '그림자만 보고 맞혀 봐', icon: 94, color: '#e9e1f3',
  desc: '까만 실루엣의 주인공을 맞혀 줘. 틀린 친구는 오답 노트에 모아 두었다가 복습할 수 있어.',
  pausable: true,
  options: [
    { key: 'mode', label: '모드', default: 'all', choices: [{ v: 'all', label: '도전', hint: '새 문제를 골고루' }, { v: 'review', label: '오답 복습', hint: '틀렸던 친구만 다시 · 기록에는 반영하지 않아요' }] },
    { key: 'diff', label: '난도', default: 'normal', choices: [
      { v: 'easy', label: '쉬움', hint: '파트너 8종 · 3지선다' },
      { v: 'normal', label: '보통', hint: `도감 ${POKEDEX.length}종 · 4지선다` },
      { v: 'hard', label: '어려움', hint: `비슷한 타입 선택지 · 문제당 ${HARD_SECONDS}초` },
    ] },
    { key: 'len', label: '문제 수', default: 10, choices: [{ v: 5, label: '5' }, { v: 10, label: '10' }, { v: 20, label: '20' }] },
  ],
  recordKey: (o) => `${o.diff}-${o.len}`, unit: '개', format: (v) => `${v}개 정답`,
  extraSetup(env) {
    const r = env.getState().review;
    return el('p', 'setup-note', r.length ? `오답 노트: ${r.map((id) => byId(id)?.name).join(', ')}` : '오답 노트가 비어 있어요. 멋져!');
  },
  mount(host, opts, api) {
    const env = api.env;
    const review = opts.mode === 'review';
    const pool = review ? env.getState().review.map(byId).filter(Boolean) : opts.diff === 'easy' ? PARTNERS : POKEDEX;
    const choicePool = opts.diff === 'easy' ? PARTNERS : POKEDEX;
    if (!pool.length) {
      host.replaceChildren(el('p', 'setup-note', '복습할 오답이 없어요! 도전 모드로 새 문제를 풀어 봐.'));
      setTimeout(() => api.finish({ score: 0, record: null, headline: '복습할 문제 없음', lines: ['오답 노트가 비어 있어요.'] }), 1200);
      return {};
    }
    const deck = freshDeck(pool, review ? Math.min(opts.len, pool.length) : opts.len, env.getState().seen);
    const nChoices = opts.diff === 'easy' ? 3 : 4;
    let i = 0, correct = 0, streak = 0, bestStreak = 0, skipped = 0, dead = false, timer = 0, left = HARD_SECONDS, locked = false;
    const wrongIds = [];

    const hud = () => api.hud([['문제', `${Math.min(i + 1, deck.length)}/${deck.length}`], ['정답', correct], ['연속', streak]]);
    const stopTimer = () => { clearInterval(timer); timer = 0; };

    function answer(choice, btn, choices, img, feedback, target) {
      if (locked) return;
      locked = true;
      stopTimer();
      for (const x of choices.children) { x.disabled = true; if (Number(x.dataset.id) === target.id) x.classList.add('correct'); }
      img.classList.remove('hidden');
      img.alt = target.name;
      const ok = choice?.id === target.id;
      if (ok) {
        correct++; streak++; bestStreak = Math.max(bestStreak, streak); api.sfx('correct');
        if (review) env.update((s) => { s.review = s.review.filter((id) => id !== target.id); });
      } else {
        streak = 0; wrongIds.push(target.id); btn?.classList.add('wrong'); api.sfx('wrong');
        env.update((s) => { s.review = [target.id, ...s.review.filter((id) => id !== target.id)].slice(0, 40); });
      }
      env.discover(target.id);
      env.markSeen(target.id);
      feedback.textContent = ok ? (streak >= 3 ? `${streak}연속 정답! ${target.name}` : `정답! ${target.name}`) : choice ? `아쉬워! 정답은 ${target.name}` : `시간 끝! 정답은 ${target.name}`;
      hud();
      setTimeout(() => { if (!dead) { i++; render(); } }, 1050);
    }

    function render() {
      if (i >= deck.length) return finish();
      locked = false;
      hud();
      const target = deck[i];
      const body = el('div', 'quiz-body');
      body.append(el('p', 'quiz-q', `${i + 1} / ${deck.length} · 실루엣의 주인공은 누구일까?`));
      const feedback = el('p', 'quiz-feedback', '', { 'aria-live': 'polite' });
      const bar = el('div', 'time-bar', '', { 'aria-hidden': 'true' });
      const choices = el('div', 'choice-grid c' + nChoices);
      const img = pokeImg(target.id, {
        cls: 'quiz-image hidden', alt: '포켓몬 실루엣',
        onLoad: () => { if (opts.diff === 'hard' && !timer && !locked) startTimer(); },
        onFail: () => {
          if (locked) return;
          locked = true;
          stopTimer();
          skipped++;
          feedback.textContent = '이미지를 불러오지 못해 이 문제는 건너뛸게요.';
          setTimeout(() => { if (!dead) { i++; render(); } }, 1100);
        },
      });
      const options = review ? sample([target, ...sample(choicePool.filter((p) => p.id !== target.id), nChoices - 1)], nChoices) : cryChoices(target, choicePool, nChoices, opts.diff === 'hard');
      for (const c of options) {
        const b = button(c.name, 'choice', () => answer(c, b, choices, img, feedback, target), { 'data-id': String(c.id) });
        choices.append(b);
      }
      function startTimer() {
        left = HARD_SECONDS;
        bar.style.setProperty('--p', '1');
        timer = setInterval(() => {
          if (api.paused) return;
          left -= 0.1;
          bar.style.setProperty('--p', String(Math.max(0, left / HARD_SECONDS)));
          if (left <= 0) answer(null, null, choices, img, feedback, target);
        }, 100);
      }
      body.append(img);
      if (opts.diff === 'hard') body.append(bar);
      body.append(choices, feedback);
      host.replaceChildren(body);
      // preload the next silhouette
      if (deck[i + 1]) pokeImg(deck[i + 1].id);
    }

    function finish() {
      const answered = deck.length - skipped;
      api.finish({
        score: correct, record: review || skipped ? null : correct, headline: `${correct} / ${answered}`, eyebrow: review ? 'REVIEW' : 'SILHOUETTE', pokemon: deck[deck.length - 1]?.id,
        lines: [
          `최고 연속 정답 ${bestStreak}`,
          skipped ? `이미지 문제로 ${skipped}개를 건너뛰어 이번 판은 기록에 넣지 않았어요.` : '',
          wrongIds.length ? '오답 노트에 담았어요: ' + [...new Set(wrongIds)].map((id) => byId(id)?.name).join(', ') : '오답 없이 완벽해!',
        ].filter(Boolean),
      });
    }
    render();
    return { destroy() { dead = true; stopTimer(); } };
  },
};
