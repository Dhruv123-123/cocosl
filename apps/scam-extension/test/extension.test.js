import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
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
  assert.deepEqual(m.permissions.sort(), ['activeTab', 'contextMenus', 'storage']);
  assert.equal(m.host_permissions, undefined);
  assert.deepEqual(m.optional_permissions, ['tabs']);
});

test('a bare domain without https:// is still checked', () => {
  assert.equal(checkPage('paypa1-secure.com/login').level, 'high');
  assert.equal(checkPage('www.paypal.com').level, 'official');
});
