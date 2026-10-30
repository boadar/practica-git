// Control de Importaciones - service worker (network-first: con conexion siempre sirve lo ultimo)
const CACHE_NAME = 'control-importaciones-v39';
const ARCHIVOS = ['./', 'index.html', 'seed.js', 'plan_base.js', 'proformas.js', 'analisis_base.js', 'manifest.webmanifest', 'icon-192.png', 'icon-512.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE_NAME).then(c => c.addAll(ARCHIVOS)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET' || new URL(e.request.url).origin !== location.origin) return;
  e.respondWith(
    fetch(e.request).then(r => { const copia = r.clone(); caches.open(CACHE_NAME).then(c => c.put(e.request, copia)); return r; })
      .catch(() => caches.match(e.request))
  );
});
