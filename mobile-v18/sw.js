// PokéDock V18 service worker. Caches only its own "pokedock-v18-*" storage, so the V17.1 app
// that shares this origin keeps its caches. Shell: cache-first per release. Sprites: cached on the
// first online visit. Cries: cached only when the user asks for it in the offline manager.
const RELEASE = '18.0.0';
const SHELL = 'pokedock-v18-shell-' + RELEASE;
const SPRITES = 'pokedock-v18-sprites-v1';
const CRIES = 'pokedock-v18-cries-v1';
const CORE = ['./', './index.html', './styles.css', './v18.css', './app.js', './core.js', './pokedex.js', './ui.js', './sfx.js', './offline.js',
  './games/arcade.js', './games/cry.js', './games/balance.js', './games/silhouette.js', './games/memory.js', './games/runner.js', './games/runner-engine.js', './games/reaction.js', './games/daily.js',
  './ble/m6.js', './ble/transports.js', './ble/pokedock_ble_client.mjs', './ble/pokedock_ble_protocol.mjs',
  './manifest.webmanifest', './icon.svg', './icon-192.png', './icon-512.png',
  './assets/sounds/alarm_dawn.wav', './assets/sounds/alarm_sparkle.wav', './assets/sounds/alarm_calm.wav'];
// Must match POKEDEX in pokedex.js (checked by tests/v18_unit.test.mjs).
const IDS = [94, 393, 468, 448, 195, 175, 417, 385, 25, 133, 54, 143, 37, 39, 196, 197, 258, 280, 447, 492, 570, 700, 702, 778];
const SP = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/';
const CR = 'https://raw.githubusercontent.com/PokeAPI/cries/main/cries/pokemon/latest/';
const art = (id) => `${SP}other/official-artwork/${id}.png`;
const pixel = (id) => `${SP}versions/generation-v/black-white/animated/${id}.gif`;
const showdown = (id) => `${SP}other/showdown/${id}.gif`;

self.addEventListener('install', (e) => e.waitUntil(caches.open(SHELL).then((c) => c.addAll(CORE)).then(() => self.skipWaiting())));
self.addEventListener('activate', (e) => e.waitUntil(
  caches.keys()
    .then((keys) => Promise.all(keys.filter((k) => k.startsWith('pokedock-v18-shell-') && k !== SHELL).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()),
));

async function broadcast(msg) {
  for (const c of await self.clients.matchAll({ includeUncontrolled: true })) c.postMessage(msg);
}

async function store(cache, url) {
  if (await cache.match(url)) return true;
  const res = await fetch(url, { mode: 'cors', credentials: 'omit' });
  if (!res.ok) throw new Error('HTTP ' + res.status);
  await cache.put(url, res);
  return true;
}

let running = {};
async function cacheGroup(kind) {
  if (running[kind]) return running[kind];
  running[kind] = (async () => {
    const cache = await caches.open(kind === 'cries' ? CRIES : SPRITES);
    const jobs = kind === 'cries' ? IDS.map((id) => [CR + id + '.ogg']) : IDS.flatMap((id) => [[art(id)], [pixel(id), showdown(id)]]);
    let done = 0, next = 0, error = '';
    const work = async () => {
      while (next < jobs.length) {
        const urls = jobs[next++];
        for (const u of urls) {
          try { await store(cache, u); done++; break; }
          catch (e) { error = e?.name === 'QuotaExceededError' ? '저장 공간 부족' : navigatorOffline() ? '오프라인' : '일부 실패'; }
        }
        broadcast({ type: 'POKEDOCK_OFFLINE', kind, done, total: jobs.length, error: done === jobs.length ? '' : error });
      }
    };
    await Promise.all(Array.from({ length: 4 }, work));
    broadcast({ type: 'POKEDOCK_OFFLINE', kind, done, total: jobs.length, error: done === jobs.length ? '' : error || '일부 실패', finished: true });
  })().finally(() => { running[kind] = null; });
  return running[kind];
}
const navigatorOffline = () => self.navigator && self.navigator.onLine === false;

async function status() {
  const shell = await caches.open(SHELL);
  const shellReady = (await Promise.all(CORE.map((u) => shell.match(u)))).every(Boolean);
  const sc = await caches.open(SPRITES), cc = await caches.open(CRIES);
  let sprites = 0, cries = 0;
  for (const id of IDS) {
    if (await sc.match(art(id))) sprites++;
    if ((await sc.match(pixel(id))) || (await sc.match(showdown(id)))) sprites++;
    if (await cc.match(CR + id + '.ogg')) cries++;
  }
  return { type: 'POKEDOCK_STATUS', shell: { ready: shellReady }, sprites: { done: sprites, total: IDS.length * 2 }, cries: { done: cries, total: IDS.length } };
}

self.addEventListener('message', (e) => {
  const t = e.data?.type;
  if (t === 'POKEDOCK_CACHE') e.waitUntil(cacheGroup(e.data.kind === 'cries' ? 'cries' : 'sprites'));
  else if (t === 'POKEDOCK_STATUS') e.waitUntil(status().then((s) => e.source?.postMessage(s)));
  else if (t === 'POKEDOCK_CLEAR') e.waitUntil(caches.delete(e.data.kind === 'cries' ? CRIES : SPRITES).then(status).then((s) => e.source?.postMessage(s)));
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.hostname === 'raw.githubusercontent.com') {
    const sprite = url.pathname.startsWith('/PokeAPI/sprites/master/sprites/pokemon/');
    const cry = url.pathname.startsWith('/PokeAPI/cries/main/cries/pokemon/');
    if (!sprite && !cry) return;
    e.respondWith((async () => {
      const cache = await caches.open(sprite ? SPRITES : CRIES);
      const hit = await cache.match(url.href);
      if (hit) return hit;
      const res = await fetch(url.href, { mode: 'cors', credentials: 'omit' });
      if (sprite && res.ok) cache.put(url.href, res.clone()).catch(() => {});
      return res;
    })());
    return;
  }
  if (url.origin !== self.location.origin) return;
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).then(async (res) => {
      if (res.ok) (await caches.open(SHELL)).put('./index.html', res.clone()).catch(() => {});
      return res;
    }).catch(async () => (await caches.match(req, { ignoreSearch: true })) || caches.match('./index.html')));
    return;
  }
  e.respondWith(caches.match(req, { ignoreSearch: true }).then((hit) => hit || fetch(req).then(async (res) => {
    if (res.ok && url.pathname.includes('/mobile-v18/')) (await caches.open(SHELL)).put(req, res.clone()).catch(() => {});
    return res;
  })));
});
