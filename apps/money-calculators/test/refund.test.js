import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as R from '../lib/refund.js';
import { STANDARD_DEDUCTION, BRACKETS } from '../lib/tax2026.js';

test('2026 head of household figures from Rev. Proc. 2025-32', () => {
  assert.equal(STANDARD_DEDUCTION.hoh, 24150);
  assert.deepEqual(BRACKETS.hoh.map(([u]) => u).slice(0, 6), [17700, 67450, 105700, 201750, 256200, 640600]);
  assert.equal(R.incomeTax(17700, 'hoh'), 1770);
  assert.equal(R.incomeTax(67450, 'hoh'), 1770 + 0.12 * (67450 - 17700));
});

test('single W-2 worker: $55k wages, $5,200 withheld gets $780 back', () => {
  const r = R.estimateRefund({ filing: 'single', wages: 55000, withheld: 5200 });
  assert.equal(r.taxable, 38900);
  assert.equal(r.tax, 4420);
  assert.equal(r.refund, 780);
  assert.equal(r.marginal, 0.12);
});

test('owing shows as a negative refund', () => {
  const r = R.estimateRefund({ filing: 'single', wages: 80000, withheld: 5000 });
  assert.ok(r.refund < -1000 && r.owesMuch);
});

test('child tax credit: $2,200 each, $1,700 refundable, capped at 15% of earnings over $2,500', () => {
  const r = R.estimateRefund({ filing: 'hoh', wages: 30000, withheld: 800, kids: 2 });
  assert.equal(r.tax, 585);
  assert.equal(r.nonrefundable, 585);
  assert.equal(r.refundableCredit, 3400);
  assert.equal(r.refund, 4200);
  const low = R.estimateRefund({ filing: 'hoh', wages: 10000, kids: 2 });
  assert.equal(low.refundableCredit, 1125, '15% of $7,500');
});

test('child credit phases out $50 per $1,000 over $200k single / $400k joint', () => {
  assert.equal(R.estimateRefund({ filing: 'single', wages: 210000, kids: 1 }).credit, 1700);
  assert.equal(R.estimateRefund({ filing: 'married', wages: 410000, kids: 1 }).credit, 1700);
  assert.equal(R.estimateRefund({ filing: 'married', wages: 400000, kids: 1, otherDeps: 1 }).credit, 2700);
});

test('tips and overtime deductions: caps and phase-out above $150k', () => {
  assert.equal(R.estimateRefund({ filing: 'single', wages: 60000, tips: 30000 }).tipsDed, 25000);
  assert.equal(R.estimateRefund({ filing: 'single', wages: 60000, overtime: 20000 }).otDed, 12500);
  assert.equal(R.estimateRefund({ filing: 'married', wages: 90000, overtime: 30000 }).otDed, 25000);
  assert.equal(R.estimateRefund({ filing: 'single', wages: 160000, tips: 5000 }).tipsDed, 4000);
});

test('65 and older: extra standard deduction plus the $6,000 senior deduction', () => {
  const r = R.estimateRefund({ filing: 'married', wages: 50000, seniors: 2 });
  assert.equal(r.standard, 32200 + 2 * 1650);
  assert.equal(r.seniorDed, 12000);
  assert.equal(R.estimateRefund({ filing: 'single', wages: 85000, seniors: 1 }).seniorDed, 5400);
  assert.equal(R.estimateRefund({ filing: 'single', wages: 50000, seniors: 2 }).seniors === undefined, true);
  assert.equal(R.estimateRefund({ filing: 'single', wages: 50000, seniors: 2 }).seniorDed, 6000, 'one person max when single');
});

test('bad input falls back safely', () => {
  const r = R.estimateRefund({ filing: 'nope', wages: -5, withheld: 'x' });
  assert.equal(r.filing, 'single');
  assert.equal(r.refund, 0);
});
