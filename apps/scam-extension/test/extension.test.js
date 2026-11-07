import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { checkPage, badgeFor, menuText } from '../lib/site.js';
import { analyzeMessage } from '../lib/scan.js';
import { translateResult } from '../lib/i18n.js';

test('official and everyday sites never get a warning', () => {
  for (const url of ['https://www.paypal.com/signin', 'https://usps.com/track', 'https://www.irs.gov/payments', 'https://smile.amazon.com/']) {
    assert.equal(checkPage(url).level, 'official', url);
  }
  for (const url of ['https://news.ycombinator.com/', 'https://s3.amazonaws.com/bucket/x', 'https://en.wikipedia.org/wiki/PayPal', 'https://example.shop/']) {
    assert.notEqual(checkPage(url).level, 'high', url);
    assert.equal(badgeFor(checkPage(url).level), null, url);
  }
});

test('look-alike and brand-impersonating sites are high risk with a badge', () => {
  for (const url of ['https://paypa1-secure.com/login', 'https://usps-redelivery-center.top/track', 'https://amaz0n-account.help/verify']) {
    const v = checkPage(url);
    assert.equal(v.level, 'high', `${url} ${JSON.stringify(v)}`);
    assert.deepEqual(badgeFor(v.level), { text: '!', color: '#c62828' });
  }
});

test('a raw IP address is a caution, not a red badge (home routers use them)', () => {
  const v = checkPage('http://192.168.4.20/login');
  assert.equal(v.level, 'medium');
  assert.equal(badgeFor(v.level), null);
});

test('browser pages and junk are ignored', () => {
  for (const url of ['chrome://extensions', 'about:blank', 'file:///tmp/x.html', '', 'not a url', 'hello there']) assert.equal(checkPage(url).level, 'none', url);
});

test('right-click text: links send the URL, selections are trimmed and capped', () => {
  assert.equal(menuText({ menuItemId: 'check-link', linkUrl: 'https://bit.ly/x', selectionText: 'ignored' }), 'https://bit.ly/x');
  assert.equal(menuText({ menuItemId: 'check-selection', selectionText: '  hi  ' }), 'hi');
  assert.equal(menuText({ menuItemId: 'check-selection', selectionText: 'x'.repeat(9000) }).length, 4000);
  assert.equal(menuText({ menuItemId: 'check-selection' }), '');
});

