// Game 7 — 오늘의 포켓몬. One Pokémon, one type quiz and one small mission per KST day. A stamp is
// recorded once per day on this device; it is a memento, not a prize or a server-side reward.
import { POKEDEX, typesKo } from '../pokedex.js';
import { dailyPick, kstDay, addDays, hashDay } from '../core.js';
import { el, button, pokeImg, shuffle } from '../ui.js';

export function typeQuiz(pokemon, day) {
  const answer = typesKo(pokemon);
  const others = [...new Set(POKEDEX.map(typesKo))].filter((t) => t !== answer);
  let seed = hashDay(day, 3);
  const rnd = () => ((seed = Math.imul(seed ^ (seed >>> 15), 2246822507) >>> 0) / 4294967296);
  return { answer, choices: shuffle([answer, ...shuffle(others, rnd).slice(0, 3)], rnd) };
}

export default {
  id: 'daily', title: '오늘의 포켓몬', eyebrow: "TODAY'S FRIEND", tagline: '하루 한 번 새 친구와 미션', icon: 385, color: '#f8f0d8',
  desc: '매일 한 마리의 포켓몬이 찾아와. 타입 퀴즈를 맞히거나 작은 미션을 끝내면 오늘의 도장을 찍어 줄게. 도장은 이 기기에만 기록돼.',
  noRecord: true, options: [],
  recordKey: () => 'day',
  hubMeta: (s) => (s.daily[kstDay()]?.stamp ? '오늘 도장 완료 ✓' : s.daily[kstDay()]?.revealed ? '도장 찍으러 가기' : '새 친구가 기다려요'),
  mount(host, opts, api) {
    const env = api.env;
    const day = kstDay();
    const { pokemon, mission } = dailyPick(day);
    const quiz = typeQuiz(pokemon, day);
    const rec = () => env.getState().daily[day] || { revealed: false, answered: null, correct: false, mission: false, stamp: false };
    const save = (patch) => env.update((s) => { s.daily[day] = { ...rec(), ...patch }; });
    api.hud([['날짜', day.slice(5).replace('-', '.')]]);

    function stampIfEarned() {
      const r = rec();
      if (!r.revealed) return false;
      const missionDone = r.mission || mission.check(env.getState(), day);
      if (missionDone && !r.mission) save({ mission: true });
      if (!r.stamp && (r.correct || missionDone)) {
        save({ stamp: true });
        env.award('daily');
        api.sfx('stamp');
        return true;
      }
      return false;
    }

    function render() {
      const r = rec();
      const wrap = el('div', 'daily');
      const card = el('div', 'daily-card' + (r.revealed ? ' revealed' : ''));
      card.style.setProperty('--dc', pokemon.color);
      if (!r.revealed) {
        const reveal = button('', 'daily-reveal', () => {
          save({ revealed: true });
          env.discover(pokemon.id);
          env.markPlayed('daily');
          api.sfx('start');
          render();
        }, { 'aria-label': '오늘의 포켓몬 공개하기' });
        reveal.append(el('span', 'daily-q', '?'), el('b', '', '오늘의 친구 공개하기'), el('small', '', '눌러서 카드를 뒤집어 줘'));
        card.append(reveal);
        wrap.append(card);
        host.replaceChildren(wrap);
        return;
      }
      card.append(pokeImg(pokemon.id, { cls: 'daily-img' }));
      const info = el('div', 'daily-info');
      info.append(el('span', 'eyebrow', `NO. ${String(pokemon.id).padStart(3, '0')} · ${typesKo(pokemon)}`), el('h3', '', pokemon.name), el('p', '', `“${pokemon.line}”`));
      card.append(info);
      wrap.append(card);

      const q = el('section', 'daily-section');
      q.append(el('span', 'eyebrow', 'TODAY QUIZ'), el('b', '', `${pokemon.name}의 타입은 무엇일까?`));
      const choices = el('div', 'choice-grid c4');
      for (const c of quiz.choices) {
        const b = button(c, 'choice', () => {
          if (rec().answered != null) return;
          const ok = c === quiz.answer;
          save({ answered: c, correct: ok });
          api.sfx(ok ? 'correct' : 'wrong');
          stampIfEarned();
          render();
        });
        if (r.answered != null) {
          b.disabled = true;
          if (c === quiz.answer) b.classList.add('correct');
          else if (c === r.answered) b.classList.add('wrong');
        }
        choices.append(b);
      }
      q.append(choices);
      if (r.answered != null) q.append(el('p', 'quiz-feedback', r.correct ? '정답! 오늘의 퀴즈 완료.' : `정답은 ${quiz.answer}. 퀴즈는 하루 한 번만 풀 수 있어요.`));
      wrap.append(q);

      const m = el('section', 'daily-section');
      const done = r.mission || mission.check(env.getState(), day);
      m.append(el('span', 'eyebrow', 'SMALL MISSION'), el('b', '', mission.text), el('p', 'quiz-feedback', done ? '미션 완료 ✓' : '아직이야. 끝내고 다시 와서 확인해 줘.'));
      if (!done) m.append(button('미션 확인하기', 'btn light', () => { if (!stampIfEarned()) api.sfx('tick'); render(); }));
      wrap.append(m);

      const stamps = el('section', 'daily-section stamps');
      stamps.append(el('span', 'eyebrow', 'MY STAMPS · 최근 7일'));
      const row = el('div', 'stamp-row');
      const all = env.getState().daily;
      for (let k = 6; k >= 0; k--) {
        const d = addDays(day, -k);
        const has = all[d]?.stamp;
        row.append(el('span', 'stamp' + (has ? ' on' : '') + (d === day ? ' today' : ''), has ? '★' : d.slice(8), { title: d + (has ? ' 도장' : '') }));
      }
      const total = Object.values(all).filter((x) => x.stamp).length;
      stamps.append(row, el('small', '', `지금까지 모은 도장 ${total}개 · 이 기기에만 기록돼요`));
      wrap.append(stamps);
      host.replaceChildren(wrap);
      if (rec().stamp) {
        wrap.prepend(el('p', 'daily-done', '오늘의 도장 쾅! 내일 또 새로운 친구가 와요 ♡'));
      }
    }
    stampIfEarned();
    render();
    return {};
  },
};
