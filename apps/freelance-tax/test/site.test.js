import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import config from '../config.js';
import { pages } from '../tools/compare-data.mjs';
import { build } from '../tools/build-pages.mjs';
import { tagCheckout, pageName, live } from '../site.js';

test('compare pages and sitemap are up to date with compare-data.mjs', () => {
  for (const [rel, html] of build()) assert.equal(readFileSync(new URL(`../${rel}`, import.meta.url), 'utf8'), html, `${rel} is stale: run node tools/build-pages.mjs`);
});

test('five comparison pages, each with a disclosure, FAQ and real provider homepages', () => {
  assert.deepEqual(pages.map((p) => p.slug), ['freelancer-banking', 'tax-software', 'invoicing-tools', 's-corp-services', 'health-insurance']);
  for (const [rel, html] of build().filter(([r]) => r.startsWith('compare/') && r !== 'compare/index.html')) {
    assert.match(html, /How we picked/, rel);
    assert.match(html, /"@type":"FAQPage"/, rel);
    assert.ok(!html.includes('REPLACE_ME'), `${rel} hard-codes a placeholder link`);
    for (const m of html.matchAll(/href="(https?:[^"]+)"/g)) assert.doesNotMatch(m[1], /utm_/, `${rel}: no UTM on outside links`);
  }
});

test('every affiliate key on the pages exists in config.js', () => {
  for (const pg of pages) for (const p of pg.providers) if (p.aff) assert.ok(config.affiliates[p.aff], `${pg.slug}: ${p.aff} missing from config.affiliates`);
  assert.ok(Object.values(config.affiliates).every((a) => !live(a.url)), 'only placeholder affiliate links until programs approve us');
});

test('checkout links get UTM per docs/UTM.md; others are left alone', () => {
  assert.equal(tagCheckout('https://me.gumroad.com/l/x', null, 'compare-tax-software'),
    'https://me.gumroad.com/l/x?utm_source=freelance-tax&utm_medium=app&utm_campaign=compare-tax-software');
  assert.equal(tagCheckout('https://me.gumroad.com/l/x', [['utm_source', 'pinterest'], ['utm_medium', 'social'], ['utm_campaign', 'pin-1']], 'calculator'),
    'https://me.gumroad.com/l/x?utm_source=pinterest&utm_medium=social&utm_campaign=pin-1');
  assert.equal(tagCheckout('https://me.gumroad.com/l/x?utm_source=x', null, 'calculator'), 'https://me.gumroad.com/l/x?utm_source=x');
  assert.match(tagCheckout('https://buy.stripe.com/abc', null, 'free'), /client_reference_id=freelance-tax__app__free/);
  assert.equal(tagCheckout('https://keepertax.com/', null, 'calculator'), 'https://keepertax.com/');
});

test('page names used as utm_campaign', () => {
  assert.equal(pageName('/'), 'calculator');
  assert.equal(pageName('/free/thanks/'), 'free-thanks');
  assert.equal(pageName('/compare/tax-software/index.html'), 'compare-tax-software');
  assert.equal(pageName('/apps/freelance-tax/compare/'), 'compare');
});
