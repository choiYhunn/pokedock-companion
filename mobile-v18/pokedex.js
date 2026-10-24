// PokéDock V18 Pokédex: the 8 M6 partners first (order kept from V17), then the 16 extended
// friends already listed in config/pokemon_catalog.json. No image or sound files live in this
// repository; URLs point at the PokeAPI GitHub repositories and are cached per device at runtime.

export const TYPE_KO = Object.freeze({
  normal: '노말', fire: '불꽃', water: '물', electric: '전기', grass: '풀', ice: '얼음', fighting: '격투',
  poison: '독', ground: '땅', flying: '비행', psychic: '에스퍼', bug: '벌레', rock: '바위', ghost: '고스트',
  dragon: '드래곤', dark: '악', steel: '강철', fairy: '페어리',
});

// behavior: default motion for taps. pixel: measured gen-V sprite size for integer scaling (partners only).
const P = (id, name, en, types, color, behavior, line, extra = {}) =>
  Object.freeze({ id, name, en, types: Object.freeze(types), color, behavior, line, partner: false, ...extra });

export const POKEDEX = Object.freeze([
  P(94, '팬텀', 'GENGAR', ['ghost', 'poison'], '#ae88d4', 'peek', '오늘은 나랑 놀아볼래?', { partner: true, pixel: [74, 63] }),
  P(393, '팽도리', 'PIPLUP', ['water'], '#91c5ed', 'hop', '한 번 더 도전해 볼까?', { partner: true, pixel: [30, 41] }),
  P(468, '토게키스', 'TOGEKISS', ['fairy', 'flying'], '#eec9e5', 'dance', '좋은 일이 가득할 거야!', { partner: true, pixel: [86, 52] }),
  P(448, '루카리오', 'LUCARIO', ['fighting', 'steel'], '#7a9fd2', 'celebrate', '오늘도 조금씩 성장하자.', { partner: true, pixel: [47, 63] }),
  P(195, '누오', 'QUAGSIRE', ['water', 'ground'], '#add4d9', 'hop', '천천히 가도 괜찮아.', { partner: true, pixel: [67, 58] }),
  P(175, '토게피', 'TOGEPI', ['fairy'], '#f1c3b1', 'celebrate', '너랑 있으면 행복해!', { partner: true, pixel: [40, 38] }),
  P(417, '파치리스', 'PACHIRISU', ['electric'], '#bed8ee', 'dance', '우리, 잠깐 놀까?', { partner: true, pixel: [53, 55] }),
  P(385, '지라치', 'JIRACHI', ['steel', 'psychic'], '#eec97c', 'peek', '소원 하나 들어줄까?', { partner: true, pixel: [55, 47] }),
  P(25, '피카츄', 'PIKACHU', ['electric'], '#f3d77a', 'hop', '피카피카! 오늘도 반짝이자.'),
  P(133, '이브이', 'EEVEE', ['normal'], '#d9b48f', 'dance', '어떤 모습이 될지 기대돼!'),
  P(54, '고라파덕', 'PSYDUCK', ['water'], '#f1d48a', 'peek', '머리가 아파도… 같이 있으면 괜찮아.'),
  P(143, '잠만보', 'SNORLAX', ['normal'], '#8fb0b8', 'hop', '조금만 더 자고 일어나자…'),
  P(37, '식스테일', 'VULPIX', ['fire'], '#e9a27f', 'dance', '따뜻한 하루 보내!'),
  P(39, '푸린', 'JIGGLYPUFF', ['normal', 'fairy'], '#f4c0d2', 'celebrate', '노래 한 곡 들려줄까?'),
  P(196, '에브이', 'ESPEON', ['psychic'], '#d8b7e0', 'peek', '네 마음, 살짝 느껴져.'),
  P(197, '블래키', 'UMBREON', ['dark'], '#7d8296', 'peek', '밤에도 내가 옆에 있을게.'),
  P(258, '물짱이', 'MUDKIP', ['water'], '#8fc1e3', 'hop', '물장구 치러 갈래?'),
  P(280, '랄토스', 'RALTS', ['psychic', 'fairy'], '#bfe0c4', 'dance', '네 기분이 좋으면 나도 좋아.'),
  P(447, '리오르', 'RIOLU', ['fighting'], '#8eb0db', 'celebrate', '나도 루카리오처럼 될 거야!'),
  P(492, '쉐이미', 'SHAYMIN', ['grass'], '#b6dca0', 'dance', '꽃향기 맡으러 가자!'),
  P(570, '조로아', 'ZORUA', ['dark'], '#9e93b8', 'peek', '헤헤, 누구로 변해 볼까?'),
  P(700, '님피아', 'SYLVEON', ['fairy'], '#f2c6d8', 'dance', '리본으로 꼭 안아줄게.'),
  P(702, '데덴네', 'DEDENNE', ['electric', 'fairy'], '#f0d290', 'hop', '찌릿! 기운 충전 완료!'),
  P(778, '따라큐', 'MIMIKYU', ['ghost', 'fairy'], '#e8d58c', 'peek', '나랑… 친구 해 줄래?'),
]);