test('Spanish results translate every user-facing string', () => {
  const r = translateResult(analyzeMessage('USPS: Su paquete no pudo ser entregado. Pague $1.99 hoy: https://usps-entrega.top/pagar', { sender: 'USPS <alerts@gmail.com>' }));
  assert.equal(r.level, 'high');
  assert.match(r.category, /entrega|Phishing/i);
  assert.ok(r.steps.every((s) => typeof s === 'string' && !/^(Don't|Report|To check)/.test(s)));
  assert.ok(r.links[0].issues.every((i) => !/^(Uses|Link)/.test(i.label)), JSON.stringify(r.links[0].issues));
});

test('the generated lib copies match the checker source', () => {
  for (const f of ['scan.js', 'i18n.js', 'site.js']) {
    const copy = readFileSync(new URL(`../lib/${f}`, import.meta.url), 'utf8');
    const original = readFileSync(new URL(`../../scam-checker/lib/${f}`, import.meta.url), 'utf8');
    assert.ok(copy.endsWith(original), `${f} is stale: run node scam-extension/build.mjs`);
  }
});

test('manifest asks only for narrow permissions', () => {
  const m = JSON.parse(readFileSync(new URL('../manifest.json', import.meta.url), 'utf8'));
  assert.equal(m.manifest_version, 3);
  assert.deepEqual(m.permissions.sort(), ['activeTab', 'contextMenus', 'scripting', 'storage']);
  assert.equal(m.host_permissions, undefined);
  assert.deepEqual(m.optional_permissions, ['tabs']);
});

test('a bare domain without https:// is still checked', () => {
  assert.equal(checkPage('paypa1-secure.com/login').level, 'high');
  assert.equal(checkPage('www.paypal.com').level, 'official');
});

test('page words: pressure plus a scam pattern is flagged, shops and official sites are not', async () => {
  const { pageTextVerdict } = await import('../lib/site.js');
  const scam = pageTextVerdict('URGENT: your account will be suspended in 24 hours. Pay the outstanding toll balance now with a gift card.', 'https://ezpass-billing.top/pay');
  assert.equal(scam.level, 'high');
  assert.equal(scam.categoryId, 'toll');
  assert.equal(pageTextVerdict('Holiday sale! Gift cards make great presents. Free shipping over $35.', 'https://shop.example.com/').level, 'low');
  assert.equal(pageTextVerdict('Your account will be suspended. Verify now.', 'https://www.paypal.com/signin').level, 'none', 'official site skipped');
  assert.equal(pageTextVerdict('anything', 'chrome://settings').level, 'none');
});

test('explainer links: Scam Shield guides and Scam Decoded explainers', async () => {
  const { explainerUrl } = await import('../lib/site.js');
  const shield = (await import('../lib/config.js')).default.explainers;
  assert.match(explainerUrl(shield, 'toll'), /\/scams\/toll-text-scam\/$/);
  assert.match(explainerUrl(shield, 'toll', 'es'), /\/es\/estafas\/mensaje-peaje-sin-pagar\/$/);
  assert.equal(explainerUrl(shield, 'nope'), null);
  assert.equal(explainerUrl({ base: 'https://x/', map: { a: '../evil' } }, 'a'), null);
  const decoded = JSON.parse(readFileSync(new URL('../brands/scam-decoded.json', import.meta.url), 'utf8'));
  // The explainer pages on the Scam Decoded site (sites/scam-decoded/public/scams/, PR #9).
  const SITE = ['bank-impersonation-calls', 'breach-follow-ups', 'fake-charity-scams', 'fake-order-and-refund-emails', 'family-emergency-scams', 'gift-card-scams', 'government-impostor-scams', 'investment-and-crypto-scams', 'job-and-task-scams', 'lookalike-links', 'online-marketplace-scams', 'package-delivery-texts', 'prize-and-lottery-scams', 'romance-scams', 'tech-support-scams', 'toll-texts', 'verification-code-scams'];
  for (const [k, slug] of Object.entries(decoded.explainers.map)) assert.ok(SITE.includes(slug), `${k}: ${slug}`);
  assert.equal(explainerUrl(decoded.explainers, 'lookalike'), 'https://scamdecoded.netlify.app/scams/lookalike-links/');
});

test('Scam Decoded build is complete and current: run node scam-extension/build.mjs --brand scam-decoded', () => {
  const dir = new URL('../build/scam-decoded/', import.meta.url);
  const m = JSON.parse(readFileSync(new URL('manifest.json', dir), 'utf8'));
  assert.equal(m.short_name, 'Scam Decoded');
  assert.equal(m.homepage_url, 'https://scamdecoded.netlify.app');
  assert.deepEqual(m.permissions.sort(), ['activeTab', 'contextMenus', 'scripting', 'storage']);
  assert.equal(m.host_permissions, undefined);
  for (const size of Object.values(m.icons)) assert.ok(existsSync(new URL(size, dir)), size);
  for (const f of ['popup.html', 'popup.js', 'background.js']) assert.equal(readFileSync(new URL(f, dir), 'utf8'), readFileSync(new URL(`../${f}`, import.meta.url), 'utf8'), f);
  for (const f of ['scan.js', 'i18n.js', 'site.js']) assert.ok(readFileSync(new URL(`lib/${f}`, dir), 'utf8').endsWith(readFileSync(new URL(`../../scam-checker/lib/${f}`, import.meta.url), 'utf8')), f);
  assert.match(readFileSync(new URL('popup.css', dir), 'utf8'), /--brand: #12766d/);
  const msgs = JSON.parse(readFileSync(new URL('_locales/en/messages.json', dir), 'utf8'));
  assert.equal(msgs.extName.message, 'Scam Decoded: Is This a Scam?');
});

test('popup code sends nothing: no fetch, no XHR, no remote scripts', () => {
  for (const f of ['popup.js', 'background.js', 'popup.html']) {
    const code = readFileSync(new URL(`../${f}`, import.meta.url), 'utf8');
    assert.doesNotMatch(code, /fetch\(|XMLHttpRequest|sendBeacon|<script[^>]+src="https?:/, f);
  }
});
