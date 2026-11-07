// Offline support for the whole tools site (apps/). Registered by the hub page (index.html).
// - Pages: network first, so people always get the latest version online; the cached copy offline.
// - Scripts, styles and images: served from cache at once and refreshed in the background.
// - Every tool you open is cached as you use it. Nothing you type is cached: tools keep your data
//   in localStorage, and this worker never touches requests other than GETs to this site.
// - /api/ (license checks, SMS) is never cached.
// The budget app registers its own worker for /budget/, which takes over there.
const VERSION = 'tools-v1';
const SHELL = ['./', 'index.html', 'offline.html', 'manifest.webmanifest', 'budget/icon-192.png', 'budget/icon-512.png', 'budget/config.js', 'budget/lib/track.js'];

self.addEventListener('install', (e) => e.waitUntil(caches.open(VERSION).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting())));
self.addEventListener('activate', (e) => e.waitUntil(
  caches.keys().then((keys) => Promise.all(keys.filter((k) => k.startsWith('tools-') && k !== VERSION).map((k) => caches.delete(k)))).then(() => self.clients.claim()),
));

const cacheable = (req, url) => req.method === 'GET' && url.origin === self.location.origin && !url.pathname.startsWith('/api/') && !url.pathname.startsWith('/.netlify/');

self.addEventListener('fetch', (e) => {
  const req = e.request;
  const url = new URL(req.url);
  if (!cacheable(req, url)) return;
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).then((res) => {
      if (res.ok) { const copy = res.clone(); caches.open(VERSION).then((c) => c.put(req, copy)); }
      return res;
    }).catch(async () => (await caches.match(req, { ignoreSearch: true })) || caches.match('offline.html')));
    return;
  }
  e.respondWith(caches.match(req).then((hit) => {
    const fresh = fetch(req).then((res) => {
      if (res.ok) { const copy = res.clone(); caches.open(VERSION).then((c) => c.put(req, copy)); }
      return res;
    }).catch(() => hit);
    return hit || fresh;
  }));
});

// The hub can ask to save a list of pages for offline use ("Save tools for offline").
self.addEventListener('message', (e) => {
  if (e.data?.type !== 'precache' || !Array.isArray(e.data.urls)) return;
  e.waitUntil(caches.open(VERSION).then((c) => Promise.all(e.data.urls.map((u) => c.add(u).catch(() => null))))
    .then((done) => e.source?.postMessage({ type: 'precached', count: done.length })));
});
