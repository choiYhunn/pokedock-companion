// Game 2 — 포켓몬 밸런스 게임. Only the player's own choices are shown; there is no server, so no
// "other players picked…" statistics are invented.
import { byId, artUrl } from '../pokedex.js';
import { el, button, pokeImg, shuffle } from '../ui.js';

const O = (text, pokemon, tag, react) => ({ text, pokemon, tag, react });
export const PROMPTS = Object.freeze([
  { id: 'night-walk', a: O('팬텀이랑 밤 산책', 94, 'night', '크크, 그림자 길로 안내할게!'), b: O('팽도리랑 물놀이', 393, 'active', '팽! 첨벙첨벙 출발!') },
  { id: 'rest-train', a: O('누오처럼 하루 종일 쉬기', 195, 'cozy', '누오… 아무것도 안 해도 돼.'), b: O('루카리오랑 하루 종일 훈련', 448, 'active', '좋아, 파동을 모아 보자!') },
  { id: 'luck-wish', a: O('토게피의 행운', 175, 'luck', '토게토게! 행운 한가득!'), b: O('지라치의 소원', 385, 'luck', '천 년에 한 번, 너에게만.') },
  { id: 'one-or-many', a: O('최애 포켓몬 한 마리만 데려가기', 94, 'loyal', '역시 나지? 헤헤.'), b: O('매일 랜덤 파트너 만나기', 133, 'adventure', '오늘은 누가 올까? 두근두근!') },
  { id: 'nap-park', a: O('잠만보 배 위에서 낮잠', 143, 'cozy', '쿨… 쿨… 푹신하지?'), b: O('피카츄랑 번개 놀이공원', 25, 'active', '피카! 롤러코스터 한 번 더!') },
  { id: 'moon-sun', a: O('블래키와 달빛 별 보기', 197, 'night', '별똥별, 같이 세어 볼래?'), b: O('에브이와 햇살 아침 산책', 196, 'adventure', '아침 공기가 반짝반짝해.') },
  { id: 'sky-picnic', a: O('토게키스 타고 하늘 여행', 468, 'adventure', '꽉 잡아, 구름 위로 간다!'), b: O('쉐이미랑 꽃밭 소풍', 492, 'cozy', '꽃향기 맡으면서 도시락 먹자!') },
  { id: 'prank', a: O('파치리스랑 도토리 숨기기', 417, 'playful', '어디 숨겼는지 나도 까먹었어!'), b: O('조로아랑 변신 장난', 570, 'playful', '짜잔, 사실 나였지롱!') },
  { id: 'costume', a: O('따라큐랑 새 옷 만들기', 778, 'kind', '이번엔 더 귀엽게 해 줘…'), b: O('팬텀이랑 그림자 숨바꼭질', 94, 'playful', '찾았다! …아니, 못 찾았지?') },
  { id: 'song', a: O('푸린 노래 끝까지 듣기 (안 졸기!)', 39, 'kind', '푸~린~♪ 끝까지 들어 줘서 고마워!'), b: O('고라파덕 두통 같이 고민하기', 54, 'kind', '고라… 덕분에 조금 나아졌어.') },
  { id: 'ribbon-charge', a: O('님피아 리본 포옹', 700, 'kind', '리본으로 꼬옥!'), b: O('데덴네 전기 충전', 702, 'active', '찌릿! 휴대폰도 충전해 줄까?') },
  { id: 'aura-mind', a: O('리오르와 파동 수련', 447, 'active', '나도 언젠간 루카리오처럼!'), b: O('랄토스와 마음 이야기', 280, 'kind', '네 마음, 따뜻하게 느껴져.') },
  { id: 'blanket-mud', a: O('식스테일 꼬리 담요 덮기', 37, 'cozy', '따뜻하지? 조금만 더 있어.'), b: O('물짱이랑 진흙 놀이', 258, 'playful', '물짱! 얼굴에 진흙 묻었어!') },
  { id: 'rain-sea', a: O('비 오는 날 누오랑 창밖 보기', 195, 'cozy', '빗소리… 좋다…'), b: O('맑은 날 팽도리랑 바다 가기', 393, 'adventure', '파도 타러 가자, 팽!') },
]);

