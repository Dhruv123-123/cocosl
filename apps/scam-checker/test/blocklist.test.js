import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { hash53, candidates, cleanDomain, encode, decode, lookup, loadBlocklist } from '../lib/blocklist.js';
import { buildList, MAX_BYTES, K } from '../tools/refresh-blocklist.mjs';

const at = (p) => new URL(p, import.meta.url);

test('hash is stable (the browser must get the same numbers the refresh script wrote)', () => {
  assert.equal(hash53('paypa1-secure.com'), hash53('paypa1-secure.com'));
  assert.notEqual(hash53('a.com'), hash53('b.com'));
  assert.ok(Number.isSafeInteger(hash53('x'.repeat(300))));
});

test('candidates walk up to the registrable domain', () => {
  assert.deepEqual(candidates('Login.Secure.Evil.com'), ['login.secure.evil.com', 'secure.evil.com', 'evil.com']);
  assert.deepEqual(candidates('www.shop.co.uk'), ['shop.co.uk']);
  assert.deepEqual(candidates('evil.com.'), ['evil.com']);
});

test('source lines are cleaned to bare hostnames', () => {
  assert.equal(cleanDomain('0.0.0.0 Bad-Site.com'), 'bad-site.com');
  assert.equal(cleanDomain('||bad.top^'), 'bad.top');
  assert.equal(cleanDomain('# comment'), '');
  assert.equal(cleanDomain('not a domain'), '');
});

test('encode and decode round-trip; lookups find listed domains and their subdomains only', () => {
  const list = ['evil-login.com', 'x.pages.dev', 'paypa1-secure.com'];
  const set = decode(encode(list, { k: 12, date: '2026-11-07' }));
  assert.equal(set.n, 3);
  assert.equal(set.date, '2026-11-07');
  assert.equal(lookup(set, 'evil-login.com'), 'evil-login.com');
  assert.equal(lookup(set, 'account.evil-login.com'), 'evil-login.com');
  assert.equal(lookup(set, 'x.pages.dev'), 'x.pages.dev');
  assert.equal(lookup(set, 'y.pages.dev'), null);
  assert.equal(lookup(set, 'paypal.com'), null);
  assert.equal(lookup(null, 'evil-login.com'), null);
});

test('the list is built from both sources, minus allowlisted, official and shared hosts', () => {
  const kids = Array.from({ length: 30 }, (_, i) => `scam${i}.freehost.io`).join('\n');
  const r = buildList({
    primaryActive: `# header\nevil-login.com\nirs.gov\nfine.example\nfreehost.io\n${kids}`,
    primary: 'pd-and-dl.com',
    communityActive: '',
    allow: '["fine.example", ".paypal.com"]',
    phishingDatabase: 'pd-and-dl.com\npd-only.com\nlogin.paypal.com',
  });
  assert.ok(r.list.includes('evil-login.com'));
  assert.ok(r.list.includes('pd-and-dl.com'), 'Phishing.Database entry confirmed by DestroyList');
  assert.ok(!r.list.includes('pd-only.com'), 'Phishing.Database-only entries are left out');
  assert.ok(!r.list.includes('irs.gov'), 'official domains are never listed');
  assert.ok(!r.list.includes('fine.example'), 'allowlist is respected');
  assert.ok(!r.list.includes('freehost.io'), 'shared host parent is dropped');
  assert.ok(r.list.includes('scam3.freehost.io'), 'its listed subdomains stay');
});

test('shipped list: small enough to stay light, matches its notes, and never flags official sites', () => {
  const file = at('../phishlist/phish.bin');
  assert.ok(existsSync(file), 'run node scam-checker/tools/refresh-blocklist.mjs');
  const buf = readFileSync(file);
  assert.ok(buf.length <= MAX_BYTES, `phish.bin is ${Math.round(buf.length / 1024)} KB; the limit is ${MAX_BYTES / 1024} KB`);
  const set = decode(buf);
  const meta = JSON.parse(readFileSync(at('../phishlist/phish-meta.json'), 'utf8'));
  assert.equal(set.k, K);
  assert.equal(set.n, meta.entries);
  assert.equal(set.date, meta.date);
  assert.equal(buf.length, meta.bytes);
  for (const d of ['google.com', 'paypal.com', 'irs.gov', 'usps.com', 'amazon.com', 'chase.com', 'netlify.app', 'pages.dev', 'github.io', 'vercel.app', 'appspot.com']) {
    assert.equal(lookup(set, d), null, `${d} must not be flagged`);
  }
  assert.match(readFileSync(at('../phishlist/NOTICE.txt'), 'utf8'), /Copyright \(c\) 2019 PhishDestroy[\s\S]*Copyright \(c\) 2018-2025 Mitchell Krog/);
});

test('the list loads only when someone checks a link, never at install or page load', () => {
  const sw = readFileSync(at('../sw.js'), 'utf8');
  assert.ok(!sw.includes('phish.bin'), 'not in the service worker install list');
  for (const p of ['../link/index.html', '../es/enlace/index.html', '../index.html', '../app/index.html']) {
    assert.ok(!readFileSync(at(p), 'utf8').includes('phish.bin'), `${p} must not preload the list`);
  }
});

test('loadBlocklist fetches the list once per page', async () => {
  let calls = 0;
  const bin = encode(['evil-login.com'], { k: 10, date: '2026-11-07' });
  const ok = async () => { calls++; return { ok: true, arrayBuffer: async () => bin.buffer }; };
  // module-level cache: first call wins for the page
  const a = await loadBlocklist('x', ok);
  const b = await loadBlocklist('x', ok);
  assert.equal(calls, 1);
  assert.equal(a, b);
  assert.equal(lookup(a, 'evil-login.com'), 'evil-login.com');
});
