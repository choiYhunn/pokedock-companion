// Registers the V18 service worker and exposes window.pokedockOffline for the app:
// status {shell, sprites, cries}, cacheSprites(), cacheCries(), clear(kind). Progress is
// announced with a "pokedock-offline" window event.
(function () {
  const status = { shell: { ready: false }, sprites: { done: 0, total: 48 }, cries: { done: 0, total: 24 } };
  const emit = () => window.dispatchEvent(new CustomEvent('pokedock-offline', { detail: status }));
  const isNative = !!(window.Capacitor && window.Capacitor.isNativePlatform && window.Capacitor.isNativePlatform());
  if (isNative || !('serviceWorker' in navigator)) {
    status.unsupported = !isNative;
    if (isNative) { status.shell.ready = true; status.sprites = { done: 48, total: 48, bundled: true }; }
    window.pokedockOffline = null;
    window.pokedockOfflineStatus = status;
    setTimeout(emit, 0);
    return;
  }
  let reg = null;
  const post = (msg) => {
    const target = navigator.serviceWorker.controller || (reg && reg.active);
    if (target) target.postMessage(msg);
  };
  navigator.serviceWorker.addEventListener('message', (e) => {
    const d = e.data || {};
    if (d.type === 'POKEDOCK_OFFLINE') {
      status[d.kind] = { done: d.done, total: d.total, error: d.error || '' };
      if (d.finished) post({ type: 'POKEDOCK_STATUS' });
      emit();
    } else if (d.type === 'POKEDOCK_STATUS') {
      status.shell = d.shell;
      status.sprites = { ...status.sprites, ...d.sprites };
      status.cries = { ...status.cries, ...d.cries };
      emit();
    }
  });
  let reloading = false;
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    // A new release took over. Reload once so every module comes from the same version, unless a
    // game is running (then the next launch picks it up; nothing is lost either way).
    if (reloading || document.body.classList.contains('arcade-open')) return;
    reloading = true;
    location.reload();
  });
  window.pokedockOffline = {
    status,
    cacheSprites() { post({ type: 'POKEDOCK_CACHE', kind: 'sprites' }); },
    cacheCries() { post({ type: 'POKEDOCK_CACHE', kind: 'cries' }); },
    clear(kind) { post({ type: 'POKEDOCK_CLEAR', kind }); return new Promise((r) => setTimeout(r, 300)); },
    refresh() { post({ type: 'POKEDOCK_STATUS' }); },
  };
  navigator.serviceWorker.register('./sw.js', { updateViaCache: 'none' })
    .then((r) => { reg = r; return navigator.serviceWorker.ready; })
    .then((r) => {
      reg = r;
      post({ type: 'POKEDOCK_STATUS' });
      post({ type: 'POKEDOCK_CACHE', kind: 'sprites' });
    })
    .catch(() => { status.unsupported = true; emit(); });
  window.addEventListener('online', () => post({ type: 'POKEDOCK_CACHE', kind: 'sprites' }));
})();
