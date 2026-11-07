import { test } from 'node:test';
import assert from 'node:assert/strict';
import { scams } from '../scams.mjs';
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
