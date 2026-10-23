const VERSION='pokedock-v17-1-shell-v1';
const SPRITES='pokedock-v17-1-remote-sprites-v1';
const CORE=['./','./index.html','./styles.css','./core.js','./app.js','./offline.js','./manifest.webmanifest','./icon.svg','./icon-192.png','./icon-512.png','./assets/sounds/alarm_dawn.wav','./assets/sounds/alarm_sparkle.wav','./assets/sounds/alarm_calm.wav'];
const ROOT='https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/';
const IDS=[94,393,468,448,195,175,417,385];
const URLS=IDS.flatMap(id=>[`${ROOT}other/official-artwork/${id}.png`,`${ROOT}versions/generation-v/black-white/animated/${id}.gif`]);

self.addEventListener('install',event=>event.waitUntil(caches.open(VERSION).then(cache=>cache.addAll(CORE)).then(()=>self.skipWaiting())));
self.addEventListener('activate',event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(key=>key.startsWith('pokedock-v17')&&key!==VERSION&&key!==SPRITES).map(key=>caches.delete(key)))).then(()=>self.clients.claim())));

async function cacheSprites(client){
 const cache=await caches.open(SPRITES);
 let done=0,next=0;
 async function work(){
  while(next<URLS.length){
   const url=URLS[next++];
   try{
    const request=new Request(url,{mode:'no-cors',credentials:'omit'});
    if(!await cache.match(request)){
     const response=await fetch(request);
     if(!response.ok&&response.type!=='opaque')throw new Error('sprite download failed');
     await cache.put(request,response);
    }
    done++;
   }catch{}
   client?.postMessage({type:'POKEDOCK_OFFLINE_PROGRESS',done,total:URLS.length});
  }
 }
 await Promise.all(Array.from({length:4},work));
}
self.addEventListener('message',event=>{
 if(event.data?.type==='POKEDOCK_CACHE_SPRITES')event.waitUntil(cacheSprites(event.source));
});
self.addEventListener('fetch',event=>{
 if(event.request.method!=='GET')return;
 const url=new URL(event.request.url);
 const sprite=url.hostname==='raw.githubusercontent.com'&&url.pathname.startsWith('/PokeAPI/sprites/master/sprites/pokemon/');
 if(sprite&&event.request.destination==='image'){
  event.respondWith(caches.open(SPRITES).then(async cache=>{
   const hit=await cache.match(event.request);if(hit)return hit;
   const response=await fetch(event.request);
   if(response.ok||response.type==='opaque')await cache.put(event.request,response.clone());
   return response;
  }));return;
 }
 if(url.origin!==self.location.origin)return;
 if(event.request.mode==='navigate'){
  event.respondWith(fetch(event.request).then(async response=>{
   if(response.ok)(await caches.open(VERSION)).put(event.request,response.clone());
   return response;
  }).catch(()=>caches.match(event.request).then(hit=>hit||caches.match('./index.html'))));return;
 }
 event.respondWith(caches.match(event.request).then(hit=>hit||fetch(event.request).then(async response=>{
  if(response.ok)(await caches.open(VERSION)).put(event.request,response.clone());
  return response;
 })));
});
