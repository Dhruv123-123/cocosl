import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { ROOT } from '../../tools/sync-shared.mjs';
import { shouldOffer, isIos } from '../../install.js';

const read = (f) => readFileSync(join(ROOT, f), 'utf8');
const exists = (href) => {
  const p = join(ROOT, href.split(/[?#]/)[0]);
  return existsSync(p) && (!statSync(p).isDirectory() || existsSync(join(p, 'index.html')));
};

test('every tool on the hub exists, and the hub lists it for search engines', () => {
  const html = read('index.html');
  const cards = [...html.matchAll(/<a class="card[^"]*" href="([^"]+)"/g)].map((m) => m[1]);
  assert.ok(cards.length >= 25, `only ${cards.length} cards`);
  for (const href of cards) assert.ok(exists(href), href);
  const listed = [...html.matchAll(/"url":"([^"]+)"/g)].map((m) => m[1]);
  for (const href of cards) assert.ok(listed.includes(href), `${href} missing from the ItemList`);
  for (const href of listed) assert.ok(exists(href), href);
});

test('installable: manifest, icons, service worker, offline page', () => {
  const m = JSON.parse(read('manifest.webmanifest'));
  assert.equal(m.display, 'standalone');
  assert.ok(m.icons.some((i) => i.sizes === '192x192') && m.icons.some((i) => i.sizes === '512x512') && m.icons.some((i) => i.purpose === 'maskable'));
  for (const i of [...m.icons, ...m.shortcuts.map((s) => ({ src: s.url }))]) assert.ok(exists(i.src), i.src);
  const html = read('index.html');
  assert.match(html, /<link rel="manifest" href="manifest\.webmanifest">/);
  assert.match(html, /src="install\.js"/);
  assert.match(html, /\[hidden\]\{display:none!important\}/, 'the install banner stays hidden until offered');
  assert.match(html, /<div id="install" class="install" hidden>/);
  const sw = read('sw.js');
  // Every file listed in SHELL (and the PAYCHECK / AFFORD lists it spreads in) must exist.
  const listed = [...sw.matchAll(/^const (?:SHELL|PAYCHECK|AFFORD) = \[([^\]]+)\]/gm)].flatMap((m) => [...m[1].matchAll(/'([^']+)'/g)].map((x) => x[1]));
  assert.ok(listed.length > 25, `precache list (${listed.length})`);
  for (const f of listed) assert.ok(exists(f === './' ? 'index.html' : f.endsWith('/') ? `${f}index.html` : f), f);
  for (const f of ['money-calculators/lib/state-tax-2026.js', 'money-calculators/student-loans/', 'money-calculators/rent-vs-buy/', 'money-calculators/lib/student-loans.js', 'money-calculators/take-home-pay/', 'budget/afford.html', 'budget/lib/afford.js']) assert.ok(listed.includes(f), `${f} is saved for offline`);
  assert.match(sw, /startsWith\('\/api\/'\)/, 'never caches the API');
  assert.match(read('netlify.toml'), /for = "\/sw\.js"[\s\S]*no-cache/);
});

test('install banner: not when installed, quiet for 30 days after "Not now", iOS detection', () => {
  assert.equal(shouldOffer({ standalone: true }), false);
  assert.equal(shouldOffer({ standalone: false, dismissedAt: null }), true);
  assert.equal(shouldOffer({ standalone: false, dismissedAt: '1000', now: 1000 + 86400000 }), false);
  assert.equal(shouldOffer({ standalone: false, dismissedAt: '1000', now: 1000 + 31 * 86400000 }), true);
  assert.equal(isIos('Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X)'), true);
  assert.equal(isIos('Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0)', 5), true, 'iPad in desktop mode');
  assert.equal(isIos('Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0)', 0), false);
  assert.equal(isIos('Mozilla/5.0 (Linux; Android 15)'), false);
});

test('paid template cards: placeholder until the checkout link is real, then a link', async () => {
  const { productCard } = await import('../../products.js');
  const p = { name: 'Money Dashboard Pro', nameEs: 'Tablero de dinero Pro', price: '$12', pitch: 'EN <b>', pitchEs: 'ES', url: 'https://REPLACE_ME.gumroad.com/l/x' };
  assert.equal(productCard(p), null);
  assert.equal(productCard({ ...p, url: 'javascript:alert(1)' }), null);
  const live = productCard({ ...p, url: 'https://shop.gumroad.com/l/x' }, 'es');
  assert.match(live, /^<a class="card" href="https:\/\/shop\.gumroad\.com\/l\/x">/);
  assert.match(live, /Tablero de dinero Pro/);
  const en = productCard({ ...p, url: 'https://shop.gumroad.com/l/x' });
  assert.match(en, /EN &lt;b&gt;/);
  for (const f of ['index.html', 'es/index.html']) {
    const html = read(f);
    assert.match(html, /<div class="card product" data-product="sheetTemplate"/, f);
    assert.match(html, /showProducts\(config\)/, f);
  }
});
