import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import * as C from '../lib/couples.js';

function sample(method = 'income') {
  const p = C.emptyPlan();
  C.setPartner(p, 0, { name: 'Alex', income: '6000' });
  C.setPartner(p, 1, { name: 'Sam', income: '4000' });
  C.setMethod(p, method);
  C.addExpense(p, { name: 'Rent', amount: '2000', paidBy: 'joint', category: 'home' });
  C.addExpense(p, { name: 'Groceries', amount: '600', paidBy: 'a', category: 'groceries' });
  C.addExpense(p, { name: 'Internet', amount: '80', paidBy: 'b', category: 'utilities' });
  return p;
}

test('split by income: same share of pay for both', () => {
  const s = C.summary(sample());
  assert.equal(s.shareA, 0.6);
  assert.equal(s.total, 2680);
  assert.deepEqual(s.owed, [1608, 1072]);
  assert.equal(s.pctOfIncome[0], s.pctOfIncome[1]);
  assert.deepEqual(s.joint, [1200, 800]);
  // Personally paid: Alex 600, Sam 80; fair split of 680 is 408 / 272, so Sam sends Alex 192.
  assert.deepEqual(s.settle, { from: 1, to: 0, amount: 192 });
  assert.deepEqual(s.left, [4392, 2928]);
});

test('50/50 and a custom split', () => {
  const p = sample('equal');
  let s = C.summary(p);
  assert.deepEqual(s.owed, [1340, 1340]);
  assert.deepEqual(s.settle, { from: 1, to: 0, amount: 260 });
  C.setMethod(p, 'custom', 70);
  s = C.summary(p);
  assert.deepEqual(s.owed, [1876, 804]);
  assert.throws(() => C.setMethod(p, 'coinflip'), /how to split/);
});

test('income split falls back to 50/50 until both pays are in, and cents always add up', () => {
  const p = C.emptyPlan();
  C.addExpense(p, { name: 'Power', amount: '100.01' });
  const s = C.summary(p);
  assert.equal(s.reason, 'no-income');
  assert.equal(Math.round((s.owed[0] + s.owed[1]) * 100) / 100, 100.01);
  C.setPartner(p, 0, { income: 1000 }); C.setPartner(p, 1, { income: 2000 });
  const t = C.summary(p);
  assert.equal(Math.round((t.owed[0] + t.owed[1]) * 100) / 100, 100.01);
  assert.equal(t.settle, null, 'joint-only bills need no settling');
  assert.throws(() => C.addExpense(p, { name: '', amount: 5 }), /Name/);
  assert.throws(() => C.addExpense(p, { name: 'x', amount: '-3' }), /amount/);
});

test('money date checklist, streak and notes', () => {
  const p = sample();
  for (const c of C.CHECKLIST) C.toggleCheck(p, '2026-10', c.id);
  for (const c of C.CHECKLIST) C.toggleCheck(p, '2026-09', c.id);
  assert.equal(C.progress(p, '2026-10').complete, true);
  assert.equal(C.streak(p, '2026-11'), 2, 'this month not done yet still counts the run before it');
  C.toggleCheck(p, '2026-11', 'win');
  assert.deepEqual(C.progress(p, '2026-11'), { done: 1, total: C.CHECKLIST.length, complete: false });
  assert.equal(C.toggleCheck(p, '2026-11', 'win'), false, 'toggles off');
  assert.equal(C.toggleCheck(p, '2026-11', 'nope'), false);
  C.setNote(p, '2026-11', 'Trip fund +$100');
  assert.equal(p.notes['2026-11'], 'Trip fund +$100');
  C.setNote(p, '2026-11', '');
  assert.ok(!('2026-11' in p.notes));
  assert.equal(C.monthKey(new Date(2026, 0, 5)), '2026-01');
});

test('saving and loading', () => {
  const p = sample();
  assert.deepEqual(C.loadPlan(JSON.stringify(p)), p);
  assert.deepEqual(C.loadPlan('{bad'), C.emptyPlan());
  assert.deepEqual(C.names(C.emptyPlan()), ['Partner 1', 'Partner 2']);
});

test('page: private, Budget Pro slot, offline', () => {
  const html = readFileSync(new URL('../couples.html', import.meta.url), 'utf8');
  assert.match(html, /Saved in this browser only/);
  assert.match(html, /href="pricing\.html\?from=couples" data-upgrade="couples"/);
  assert.doesNotMatch(readFileSync(new URL('../couples.js', import.meta.url), 'utf8'), /fetch\(/);
  assert.match(readFileSync(new URL('../sw.js', import.meta.url), 'utf8'), /'couples\.html', 'couples\.js', 'lib\/couples\.js'/);
});