export const TYPES = Object.freeze({
  night: { name: '달빛 산책러', pokemon: 94, line: '조용한 밤과 장난스러운 친구를 좋아하는 타입!' },
  cozy: { name: '포근한 휴식러', pokemon: 195, line: '천천히, 편안하게. 쉬는 것도 실력이야.' },
  active: { name: '에너지 충전러', pokemon: 448, line: '움직이면서 기운을 얻는 반짝이는 타입!' },
  luck: { name: '행운 수집가', pokemon: 385, line: '작은 행운과 소원을 믿는 반짝 마음.' },
  adventure: { name: '두근두근 모험가', pokemon: 468, line: '새로운 하루를 기대하는 모험가!' },
  playful: { name: '장난꾸러기', pokemon: 570, line: '웃음이 많은 곳에 늘 네가 있어.' },
  kind: { name: '다정한 친구', pokemon: 700, line: '누군가를 챙겨 주는 따뜻한 타입.' },
  loyal: { name: '한결같은 단짝', pokemon: 94, line: '한 번 정한 친구는 끝까지!' },
});

export function summarize(picks) {
  const counts = {};
  for (const p of picks) counts[p.tag] = (counts[p.tag] || 0) + 1;
  const top = Object.entries(counts).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))[0]?.[0] || 'cozy';
  return { type: top, ...TYPES[top], counts };
}

// Draw a shareable PNG card. Images come from a CORS-enabled host; if one cannot be drawn the
// card is still produced with text only.
async function drawCard(result, picks) {
  const c = document.createElement('canvas');
  c.width = 720; c.height = 900;
  const g = c.getContext('2d');
  const grad = g.createLinearGradient(0, 0, 720, 900);
  grad.addColorStop(0, '#eee4f1'); grad.addColorStop(0.55, '#f6ecf2'); grad.addColorStop(1, '#f7e8d9');
  g.fillStyle = grad; g.fillRect(0, 0, 720, 900);
  g.fillStyle = '#ffffffaa'; g.beginPath(); g.ellipse(360, 900, 520, 260, 0, 0, Math.PI * 2); g.fill();
  g.fillStyle = '#9681a1'; g.font = '800 22px system-ui, sans-serif'; g.fillText('POKÉDOCK · BALANCE GAME', 56, 80);
  g.fillStyle = '#58406c'; g.font = '900 56px system-ui, sans-serif'; g.fillText(result.name, 56, 160);
  g.fillStyle = '#866e88'; g.font = '700 26px system-ui, sans-serif'; g.fillText(result.line, 56, 210);
  try {
    const img = await new Promise((res, rej) => { const i = new Image(); i.crossOrigin = 'anonymous'; i.onload = () => res(i); i.onerror = rej; i.src = artUrl(result.pokemon); });
    g.drawImage(img, 380, 230, 300, 300);
  } catch { /* text-only card */ }
  g.fillStyle = '#5b4a66'; g.font = '700 24px system-ui, sans-serif';
  picks.slice(0, 6).forEach((p, k) => g.fillText(`✦ ${p.text}`, 56, 590 + k * 44));
  g.fillStyle = '#a28eb1'; g.font = '700 18px system-ui, sans-serif'; g.fillText('내 선택만으로 만든 결과예요 · 다른 사람 통계 없음', 56, 870);
  return new Promise((res) => { try { c.toBlob((b) => res(b), 'image/png'); } catch { res(null); } });
}

