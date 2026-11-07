import { test } from 'node:test';
import assert from 'node:assert/strict';
import { scams } from '../scams.mjs';
import { scamsEs } from '../scams-es.mjs';
import { analyzeMessage } from '../lib/scan.js';

test('every scam guide example is flagged high risk by the checker', () => {
  for (const s of scams) {
    const r = analyzeMessage(s.example);
    assert.equal(r.level, 'high', `${s.slug} scored ${r.score}`);
    assert.ok(r.category, `${s.slug} has no category`);
  }
});

test('scam guides are complete and slugs are unique', () => {
  const slugs = new Set();
  for (const s of scams) {
    assert.match(s.slug, /^[a-z0-9-]+$/);
    assert.ok(!slugs.has(s.slug), `duplicate ${s.slug}`);
    slugs.add(s.slug);
    for (const k of ['title', 'h1', 'short', 'description', 'example', 'real', 'check']) assert.ok(s[k], `${s.slug}.${k}`);
    assert.ok(s.signs.length >= 3, `${s.slug} needs 3+ signs`);
    assert.ok(s.sources.length >= 1 && s.sources.every(([, url]) => url.startsWith('https://')), `${s.slug} sources`);
    assert.ok(s.description.length <= 200, `${s.slug} description too long for search results`);
  }
});

test('real one-time-code texts that warn you not to share stay low', () => {
  for (const msg of [
    'Your Google verification code is 482913. Do not share this code with anyone.',
    'WhatsApp code 123-456. Never share this code with anyone.',
    'Your Bank of America code is 559201. We will never call to ask for it. Don\'t share it.',
  ]) assert.equal(analyzeMessage(msg).level, 'low', msg);
});

test('every Spanish guide example is flagged high risk and matches an English guide', () => {
  const en = new Set(scams.map((s) => s.slug));
  const slugs = new Set();
  for (const s of scamsEs) {
    const r = analyzeMessage(s.example);
    assert.equal(r.level, 'high', `${s.slug} scored ${r.score}`);
    assert.ok(en.has(s.en), `${s.slug} points to missing English guide ${s.en}`);
    assert.match(s.slug, /^[a-z0-9-]+$/);
    assert.ok(!slugs.has(s.slug), `duplicate ${s.slug}`);
    slugs.add(s.slug);
    for (const k of ['title', 'h1', 'short', 'description', 'example', 'real', 'check']) assert.ok(s[k], `${s.slug}.${k}`);
    assert.ok(s.signs.length >= 3 && s.sources.length >= 1, s.slug);
    assert.ok(s.description.length <= 200, `${s.slug} description too long`);
  }
  assert.equal(scamsEs.length, scams.length, 'every English guide has a Spanish version');
});

test('each scam category links to an existing guide, in English and Spanish', async () => {
  const { GUIDES, guideFor, CATEGORIES } = await import('../lib/scan.js');
  const { existsSync } = await import('node:fs');
  for (const [id] of CATEGORIES) {
    if (!GUIDES[id]) continue;
    assert.ok(existsSync(new URL(`../${guideFor(id)}index.html`, import.meta.url)), guideFor(id));
    assert.ok(existsSync(new URL(`../es/${guideFor(id, 'es')}index.html`, import.meta.url)), guideFor(id, 'es'));
  }
  assert.equal(guideFor('nope'), null);
  assert.equal(guideFor(analyzeMessage('Your toll balance is overdue. Pay now at https://ezpass-pay.top to avoid a fine.').categoryId), 'scams/toll-text-scam/');
});
