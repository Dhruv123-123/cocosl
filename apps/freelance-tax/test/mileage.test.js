import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { mileagePlan, mileageDeduction, MILEAGE_RATE, RATE_JAN_JUN, RATE_JUL_DEC } from '../lib/mileage.js';
import { federalTax } from '../lib/tax.js';

const near = (a, b, tol = 1) => assert.ok(Math.abs(a - b) <= tol, `${a} not within ${tol} of ${b}`);

test('2026 has two rates: 72.5 cents to June 30, 76 cents from July 1 (Announcement 2026-11)', () => {
  assert.equal(RATE_JAN_JUN, 0.725);
  assert.equal(RATE_JUL_DEC, 0.76);
  assert.equal(MILEAGE_RATE, 0.76);
  near(mileageDeduction(10000, 0), 7250, 0.01);
  near(mileageDeduction(10000, 10000), 7600, 0.01);
  near(mileageDeduction(10000), 7425, 0.01); // no split given: half assumed from July
  near(mileageDeduction(10000, 99999), 7600, 0.01); // the July miles can't exceed the total
});

test('the worked example used on the page and in the driver Shorts', () => {
  const p = mileagePlan({ earnings: 30000, miles: 15000, deliveries: 3000 });
  near(p.deduction, 11137.5, 0.01); // 7,500 miles at 72.5¢ + 7,500 at 76¢
  near(p.profit, 18862.5, 0.01);
  near(p.taxNoMiles, 5181, 1); // same as the $30K profit figure used across the brand
  near(p.tax, federalTax({ profit: 18862.5 }).total, 0.01);
  assert.ok(p.saving > 2300 && p.saving < 2500, String(p.saving));
  assert.ok(p.perDelivery > 0.85 && p.perDelivery < 1, String(p.perDelivery));
  assert.ok(p.owesEstimates);
});

test('the FAQ example: $30K payouts, 15,000 miles', () => {
  const p = mileagePlan({ earnings: 30000, miles: 15000, deliveries: 3000 });
  near(p.tax, 2780, 10);
  near(p.taxNoMiles, 5180, 10);
  near(p.setAsideRate, 0.093, 0.001);
  near(p.perDelivery, 0.93, 0.01);
  const html = readFileSync(new URL('../mileage/index.html', import.meta.url), 'utf8');
  for (const s of ['$2,780', '9.3%', '93¢', '$5,180', '$11,138', 'milesFromJuly']) assert.ok(html.includes(s), s);
});

test('no miles means no saving; miles never push profit below zero', () => {
  assert.equal(mileagePlan({ earnings: 20000 }).saving, 0);
  const p = mileagePlan({ earnings: 5000, miles: 20000 });
  assert.equal(p.profit, 0);
  assert.equal(p.tax, 0);
  assert.equal(mileagePlan({ earnings: -5, miles: 'x' }).tax, 0);
});

test('the saving is always less than the deduction, and an own log beats the app figure', () => {
  for (const earnings of [15000, 40000, 80000]) {
    const p = mileagePlan({ earnings, miles: 12000, appMiles: 7000 });
    assert.ok(p.saving < p.deduction);
    assert.ok(p.appSaving > 0 && p.appSaving < p.saving);
    assert.ok(p.per100 > 0 && p.per100 < 100 * RATE_JUL_DEC);
  }
  assert.equal(mileagePlan({ earnings: 30000, miles: 9000 }).appSaving, null);
});

test('a W-2 job raises the rate on driving income; state tax adds to the set-aside', () => {
  const solo = mileagePlan({ earnings: 30000, miles: 10000 });
  assert.ok(mileagePlan({ earnings: 30000, miles: 10000, w2Wages: 60000 }).tax > solo.tax);
  assert.ok(mileagePlan({ earnings: 30000, miles: 10000, stateRate: 0.05 }).tax > solo.tax);
});

test('page states the rate, the commuting rule, and links to irs.gov guidance by name', () => {
  const html = readFileSync(new URL('../mileage/index.html', import.meta.url), 'utf8');
  for (const s of ['72.5', '76¢', 'Announcement 2026-11', 'Commuting', 'Publication 463', '"@type":"FAQPage"', 'aria-current="page"']) assert.ok(html.includes(s), s);
  assert.ok(!/<a [^>]*href="https?:/.test(html), 'no outside links on the mileage page');
});
