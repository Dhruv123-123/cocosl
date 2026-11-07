import { test } from 'node:test';
import assert from 'node:assert/strict';
import { emptyGroup, loadGroup, weights, splitCents, settleUp, summary, splitCsv, splitText } from '../lib/splitbills.js';

const group = () => {
  const g = emptyGroup(3);
  g.people = [{ name: 'Ana', income: 6000, pct: 50 }, { name: 'Ben', income: 3000, pct: 30 }, { name: 'Cy', income: 3000, pct: 20 }];
  return g;
};

test('weights for each method, with an equal fallback', () => {
  const g = group();
  assert.deepEqual(weights(g, 'income'), [0.5, 0.25, 0.25]);
  assert.deepEqual(weights(g, 'custom'), [0.5, 0.3, 0.2]);
  assert.deepEqual(weights(emptyGroup(2), 'income'), [0.5, 0.5]);
});

test('splits in cents always add up', () => {
  const p = splitCents(100, [1 / 3, 1 / 3, 1 / 3]);
  assert.deepEqual(p, [33.34, 33.33, 33.33]);
  for (const a of [0.01, 99.99, 1234.57]) assert.equal(Math.round(splitCents(a, [0.41, 0.29, 0.3]).reduce((x, y) => x + y, 0) * 100), Math.round(a * 100));
});

test('settle up uses the fewest payments and balances to zero', () => {
  const m = settleUp([3000, -1000, -2000]);
  assert.deepEqual(m, [{ from: 2, to: 0, amount: 20 }, { from: 1, to: 0, amount: 10 }]);
  assert.deepEqual(settleUp([0, 0]), []);
});

test('summary: rent by income, internet split equally, who owes whom', () => {
  const g = group();
  g.bills = [
    { id: 'r', name: 'Rent', amount: 2400, paidBy: 0, method: 'group' },
    { id: 'i', name: 'Internet', amount: 90, paidBy: 1, method: 'equal' },
  ];
  const s = summary(g);
  assert.deepEqual(s.rows[0].parts, [1200, 600, 600]);
  assert.deepEqual(s.rows[1].parts, [30, 30, 30]);
  assert.deepEqual(s.share, [1230, 630, 630]);
  assert.deepEqual(s.balance, [1170, -540, -630]);
  assert.deepEqual(s.moves, [{ from: 2, to: 0, amount: 630 }, { from: 1, to: 0, amount: 540 }]);
  assert.equal(s.pctOfIncome[0], 0.205);
  const csv = splitCsv(g, s);
  assert.match(csv, /^Bill,Amount,Paid by,Split,Ana,Ben,Cy\r\nRent,2400.00,Ana,By income,1200.00,600.00,600.00\r\n/);
  assert.match(csv, /\r\nBalance,,,,1170.00,-540.00,-630.00\r\n$/);
  assert.match(splitText(g, s), /Cy → Ana: \$630\.00/);
  assert.match(splitCsv(g, s, 'es'), /^Gasto,Monto,Pagó,División/);
});

test('loadGroup cleans bad data', () => {
  assert.equal(loadGroup('nope').people.length, 2);
  const g = loadGroup({ people: [{ name: 'A' }, { name: 'B' }], bills: [{ name: 'X', amount: 10, paidBy: 9 }, { name: '', amount: 5 }], method: 'weird' });
  assert.equal(g.bills.length, 1);
  assert.equal(g.bills[0].paidBy, 0);
  assert.equal(g.method, 'income');
});
