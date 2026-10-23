/* PokéDock original UI offline shell, external franchise artwork remains network-dependent. */
const CACHE='pokedock-original-v10-mobile-v1';
const LOCAL=['./','./index.html','./manifest.webmanifest','./icon.svg','../ui/party-game.css?v=9','../ui/party-game.js?v=9'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(LOCAL)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{const url=new URL(e.request.url);if(e.request.method!=='GET'||url.origin!==self.location.origin)return;
e.respondWith(caches.match(e.request).then(cached=>cached||fetch(e.request).then(r=>{if(r.ok){const cp=r.clone();caches.open(CACHE).then(c=>c.put(e.request,cp));}return r;})));
});
