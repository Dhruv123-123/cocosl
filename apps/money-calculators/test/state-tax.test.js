import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { STATES, STATE_OPTIONS, stateIncomeTax } from '../lib/state-tax-2026.js';
import { takeHomePay } from '../lib/calc.js';
import { NO_WAGE_TAX_STATES } from '../lib/tax2026.js';

test('every state and DC is in the table, with sane brackets', () => {
  assert.equal(Object.keys(STATES).length, 51);
  assert.equal(STATE_OPTIONS[0][1], 'Alabama');
  for (const [code, s] of Object.entries(STATES)) {
    if (s.none) continue;
    for (const f of ['single', 'married']) {
      const b = s[f];
      assert.ok(b.length, `${code} ${f}`);
      for (let i = 1; i < b.length; i++) assert.ok(b[i][0] > b[i - 1][0], `${code} ${f} thresholds rise`);
      for (const [, rate] of b) assert.ok(rate > 0 && rate < 15, `${code} rate ${rate}`);
    }
  }
  const none = Object.values(STATES).filter((s) => s.none).map((s) => s.name).sort();
  assert.deepEqual(none, [...NO_WAGE_TAX_STATES].sort(), 'no-tax list matches the federal file');
});

test('flat, graduated and zero-first-bracket states', () => {
  // Ohio: 2.75% above $26,050 after a $2,400 exemption.
  assert.equal(stateIncomeTax('OH', { wages: 57000 }).tax, 785.13);
  // Illinois flat 4.95% after the $2,925 exemption.
  assert.equal(stateIncomeTax('IL', { wages: 60000 }).tax, Math.round((60000 - 2925) * 4.95) / 100);
  // California single, $57,000 after 401(k): 1/2/4/6% brackets minus the $153 credit.
  const ca = stateIncomeTax('CA', { wages: 60000, pretax401k: 3000 });
  assert.equal(ca.taxable, 51460);
  assert.equal(ca.tax, 1469.49);
  assert.equal(ca.marginal, 6);
  // Mississippi: nothing on the first $10,000 of taxable income.
  assert.equal(stateIncomeTax('MS', { wages: 18000 }).tax, 0);
  assert.equal(stateIncomeTax('TX', { wages: 90000 }).tax, 0);
  assert.equal(stateIncomeTax('TX', { wages: 90000 }).none, true);
  // Married brackets are used for married filers.
  assert.ok(stateIncomeTax('NY', { wages: 120000, filing: 'married' }).tax < stateIncomeTax('NY', { wages: 120000 }).tax);
  assert.throws(() => stateIncomeTax('ZZ', { wages: 1 }), /Pick a state/);
});

test('special rules: PA taxes 401(k), Connecticut exemption phases out', () => {
  assert.equal(stateIncomeTax('PA', { wages: 60000, pretax401k: 3000 }).tax, 1842);
  assert.equal(stateIncomeTax('CT', { wages: 30000 }).taxable, 15000, 'full $15,000 exemption at $30,000');
  assert.equal(stateIncomeTax('CT', { wages: 35500 }).taxable, 35500 - 9000, 'drops $1,000 per $1,000 (or part) over $30,000');
  assert.equal(stateIncomeTax('CT', { wages: 60000 }).taxable, 60000, 'gone by $45,000');
});

test('take-home pay uses the state table, and custom still works', () => {
  const custom = takeHomePay({ salary: 60000, pretax401k: 3000, stateRate: 4 });
  assert.equal(custom.state, 2280);
  assert.equal(custom.stateInfo, null);
  const tx = takeHomePay({ salary: 60000, pretax401k: 3000, stateRate: 4, state: 'TX' });
  assert.equal(tx.state, 0, 'the custom rate is ignored once a state is picked');
  assert.equal(tx.takeHome, custom.takeHome + 2280);
  const ca = takeHomePay({ salary: 60000, pretax401k: 3000, state: 'CA' });
  assert.equal(ca.state, 1469.49);
  assert.ok(Math.abs(ca.effectiveState - 1469.49 / 60000) < 1e-9);
});

test('sources are cited and nothing is fetched', () => {
  const src = readFileSync(new URL('../lib/state-tax-2026.js', import.meta.url), 'utf8');
  assert.match(src, /taxfoundation\.org\/data\/all\/state\/state-income-tax-rates-2026/);
  assert.doesNotMatch(src, /fetch\(/);
});