export const PARTNERS = Object.freeze(POKEDEX.filter((p) => p.partner));
export const PARTNER_IDS = Object.freeze(PARTNERS.map((p) => p.id));
// Korean particle after a name: josa('팬텀', '이', '가') → '팬텀이', josa('피카츄', '이', '가') → '피카츄가'.
export function josa(word, withBatchim, without) {
  const c = word.charCodeAt(word.length - 1);
  const has = c >= 0xac00 && c <= 0xd7a3 && (c - 0xac00) % 28 !== 0;
  return word + (has ? withBatchim : without);
}
export const byId = (id) => POKEDEX.find((p) => p.id === id) || null;
export const typesKo = (p) => p.types.map((t) => TYPE_KO[t] || t).join(' · ');
export const typesEn = (p) => p.types.map((t) => t.toUpperCase()).join(' · ');

const SPRITES = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/';
export const CRIES = 'https://raw.githubusercontent.com/PokeAPI/cries/main/cries/pokemon/';

// A native build can set <html data-bundled-sprites="1"> and ship private copies in assets/sprites
// (same layout as the V17 Android build). The public Pages build never bundles them.
const bundled = () => typeof document !== 'undefined' && document.documentElement.dataset.bundledSprites === '1';
export const artUrl = (id) => (bundled() ? `assets/sprites/${id}_art.png` : `${SPRITES}other/official-artwork/${id}.png`);
export const pixelUrl = (id) => (bundled() ? `assets/sprites/${id}_pixel.gif` : `${SPRITES}versions/generation-v/black-white/animated/${id}.gif`);
export const pixelFallbackUrl = (id) => `${SPRITES}other/showdown/${id}.gif`;
export const cryUrl = (id) => `${CRIES}latest/${id}.ogg`;

// Every remote file the offline manager may cache, grouped so the user can see what is stored.
export const spriteUrls = (ids = POKEDEX.map((p) => p.id)) => ids.flatMap((id) => [artUrl(id), pixelUrl(id)]);
export const cryUrls = (ids = POKEDEX.map((p) => p.id)) => ids.map(cryUrl);

// Short reactions per Pokémon for petting and partner-room actions. Gengar gets the most mischief.
export const REACTIONS = Object.freeze({
  94: ['헤헤, 놀랐지?', '그림자 속에서 짠!', '간지러워~ 한 번 더!', '밤 산책 갈래? 크크', '장난 하나 칠까 말까…'],
  393: ['팽! 기분 최고야!', '물장구 칠 사람~', '나 멋있지?'],
  468: ['오늘 좋은 일이 생길 거야.', '포근하게 날아왔어!', '행복을 나눠줄게.'],
  448: ['파동이 느껴져.', '한 세트만 더!', '집중, 좋아.'],
  195: ['누오…', '멍~ 때리는 중', '천천히 해도 돼.'],
  175: ['토게토게!', '행운 한 스푼!', '안아줘!'],
  417: ['찌릿찌릿!', '도토리 숨겨 놨어!', '같이 뛰자!'],
  385: ['소원 하나만 말해 봐.', '반짝반짝 별빛!', '잘 자고 일어났어?'],
});
export const reactionFor = (p, n = 0) => {
  const lines = REACTIONS[p.id] || [p.line, '반가워!', '같이 놀자!'];
  return lines[n % lines.length];
};
