/* PokéDock original V10 offline shell and limited personal sprite cache.
   Franchise sprites are fetched from PokeAPI source; no images are republished in this repository. */
const CORE='pokedock-original-v10-mobile-v2';
const IMAGES='pokedock-original-v10-image-cache-v1';
const LOCAL=['./','./index.html','./manifest.webmanifest','./icon.svg','../ui/party-game.css?v=9','../ui/party-game.js?v=9'];
const MAX_IMAGES=32;
self.addEventListener('install',e=>e.waitUntil(caches.open(CORE).then(c=>c.addAll(LOCAL)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CORE&&k!==IMAGES).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{
 const url=new URL(e.request.url);
 if(e.request.method!=='GET')return;
 const sprites=(url.hostname==='raw.githubusercontent.com' && url.pathname.startsWith('/PokeAPI/sprites/master/sprites/pokemon/'));
 if(sprites && e.request.destination==='image'){
  e.respondWith(caches.open(IMAGES).then(async cache=>{
   const existing=await cache.match(e.request);
   if(existing)return existing;
   const response=await fetch(e.request);
   if(response.ok||response.type==='opaque'){
    await cache.put(e.request,response.clone());
    const keys=await cache.keys();if(keys.length>MAX_IMAGES)await cache.delete(keys[0]);
   }
   return response;
  }));
  return;
 }
 if(url.origin!==self.location.origin)return;
 e.respondWith(caches.match(e.request).then(cached=>cached||fetch(e.request).then(r=>{
  if(r.ok){const cp=r.clone();caches.open(CORE).then(c=>c.put(e.request,cp));}
  return r;
 })));
});
