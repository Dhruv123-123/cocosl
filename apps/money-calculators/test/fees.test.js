import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { analyzeFees, growth } from '../lib/fees.js';
import { TEXT } from '../lib/text.js';

const FUNDS = [
  { name: 'S&P 500 Index', category: 'us-stock', expenseRatio: 0.04, balance: 18000 },
  { name: 'Large Cap Growth', category: 'us-stock', expenseRatio: 0.82, balance: 12000 },
  { name: 'International Index', category: 'intl-stock', expenseRatio: 0.08, balance: 6000 },
  { name: 'Target Date 2055', category: 'target-date', expenseRatio: 0.65, balance: 9000 },
];

test('growth matches the closed-form future value', () => {
  const r = 0.07 / 12; const n = 360;
  const want = 1000 * (1 + r) ** n + 100 * (((1 + r) ** n - 1) / r);
  assert.ok(Math.abs(growth(1000, 100, 30, 7) - want) < 0.01);
  assert.equal(growth(500, 10, 2, 0), 740);
});

test('fees in dollars, average expense ratio and 30-year drag', () => {
  const r = analyzeFees(FUNDS, { monthly: 500, years: 30, annualReturn: 7 });
  assert.equal(r.total, 45000);
  assert.equal(r.funds[0].yearlyFee, 7.2);
  assert.equal(r.funds[1].yearlyFee, 98.4);
  assert.equal(r.yearlyFees, 7.2 + 98.4 + 4.8 + 58.5);
  assert.equal(r.avgExpenseRatio, 0.375); // (720 + 9840 + 480 + 5850) / 45000 = 0.3753
  assert.ok(r.feeDrag > 40000 && r.feeDrag < 90000, `drag ${r.feeDrag}`);
  assert.ok(r.endWithFees < r.lowestCostEnd && r.lowestCostEnd < r.endNoFees);
  // The cheaper US stock fund is pointed out; one-of-a-kind categories aren't.
  assert.deepEqual(r.funds[1].cheaperInCategory, { name: 'S&P 500 Index', expenseRatio: 0.04 });
  assert.equal(r.funds[0].cheaperInCategory, null);
  assert.equal(r.funds[3].cheaperInCategory, null);
});

test('no balance yet: funds weigh equally, and errors are plain English', () => {
  const r = analyzeFees([{ expenseRatio: 0.1, balance: 0 }, { expenseRatio: 0.5, balance: 0 }], { monthly: 300, years: 20 });
  assert.equal(r.avgExpenseRatio, 0.3);
  assert.equal(r.yearlyFees, 0);
  assert.ok(r.feeDrag > 0);
  assert.equal(r.funds[0].name, 'Fund 1');
  assert.throws(() => analyzeFees([]), /at least one fund/);
  assert.throws(() => analyzeFees([{ expenseRatio: 12, balance: 1 }]), /percent/);
  assert.throws(() => analyzeFees([{ expenseRatio: NaN, balance: 1 }]), /expense ratio/);
  assert.throws(() => analyzeFees([{ expenseRatio: 0.1, balance: NaN }]), /balance/);
  assert.throws(() => analyzeFees(FUNDS, { years: 0 }), /Years/);
});

test('fee checker copy exists in both languages and never tells people what to buy', () => {
  for (const lang of ['en', 'es']) {
    const t = TEXT[lang].fees;
    assert.equal(Object.keys(t.categories).length, 6);
    const html = t.result(analyzeFees(FUNDS)) + t.gap(analyzeFees(FUNDS)) + t.note;
    assert.doesNotMatch(html, /\byou should (buy|switch)|deberías (comprar|cambiarte)/i);
  }
  const page = readFileSync(new URL('../401k-fees/index.html', import.meta.url), 'utf8');
  assert.match(page, /id="funds"/);
  assert.match(page, /FAQPage/);
});
