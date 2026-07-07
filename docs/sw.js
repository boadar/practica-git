/* Service worker de Pedidos OFICA — permite usar la app sin conexión.
   Estrategia: cache-first para los recursos propios; guarda en caché lo que se pide.
   Sube el número de versión (CACHE) cuando publiques una nueva versión de la app. */
const CACHE = 'pedidos-ofica-v3';
const ASSETS = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icon-180.png',
  './icon-192.png',
  './icon-512.png'
];

self.addEventListener('install', (e) => {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ASSETS)).catch(() => {}));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    caches.match(e.request).then((cached) => {
      if (cached) return cached;
      return fetch(e.request).then((resp) => {
        try {
          if (new URL(e.request.url).origin === self.location.origin) {
            const copy = resp.clone();
            caches.open(CACHE).then((c) => c.put(e.request, copy));
          }
        } catch (_) {}
        return resp;
      }).catch(() => caches.match('./index.html'));
    })
  );
});
