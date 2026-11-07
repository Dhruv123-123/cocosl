import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as C from '../lib/challenge.js';

const sum = (a) => Math.round(a.reduce((t, x) => t + x, 0) * 100) / 100;

test('classic challenge: $1 to $52, $1,378 in total', () => {
  const r = C.schedule({ start: '2026-11-09' });
  assert.equal(C.CLASSIC_TOTAL, 1378);
  assert.equal(r.length, 52);
  assert.deepEqual([r[0].amount, r[51].amount, r[51].total], [1, 52, 1378]);
  assert.equal(r[1].date, '2026-11-16');
  assert.equal(r[51].date, '2027-11-01');
});

test('every style adds up to the goal exactly, in cents or whole dollars', () => {
  for (const plan of C.PLANS) {
    for (const goal of [1378, 5000, 999.99, 100]) {
      const a = C.amounts({ plan, goal });
      assert.equal(sum(a), Math.round(goal * 100) / 100, `${plan} ${goal}`);
      assert.ok(a.every((x) => x >= 0));
    }
    assert.equal(sum(C.amounts({ plan, goal: 5000, round: 'dollars' })), 5000);
  }
  const rev = C.amounts({ plan: 'reverse' });
  assert.deepEqual([rev[0], rev[51]], [52, 1]);
  const hol = C.amounts({ plan: 'holiday', goal: 2000 });
  assert.equal(hol[45], hol[50], 'flat for the last six weeks');
  assert.ok(Math.abs(hol[51] - hol[45]) < 0.1, 'only rounding on the last week');
  assert.equal(C.amounts({ plan: 'nope' })[0], 1, 'unknown style falls back to classic');
});

test('progress: ahead, behind, catch-up, streak and finish', () => {
  const r = C.schedule({ start: '2026-11-09' });
  let p = C.progress(r, { 1: true, 2: true }, '2026-11-30');
  assert.deepEqual([p.saved, p.dueWeek, p.expected, p.gap, p.next.week], [3, 4, 10, -7, 3]);
  assert.equal(p.streak, 0, 'week 3 missed');
  const cu = C.catchUp(r, { 1: true, 2: true }, '2026-11-30');
  assert.deepEqual(cu, { behind: 7, extraPerWeek: 0.14, weeksLeft: 49 });
  p = C.progress(r, { 1: true, 2: true, 3: true }, '2026-11-30');
  assert.equal(p.streak, 3, 'the week in progress does not break a streak');
  p = C.progress(r, { 1: true, 2: true, 3: true, 4: true, 10: true }, '2026-11-30');
  assert.ok(p.gap > 0);
  assert.equal(C.catchUp(r, { 1: true }, '2026-11-09'), null, 'on track in week 1');
  assert.equal(C.progress(r, {}, '2026-11-01').dueWeek, 0, 'not started');
  const all = Object.fromEntries(r.map((w) => [w.week, true]));
  p = C.progress(r, all, '2028-01-01');
  assert.ok(p.finished); assert.equal(p.left, 0); assert.equal(p.pct, 100);
});

test('next Monday', () => {
  assert.equal(C.nextMonday('2026-11-07'), '2026-11-09');
  assert.equal(C.nextMonday('2026-11-09'), '2026-11-09');
});