export default {
  id: 'balance', title: '밸런스 게임', eyebrow: 'THIS OR THAT', tagline: '둘 중 하나만 고른다면?', icon: 94, color: '#efe4f7',
  desc: '두 장면 중 더 끌리는 쪽을 골라 줘. 정답은 없어! 고른 결과로 오늘의 성향 카드를 만들어 줄게.',
  options: [{ key: 'len', label: '질문 수', default: 5, choices: [{ v: 5, label: '5개' }, { v: 10, label: '10개' }] }],
  recordKey: (o) => `q${o.len}`,
  noRecord: true,
  hubMeta: (s) => (s.balance.length ? `내 선택 ${s.balance.length}개` : '첫 도전!'),
  extraSetup(env) {
    const hist = env.getState().balance;
    if (!hist.length) return el('p', 'setup-note', '아직 고른 기록이 없어요.');
    const box = el('details', 'history-box');
    box.append(el('summary', '', `내 선택 기록 ${hist.length}개`));
    const list = el('ul', 'history-list');
    for (const h of hist.slice(-8).reverse()) {
      const q = PROMPTS.find((p) => p.id === h.q);
      if (q) list.append(el('li', '', (h.pick === 0 ? q.a : q.b).text));
    }
    box.append(list);
    return box;
  },
  mount(host, opts, api) {
    const env = api.env;
    // least recently answered prompts first
    const lastSeen = {};
    env.getState().balance.forEach((h, k) => { lastSeen[h.q] = k + 1; });
    const qs = shuffle(PROMPTS).sort((a, b) => (lastSeen[a.id] || 0) - (lastSeen[b.id] || 0)).slice(0, opts.len);
    const picks = [];
    let i = 0, dead = false;
    const hud = () => api.hud([['질문', `${Math.min(i + 1, qs.length)}/${qs.length}`]]);
    function render() {
      if (i >= qs.length) return finish();
      hud();
      const q = qs[i];
      const wrap = el('div', 'balance');
      const react = el('p', 'balance-react', '', { 'aria-live': 'polite' });
      const side = (opt, k) => {
        const b = button('', 'balance-card side-' + k, () => {
          if (wrap.dataset.locked) return;
          wrap.dataset.locked = '1';
          b.classList.add('chosen');
          wrap.classList.add('decided');
          picks.push(opt);
          env.update((s) => { s.balance = [...s.balance, { q: q.id, pick: k, at: Date.now() }].slice(-60); });
          env.discover(opt.pokemon);
          react.textContent = `${byId(opt.pokemon)?.name}: “${opt.react}”`;
          api.sfx('correct');
          setTimeout(() => { if (!dead) { i++; render(); } }, 1500);
        }, { 'aria-label': opt.text });
        b.style.setProperty('--bc', byId(opt.pokemon)?.color || '#e9dcf3');
        b.append(pokeImg(opt.pokemon, { cls: 'balance-img' }), el('span', 'balance-text', opt.text));
        return b;
      };
      const vs = el('span', 'balance-vs', 'VS', { 'aria-hidden': 'true' });
      wrap.append(side(q.a, 0), vs, side(q.b, 1));
      host.replaceChildren(el('p', 'balance-q', '둘 중 하나만 고른다면?'), wrap, react);
    }
    async function finish() {
      const r = summarize(picks);
      const extra = el('div', 'share-box');
      const share = button('결과 카드 만들기', 'btn light', async () => {
        share.disabled = true;
        share.textContent = '만드는 중…';
        const blob = await drawCard(r, picks);
        share.disabled = false;
        share.textContent = '결과 카드 다시 만들기';
        if (!blob) { extra.append(el('p', 'setup-problem', '이미지 카드를 만들지 못했어요.')); return; }
        const file = new File([blob], 'pokedock-balance.png', { type: 'image/png' });
        if (navigator.canShare?.({ files: [file] })) {
          try { await navigator.share({ files: [file], title: 'PokéDock 밸런스 게임' }); return; } catch { /* cancelled */ }
        }
        const url = URL.createObjectURL(blob);
        const prev = extra.querySelector('.share-preview');
        prev?.remove();
        const a = el('a', 'share-preview', '', { href: url, download: 'pokedock-balance.png' });
        a.append(el('img', '', '', { src: url, alt: '밸런스 게임 결과 카드' }), el('span', '', '눌러서 이미지 저장'));
        extra.append(a);
      });
      extra.append(share);
      api.finish({
        score: picks.length, record: null, headline: r.name, eyebrow: 'MY BALANCE TYPE', pokemon: r.pokemon,
        lines: [r.line, '고른 장면: ' + picks.map((p) => p.text).join(' · '), '이 결과는 내 선택만으로 계산했어요.'],
        extra,
      });
    }
    render();
    return { destroy() { dead = true; } };
  },
};
