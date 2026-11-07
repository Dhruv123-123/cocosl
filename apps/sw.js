// Offline support for the whole tools site (apps/). Registered by the hub page (index.html).
// - Pages: network first, so people always get the latest version online; the cached copy offline.
// - Scripts, styles and images: served from cache at once and refreshed in the background.
// - Every tool you open is cached as you use it. Nothing you type is cached: tools keep your data
//   in localStorage, and this worker never touches requests other than GETs to this site.
// - /api/ (license checks, SMS) is never cached.
// The budget app registers its own worker for /budget/, which takes over there.
const VERSION = 'tools-v8';
// Saved at install so they work offline from day one: the hub, the paycheck calculator by state and
// the student loan chooser, rent vs buy and the "Can I afford this?" checker (the budget app's own worker also caches the checker under /budget/).
const PAYCHECK = ['money-calculators/take-home-pay/', 'money-calculators/tax-refund/', 'money-calculators/debt-payoff/', 'money-calculators/es/tax-refund/', 'money-calculators/es/debt-payoff/', 'money-calculators/lib/refund.js', 'money-calculators/student-loans/', 'money-calculators/rent-vs-buy/', 'money-calculators/style.css', 'money-calculators/app.js', 'money-calculators/config.js', 'money-calculators/lib/calc.js', 'money-calculators/lib/fees.js', 'money-calculators/lib/format.js', 'money-calculators/lib/text.js', 'money-calculators/lib/track.js', 'money-calculators/lib/tax2026.js', 'money-calculators/lib/state-tax-2026.js', 'money-calculators/lib/student-loans.js', 'money-calculators/lib/rent-vs-buy.js', 'money-calculators/lib/text-extra.js'];
const AFFORD = ['budget/afford.html', 'budget/afford.js', 'budget/lib/afford.js', 'budget/couples.html', 'budget/couples.js', 'budget/lib/couples.js', 'budget/first-paycheck.html', 'budget/first-paycheck.js', 'budget/lib/firstpaycheck.js', 'budget/checkup.html', 'budget/checkup.js', 'budget/lib/checkup.js', 'budget/money-personality.html', 'budget/money-personality.js', 'budget/lib/personality.js', 'budget/savings-challenge.html', 'budget/reto-ahorro.html', 'budget/savings-challenge.js', 'budget/lib/challenge.js', 'budget/lib/ics.js', 'budget/lib/holiday.js', 'budget/lib/dates.js', 'budget/page.js', 'budget/lib/license.js', 'budget/lib/plans.js', 'budget/lib/checkout.js', 'budget/style.css'];
const SHELL = ['./', 'index.html', 'offline.html', 'manifest.webmanifest', 'install.js', 'hub-search.js', 'search-index.json', 'es/', 'es/search-index.json', 'freelance-invoices/side-hustle.html', 'freelance-invoices/side-hustle.js', 'freelance-invoices/lib/sidehustle.js', 'freelance-invoices/config.js', 'freelance-invoices/lib/track.js', 'freelance-invoices/style.css', 'budget/icon-192.png', 'budget/icon-512.png', 'budget/config.js', 'budget/lib/track.js', ...PAYCHECK, ...AFFORD];

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
