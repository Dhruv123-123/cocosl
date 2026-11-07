import { test } from 'node:test';
import assert from 'node:assert/strict';
import { federalTax, incomeTax, quarterlyPlan, nextPayment, dueDates } from '../lib/tax.js';

const near = (a, b, tol = 0.01) => assert.ok(Math.abs(a - b) <= tol, `${a} != ${b}`);

test('$60K single matches the worked example in the launch content and tracker', () => {
  const r = federalTax({ profit: 60000 });
  near(r.seTax, 8477.73);
  near(r.agi, 55761.14);
  near(r.qbi, 7932.23);
  near(r.incomeTax, 3559.47);
  near(r.total, 12037.20);
  near(r.effectiveRate, 0.2006, 0.001);
});

test('brackets: single and married filing jointly', () => {
  near(incomeTax(12400), 1240);
  near(incomeTax(50400), 1240 + 38000 * 0.12);
  near(incomeTax(24800, 'mfj'), 2480);
  assert.equal(incomeTax(0), 0);
});

test('no SE tax under $400 of net earnings', () => {
  assert.equal(federalTax({ profit: 400 }).seTax, 0);
  assert.ok(federalTax({ profit: 500 }).seTax > 0);
});

test('Social Security part stops at the wage base, W-2 wages count first', () => {
  const big = federalTax({ profit: 300000 });
  near(big.seTax, 184500 * 0.124 + 300000 * 0.9235 * 0.029);
  const withJob = federalTax({ profit: 50000, w2Wages: 184500 });
  near(withJob.seTax, 50000 * 0.9235 * 0.029);
});

test('safe harbor wins when last year was smaller; 110% above $150K AGI', () => {
  const p = quarterlyPlan({ profit: 60000, priorYearTax: 6500, priorYearAgi: 52000 });
  assert.equal(p.method, 'safe-harbor');
  near(p.required, 6500);
  near(p.thisPayment, 1625);
  const hi = quarterlyPlan({ profit: 250000, priorYearTax: 40000, priorYearAgi: 200000 });
  near(hi.safeHarbor, 44000);
});

test('current-year method when there is no prior-year tax, and payments already made count', () => {
  const p = quarterlyPlan({ profit: 60000, nextQuarter: 3, paidSoFar: 4000 });
  assert.equal(p.method, 'current-year');
  near(p.required, 0.9 * 12037.20);
  near(p.thisPayment, p.required * 0.75 - 4000);
  near(p.perRemaining, (p.required - 4000) / 2);
});

test('withholding reduces what estimates must cover', () => {
  const p = quarterlyPlan({ profit: 20000, w2Wages: 50000, withholding: 20000 });
  assert.equal(p.thisPayment, 0);
});

test('bad input is treated as zero', () => {
  const p = quarterlyPlan({ profit: 'abc', priorYearTax: -5 });
  assert.equal(p.total, 0);
  assert.equal(p.thisPayment, 0);
});

test('next payment from a date', () => {
  assert.equal(nextPayment(new Date(Date.UTC(2026, 10, 7))), 4);
  assert.equal(nextPayment(new Date(Date.UTC(2026, 3, 15))), 1);
  assert.equal(nextPayment(new Date(Date.UTC(2026, 3, 16))), 2);
  assert.equal(nextPayment(new Date(Date.UTC(2027, 0, 16))), 5);
  assert.equal(dueDates()[3].date.getUTCFullYear(), 2027);
});
