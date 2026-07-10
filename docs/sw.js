/* Service worker de Pedidos OFICA — permite usar la app sin conexión.
   Estrategia: cache-first para los recursos propios; guarda en caché lo que se pide.
   Sube el número de versión (CACHE) cuando publiques una nueva versión de la app. */
const CACHE = 'pedidos-ofica-v55';
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
  const url = new URL(e.request.url);
  const sameOrigin = url.origin === self.location.origin;
  const isDoc = e.request.mode === 'navigate' ||
    (sameOrigin && (url.pathname.endsWith('/') || url.pathname.endsWith('/index.html')));

  // HTML de la app: network-first (siempre intenta la última versión; usa caché si no hay red)
  if (isDoc) {
    e.respondWith(
      fetch(e.request).then((resp) => {
        try {
          if (sameOrigin) { const copy = resp.clone(); caches.open(CACHE).then((c) => c.put(e.request, copy)); }
        } catch (_) {}
        return resp;
      }).catch(() => caches.match(e.request).then((r) => r || caches.match('./index.html')))
    );
    return;
  }

  // Resto de recursos: cache-first (rápido y offline)
  e.respondWith(
    caches.match(e.request).then((cached) => {
      if (cached) return cached;
      return fetch(e.request).then((resp) => {
        try {
          if (sameOrigin) { const copy = resp.clone(); caches.open(CACHE).then((c) => c.put(e.request, copy)); }
        } catch (_) {}
        return resp;
      }).catch(() => caches.match('./index.html'));
    })
  );
});
