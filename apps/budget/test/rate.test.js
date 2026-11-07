import { test } from 'node:test';
import assert from 'node:assert/strict';
import { rateBudget } from '../lib/rate.js';

const healthy = { income: 5000, housing: 1400, essentials: 900, debtPayments: 200, wants: 1000, saving: 1250, cushion: 9000, cardDebt: 0, match: 'yes' };

test('a strong budget scores an A with a "keep going" move', () => {
  const r = rateBudget(healthy);
  assert.equal(r.grade, 'A');
  assert.ok(r.score >= 95, String(r.score));
  assert.equal(r.moves[0].id, 'invest');
  assert.equal(r.parts.reduce((s, p) => s + p.max, 0), 100);
});

test('overspending is always the first move', () => {
  const r = rateBudget({ ...healthy, wants: 2800, saving: 0, match: 'no', cardDebt: 4000, cushion: 0 });
  assert.equal(r.moves[0].id, 'overspend');
  assert.ok(r.leftover < 0);
  assert.equal(r.parts.find((p) => p.id === 'plan').score, 0);
  assert.ok(['D', 'F'].includes(r.grade), r.grade);
  assert.equal(r.moves.length, 3);
});

test('missed match and card debt are flagged in order', () => {
  const r = rateBudget({ ...healthy, match: 'no', cardDebt: 2500 });
  assert.deepEqual(r.moves.slice(0, 2).map((m) => m.id), ['match', 'cards']);
  assert.match(r.moves[1].text, /\$2,500/);
});

test('cushion months use housing + essentials + debt payments', () => {
  const r = rateBudget({ ...healthy, cushion: 2500 });
  assert.equal(r.cushionMonths, 1);
  assert.ok(r.moves.some((m) => m.id === 'cushion'));
});

test('unplanned money is called out', () => {
  const r = rateBudget({ ...healthy, saving: 200 });
  assert.ok(r.moves.some((m) => m.id === 'assign'));
});

test('input validation', () => {
  assert.throws(() => rateBudget({ ...healthy, income: 0 }), /take-home/);
  assert.throws(() => rateBudget({ ...healthy, housing: -5 }), RangeError);
});
