// Small DOM helpers shared by the app and the games.
import { artUrl, byId, pixelFallbackUrl, pixelUrl } from './pokedex.js';

export function el(tag, cls = '', text = '', attrs = {}) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text) e.textContent = text;
  for (const [k, v] of Object.entries(attrs)) {
    if (v === false || v == null) continue;
    if (k.startsWith('on')) e.addEventListener(k.slice(2), v);
    else e.setAttribute(k, v === true ? '' : v);
  }
  return e;
}

export function button(text, cls, onclick, attrs = {}) {
  return el('button', cls, text, { type: 'button', onclick, ...attrs });
}

// Pokémon image with a graceful fallback chain. Pixel: gen-V GIF → Showdown GIF → artwork.
// When everything fails the <img> is swapped for a soft placeholder showing the name, so a missing
// remote file never breaks a game or a layout.
export function pokeImg(id, { kind = 'art', cls = '', alt, onFail, onLoad, cors = false } = {}) {
  const p = byId(id);
  const img = el('img', 'pokemon-image ' + cls, '', { alt: alt ?? p?.name ?? '포켓몬', draggable: 'false', decoding: 'async' });
  if (cors) img.crossOrigin = 'anonymous';
  const chain = kind === 'pixel' ? [pixelUrl(id), pixelFallbackUrl(id), artUrl(id)] : [artUrl(id)];
  let i = 0;
  img.addEventListener('load', () => onLoad?.(img));
  img.addEventListener('error', () => {
    i++;
    if (i < chain.length) { img.src = chain[i]; img.classList.toggle('pixel', i < 2 && kind === 'pixel'); return; }
    const ph = el('span', 'poke-placeholder ' + cls, p?.name ? p.name.slice(0, 1) : '?', { role: 'img', 'aria-label': `${p?.name || '포켓몬'} 이미지를 불러오지 못했어요` });
    ph.style.setProperty('--pc', p?.color || '#d9c8e6');
    if (img.isConnected) img.replaceWith(ph);
    onFail?.(ph);
  });
  img.classList.toggle('pixel', kind === 'pixel');
  img.src = chain[0];
  return img;
}

export function shuffle(items, rnd = Math.random) {
  const a = [...items];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rnd() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}
export const sample = (items, n, rnd) => shuffle(items, rnd).slice(0, n);

// Pick n distinct quiz targets, preferring ones seen least recently (seen: {id: lastShownMs}).
export function freshDeck(pool, n, seen = {}, rnd = Math.random) {
  const ordered = shuffle(pool, rnd).sort((a, b) => (seen[a.id] || 0) - (seen[b.id] || 0));
  const out = [];
  while (out.length < n && ordered.length) {
    // cycle through the pool again for long rounds, never repeating the previous question
    for (const p of ordered) {
      if (out.length >= n) break;
      if (out[out.length - 1]?.id === p.id) continue;
      out.push(p);
    }
    if (ordered.length === 1) break;
  }
  return out;
}

export function prefersReducedMotion(state) {
  return !!state?.reduceMotion || (typeof matchMedia !== 'undefined' && matchMedia('(prefers-reduced-motion: reduce)').matches);
}
