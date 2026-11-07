import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync } from 'node:fs';
import * as P from '../lib/personality.js';

test('every question offers each type exactly once', () => {
  for (const q of P.QUESTIONS) assert.deepEqual(q.o.map(([, t]) => t).sort(), [...P.ORDER].sort(), q.q);
});

test('scores the top type and runner-up', () => {
  const pick = (type) => Object.fromEntries(P.QUESTIONS.map((q, i) => [i, q.o.findIndex(([, t]) => t === type)]));
  const all = pick('worrier');
  let r = P.score(all);
  assert.equal(r.top, 'worrier'); assert.equal(r.second, null); assert.equal(r.pct, 100); assert.ok(r.complete);
  const mix = { ...pick('builder'), 0: all[0], 1: all[1], 2: all[2] };
  r = P.score(mix);
  assert.equal(r.top, 'builder'); assert.equal(r.second, 'worrier');
  assert.equal(P.score({}).answered, 0);
  assert.equal(P.score({ 0: 99 }).answered, 0, 'bad option ignored');
});

test('every type links to three tools that exist', () => {
  const root = new URL('../../', import.meta.url);
  for (const [k, t] of Object.entries(P.TYPES)) {
    assert.equal(t.tools.length, 3, k);
    for (const [, href] of t.tools) {
      const path = new URL(href.endsWith('/') ? `${href}index.html` : href, root);
      assert.ok(existsSync(path), `${k}: ${href}`);
    }
  }
  assert.ok(P.isType('planner')); assert.ok(!P.isType('toString'));
});
