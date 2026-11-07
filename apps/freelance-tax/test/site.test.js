import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import config from '../config.js';
import { pages } from '../tools/compare-data.mjs';
import { build, notYet } from '../tools/build-pages.mjs';
import { releases, LAUNCH } from '../tools/schedule.mjs';
import { audit, LIMIT_SHARED } from '../tools/seo-audit.mjs';
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

test('no page is a near-duplicate of another (research/scouting/pinterest-seo.md)', () => {
  const rows = audit();
  assert.ok(rows.length >= 9, 'audit found the pages');
  for (const r of rows) assert.ok(r.shared <= LIMIT_SHARED, `${r.path} shares ${Math.round(r.shared * 100)}% with ${r.closest}`);
});

test('compare pages carry a byline, a staggered date and Article JSON-LD with an author', () => {
  const dates = pages.map((p) => p.published);
  assert.equal(new Set(dates).size, dates.length, 'one page a week, not all on one day');
  assert.ok(dates.every((d) => /^\d{4}-\d{2}-\d{2}$/.test(d) && d >= LAUNCH));
  for (const pg of pages) {
    const html = build().find(([r]) => r === `compare/${pg.slug}/index.html`)[1];
    const art = [...html.matchAll(/<script type="application\/ld\+json">(.*?)<\/script>/g)].map((m) => JSON.parse(m[1])).find((o) => o['@type'] === 'Article');
    assert.ok(art && art.datePublished === pg.published && art.author && art.author.name, pg.slug);
    assert.match(html, /class="byline">By <a href="\.\.\/\.\.\/about\/">/);
  }
  assert.equal(typeof config.author.name, 'string', 'config.author.name: a real person, or empty for "1099 Money"');
});

test('release build leaves out pages that are not due yet', () => {
  const at = (d) => build(d).map(([r]) => r);
  const first = at(LAUNCH);
  assert.ok(first.includes('compare/freelancer-banking/index.html'));
  assert.ok(!first.includes('compare/tax-software/index.html'));
  const sitemap = build(LAUNCH).find(([r]) => r === 'sitemap.xml')[1];
  assert.ok(!sitemap.includes('mileage/') && !sitemap.includes('s-corp-services'));
  assert.deepEqual(notYet('2027-01-01'), []);
  assert.equal(at('2027-01-01').length, build().length);
  assert.ok(Object.values(releases).every((d) => d <= '2026-12-31'), 'every page live before 1099 season');
});

test('every page links to about/', () => {
  for (const f of ['index.html', 'mileage/index.html', 'free/index.html', 'free/thanks/index.html', 'compare/index.html', 'about/index.html']) {
    assert.match(readFileSync(new URL(`../${f}`, import.meta.url), 'utf8'), /href="(\.\.\/)*about\/">About these pages/, f);
  }
});
