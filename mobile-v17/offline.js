const offlineBadge=document.getElementById('offline-badge');
function showOfflineProgress(done,total){
 const ready=done===total;
 offlineBadge.textContent=ready?'오프라인 준비 완료':`이미지 저장 ${done}/${total}`;
 offlineBadge.classList.toggle('ready',ready);
 window.pokedockOfflineReady=ready;
}
if('serviceWorker' in navigator){
 let reloading=false;
 navigator.serviceWorker.addEventListener('controllerchange',()=>{
  if(!reloading){reloading=true;location.reload();}
 });
 navigator.serviceWorker.addEventListener('message',event=>{
  if(event.data?.type==='POKEDOCK_OFFLINE_PROGRESS')showOfflineProgress(event.data.done,event.data.total);
 });
 navigator.serviceWorker.register('./sw.js',{updateViaCache:'none'})
  .then(()=>navigator.serviceWorker.ready)
  .then(registration=>registration.active?.postMessage({type:'POKEDOCK_CACHE_SPRITES'}))
  .catch(()=>{offlineBadge.textContent='오프라인 저장 확인 필요'});
}else offlineBadge.textContent='오프라인 저장 미지원';
