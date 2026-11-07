// Offline support: cache the app shell, network-first so updates arrive when online.
const CACHE = 'budget-v16';
const SHELL = ['./', 'index.html', 'style.css', 'app.js', 'config.js', 'lib/budget.js', 'lib/plans.js', 'lib/license.js', 'lib/recurring.js', 'subscriptions.html', 'subscriptions.js', 'rate.html', 'rate.js', 'lib/rate.js', 'lib/track.js', 'lib/dates.js', 'lib/ics.js', 'lib/bills.js', 'lib/promos.js', 'lib/checkout.js', 'pricing.html', 'pricing.js', 'disputes.html', 'disputes.js', 'lib/disputes.js', 'lib/statement.js', 'networth.html', 'networth.js', 'lib/networth.js', 'lib/pdf.js', 'holiday.html', 'holiday.js', 'lib/holiday.js', 'afford.html', 'afford.js', 'lib/afford.js', 'couples.html', 'couples.js', 'lib/couples.js', 'first-paycheck.html', 'first-paycheck.js', 'lib/firstpaycheck.js', 'checkup.html', 'checkup.js', 'lib/checkup.js', 'money-personality.html', 'money-personality.js', 'lib/personality.js', 'savings-challenge.html', 'reto-ahorro.html', 'savings-challenge.js', 'lib/challenge.js', 'money-dashboard.html', 'tablero-dinero.html', 'money-dashboard.js', 'lib/dashboard.js', 'lib/xlsx.js', 'page.js', 'icon-192.png', 'icon-512.png', 'bills.html', 'bills.js', 'deals.html', 'deals.js', 'icon.svg', 'manifest.webmanifest'];
self.addEventListener('install', (e) => e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting())));
self.addEventListener('activate', (e) => e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET' || url.origin !== location.origin || url.pathname.startsWith('/api/')) return;
  e.respondWith(fetch(e.request).then((res) => { const copy = res.clone(); caches.open(CACHE).then((c) => c.put(e.request, copy)); return res; }).catch(() => caches.match(e.request)));
});
