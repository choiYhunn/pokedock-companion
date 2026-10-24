// Game 6 — 반응속도. The partner hides, then pops out; tap as fast as you can. Pressing before it
// appears is a false start and that round is replayed. Times use the event timestamp.
import { byId } from '../pokedex.js';
import { el, button, pokeImg } from '../ui.js';

export const reactionVerdict = (ms) => (ms < 220 ? '번개 같아!' : ms < 300 ? '아주 빨라!' : ms < 400 ? '좋은 반응!' : '천천히 해도 괜찮아.');

export default {
  id: 'reaction', title: '반응속도', eyebrow: 'QUICK PAW', tagline: '튀어나오는 순간 터치!', icon: 417, color: '#e5f0f8',
  desc: '파트너가 숨어 있다가 “지금!” 하고 튀어나오면 최대한 빨리 눌러 줘. 먼저 누르면 부정 출발이야.',
  pausable: true, lowerIsBetter: true, unit: 'ms', format: (v) => `${v}ms`,
  options: [{ key: 'rounds', label: '라운드', default: 5, choices: [{ v: 3, label: '3번' }, { v: 5, label: '5번' }] }],
  recordKey: (o) => `avg-${o.rounds}`,
  mount(host, opts, api) {
    const env = api.env;
    const p = byId(env.getState().character) || byId(94);
    const times = [];
    let phase = 'idle', t0 = 0, timer = 0, falseStarts = 0, dead = false;
    const stage = button('', 'rx-stage', () => {}, { 'aria-label': '반응 버튼' });
    const img = pokeImg(p.id, { cls: 'rx-img' });
    const label = el('span', 'rx-label');
    stage.append(img, label);
    const info = el('p', 'quiz-feedback', '', { 'aria-live': 'polite' });
    host.replaceChildren(stage, info);
    const hud = () => api.hud([['라운드', `${Math.min(times.length + 1, opts.rounds)}/${opts.rounds}`], ['최고', times.length ? Math.min(...times) + 'ms' : '-'], ['부정 출발', falseStarts]]);

    function arm() {
      clearTimeout(timer);
      phase = 'wait';
      stage.className = 'rx-stage wait';
      label.textContent = '기다려…';
      img.classList.remove(p.behavior);
      hud();
      timer = setTimeout(() => {
        if (dead || api.paused) return;
        phase = 'go';
        stage.className = 'rx-stage go';
        label.textContent = '지금!';
        if (!env.reduceMotion()) { void img.offsetWidth; img.classList.add(p.behavior); }
        requestAnimationFrame(() => { t0 = performance.now(); });
        api.sfx('go');
      }, 1500 + Math.random() * 2500);
    }

    function press(ts) {
      if (dead || api.paused) return;
      if (phase === 'idle' || phase === 'shown') return arm();
      if (phase === 'wait') {
        clearTimeout(timer);
        falseStarts++;
        phase = 'shown';
        stage.className = 'rx-stage early';
        label.textContent = '부정 출발! 다시 눌러서 재도전';
        info.textContent = `${p.name}: “앗, 아직이야!”`;
        api.sfx('wrong');
        hud();
        return;
      }
      if (phase === 'go') {
        const ms = Math.max(0, Math.round((ts || performance.now()) - (t0 || ts)));
        times.push(ms);
        phase = 'shown';
        stage.className = 'rx-stage done';
        label.textContent = `${ms}ms · ${reactionVerdict(ms)}`;
        info.textContent = times.length < opts.rounds ? '다음 라운드를 하려면 다시 눌러 줘.' : '';
        api.sfx('correct');
        hud();
        if (times.length >= opts.rounds) setTimeout(finish, 900);
      }
    }
    const onDown = (e) => { e.preventDefault(); press(e.timeStamp); };
    stage.addEventListener('pointerdown', onDown);
    const onKey = (e) => { if ((e.key === ' ' || e.key === 'Enter') && !e.repeat) { e.preventDefault(); press(e.timeStamp); } };
    stage.addEventListener('keydown', onKey);

    function finish() {
      if (dead) return;
      dead = true;
      const avg = Math.round(times.reduce((a, b) => a + b, 0) / times.length);
      api.finish({
        score: avg, record: avg, headline: `평균 ${avg}ms`, eyebrow: 'QUICK PAW', pokemon: p.id,
        lines: [`가장 빠른 기록 ${Math.min(...times)}ms`, `부정 출발 ${falseStarts}번`, `${p.name}: “${reactionVerdict(avg)}”`],
      });
    }
    phase = 'idle';
    stage.className = 'rx-stage idle';
    label.textContent = '눌러서 시작';
    hud();
    stage.focus();
    return {
      pause() { clearTimeout(timer); if (phase === 'wait' || phase === 'go') { phase = 'idle'; stage.className = 'rx-stage idle'; label.textContent = '눌러서 이어 하기'; } },
      resume() {},
      destroy() { dead = true; clearTimeout(timer); },
    };
  },
};
