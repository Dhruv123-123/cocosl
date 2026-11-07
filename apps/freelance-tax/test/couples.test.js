// The "1099 Money for couples" mini-pack (launch/1099-money/couples/) quotes these figures; keep them in step
// with the tax model. Married filing jointly, one spouse's W-2 wages + the other's freelance profit, 2026.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { federalTax, incomeTax, TABLES } from '../lib/tax.js';

const gap = (wages, profit) => {
  const both = federalTax({ profit, w2Wages: wages, status: 'mfj' });
  const wagesOnly = incomeTax(Math.max(0, wages - TABLES.standardDeduction.mfj), 'mfj');
  return { total: Math.round(both.total), wagesOnly: Math.round(wagesOnly), gap: Math.round(both.total - wagesOnly) };
};

test('couples worked example: $70K wages + $40K freelance profit', () => {
  assert.deepEqual(gap(70000, 40000), { total: 13261, wagesOnly: 4040, gap: 9221 });
  assert.equal(Math.round(federalTax({ profit: 40000 }).total), 7427);  // the same profit, filing single
  assert.equal(Math.round(9221 / 26), 355);
});

test('the other two couples', () => {
  assert.equal(gap(50000, 25000).gap, 5623);
  assert.equal(gap(90000, 60000).gap, 13992);
});
