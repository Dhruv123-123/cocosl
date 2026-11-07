import test from 'node:test';
import assert from 'node:assert/strict';
import { scorpCompare, breakEven, payroll } from '../lib/scorp.js';
import { federalTax } from '../lib/tax.js';

test('payroll tax: 7.65% each side, Social Security capped at the 2026 wage base', () => {
  assert.equal(Math.round(payroll(50000).employee), 3825);
  assert.equal(Math.round(payroll(200000).employer), Math.round(184500 * 0.062 + 200000 * 0.0145));
  assert.equal(payroll(50000).futa, 42);
});

test('worked example: $100,000 profit, $50,000 salary, $2,500 costs', () => {
  const r = scorpCompare({ profit: 100000, salary: 50000, costs: 2500 });
  assert.equal(Math.round(r.sole.total), Math.round(federalTax({ profit: 100000 }).total));
  assert.equal(Math.round(r.scorp.k1), 100000 - 50000 - 3825 - 42 - 2500);
  assert.equal(Math.round(r.scorp.employee + r.scorp.employer), 7650);
  assert.ok(r.saving > 2000 && r.saving < 2700, r.saving);
  assert.equal(Math.round(r.scorp.keep - r.sole.keep), Math.round(r.saving));
});

test('a salary equal to all the profit makes the S corp worse, and costs matter', () => {
  assert.ok(scorpCompare({ profit: 80000, salary: 80000 }).saving < 0);
  assert.ok(scorpCompare({ profit: 80000, salary: 40000, costs: 6000 }).saving < scorpCompare({ profit: 80000, salary: 40000, costs: 2500 }).saving);
  assert.equal(scorpCompare({ profit: 50000, salary: 90000 }).salary, 50000, 'salary capped at profit');
});

test('break-even rises with the salary share and with costs; range flag', () => {
  const a = breakEven({ salaryShare: 0.4 });
  const b = breakEven({ salaryShare: 0.6 });
  assert.ok(a && b && a < b);
  assert.ok(breakEven({ salaryShare: 0.5, costs: 8000 }) > breakEven({ salaryShare: 0.5, costs: 2500 }));
  assert.equal(scorpCompare({ profit: 250000, salary: 100000 }).outOfRange, true);
  assert.equal(scorpCompare({ profit: 150000, salary: 70000 }).outOfRange, false);
});
