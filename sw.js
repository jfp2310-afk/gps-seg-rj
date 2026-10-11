const CACHE = 'gps-seg-rj-v2';
const SHELL = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png',
  'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css', 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => Promise.allSettled(SHELL.map(u => c.add(u)))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET') return;
  // Rotas e geocodificação: sempre rede
  if (/osrm\.org|nominatim/.test(url.host)) return;
  const store = r => { if (r && r.ok) { const copy = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); } return r; };
  // Arquivos do próprio programa e tiles: rede primeiro (sempre a versão mais nova), cache como reserva offline
  if (url.origin === self.location.origin || /tile\.openstreetmap\.org/.test(url.host)) {
    e.respondWith(fetch(e.request).then(store).catch(() => caches.match(e.request)));
    return;
  }
  // Biblioteca Leaflet: cache primeiro
  e.respondWith(caches.match(e.request).then(hit => hit || fetch(e.request).then(store)));
});
