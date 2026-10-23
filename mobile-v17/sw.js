const CACHE='pokedock-v17-inline-v1',IMAGES='pokedock-v17-cache-gif';const CORE=['./','./index.html','./manifest.webmanifest','./icon.svg'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==CACHE&&x!==IMAGES).map(x=>caches.delete(x)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;const u=new URL(e.request.url);
const isSprite=u.hostname==='raw.githubusercontent.com'&&u.pathname.startsWith('/PokeAPI/sprites/master/sprites/pokemon/');
if(isSprite&&e.request.destination==='image'){e.respondWith(caches.open(IMAGES).then(async c=>{const hit=await c.match(e.request);if(hit)return hit;const r=await fetch(e.request);if(r.ok||r.type==='opaque'){await c.put(e.request,r.clone());const ks=await c.keys();if(ks.length>40)await c.delete(ks[0]);}return r;}));return;}
if(u.origin===self.location.origin)e.respondWith(caches.match(e.request).then(hit=>hit||fetch(e.request).then(r=>{if(r.ok)caches.open(CACHE).then(c=>c.put(e.request,r.clone()));return r;})));
});