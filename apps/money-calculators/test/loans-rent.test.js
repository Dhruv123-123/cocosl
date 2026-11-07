import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import * as S from '../lib/student-loans.js';
import { rentVsBuy, mortgagePayment } from '../lib/rent-vs-buy.js';

const by = (r) => Object.fromEntries(r.plans.map((p) => [p.key, p]));

test('RAP payment table: $120 floor, 1% per $10k band to 10%, $50 per dependent, $10 minimum', () => {
  assert.equal(S.rapBase(8000), 120);
  assert.equal(S.rapBase(10000), 120);
  assert.equal(S.rapBase(15000), 150, '1% of AGI');
  assert.equal(S.rapBase(45000), 1800, '4% of AGI');
  assert.equal(S.rapBase(100000), 9000, '9% up to $100,000');
  assert.equal(S.rapBase(150000), 15000, '10% above $100,000');
  assert.equal(S.rapMonthly(45000, 0), 150);
  assert.equal(S.rapMonthly(45000, 2), 50);
  assert.equal(S.rapMonthly(25000, 3), 10, 'never below $10');
});

test('IBR: 10% or 15% of income over 150% of the 2026 poverty guideline, capped at the 10-year payment', () => {
  assert.equal(S.povertyLine(1), 15960);
  assert.equal(S.povertyLine(4), 15960 + 3 * 5680);
  assert.equal(S.povertyLine(1, 'alaska'), 19950);
  assert.equal(S.ibrMonthly(45000, 1), 175.5);
  assert.equal(S.ibrMonthly(45000, 1, { newBorrower: false }), 263.25);
  assert.equal(S.ibrMonthly(200000, 1, { cap: 400 }), 400);
  assert.equal(S.ibrMonthly(20000, 1), 0);
});

test('Tiered Standard terms by balance', () => {
  assert.deepEqual([24999, 25000, 49999, 50000, 99999, 100000].map(S.tieredYears), [10, 15, 15, 20, 20, 25]);
});

test('older loans: standard, graduated, extended, IBR and RAP', () => {
  const r = S.comparePlans({ balance: 35000, rate: 6.5, agi: 45000, household: 1, growth: 3, cohort: 'before2026' });
  const p = by(r);
  assert.deepEqual(Object.keys(p), ['standard', 'graduated', 'extended', 'ibr', 'rap']);
  assert.equal(p.standard.first, 397.42);
  assert.equal(p.standard.months, 120);
  assert.ok(p.graduated.first < p.standard.first && p.graduated.last > p.standard.first, 'graduated starts low and rises');
  assert.ok(p.graduated.paid > p.standard.paid && p.extended.paid > p.standard.paid);
  assert.equal(p.ibr.first, 175.5);
  assert.equal(p.rap.first, 150);
  assert.equal(r.cheapest, 'standard');
  assert.equal(r.lowestPayment, 'rap');
  // No extended plan at $30,000 or less.
  assert.ok(!by(S.comparePlans({ balance: 30000, rate: 6, agi: 50000 })).extended);
});

test('new loans from July 2026: only Tiered Standard and RAP', () => {
  const r = S.comparePlans({ balance: 60000, rate: 7, agi: 30000, household: 1, cohort: 'after2026' });
  const p = by(r);
  assert.deepEqual(Object.keys(p), ['tiered', 'rap']);
  assert.equal(p.tiered.years, 20);
  // Low income: RAP's payment is under the interest, the interest is waived and the $50 match chips at principal.
  assert.equal(p.rap.first, 50);
  assert.ok(p.rap.forgiven > 0 && p.rap.forgiven < 60000, `forgiven ${p.rap.forgiven}`);
  assert.equal(p.rap.months, 360);
  assert.throws(() => S.comparePlans({ balance: 0 }), /balance/);
});

test('rent vs buy: mortgage math, winner, break-even year', () => {
  assert.equal(Math.round(mortgagePayment(320000, 6.5, 30) * 100) / 100, 2022.62);
  const short = rentVsBuy({ price: 400000, rent: 2200, years: 3 });
  assert.equal(short.winner, 'rent');
  assert.equal(short.upfront, 92000);
  assert.equal(short.firstMonth.mortgage, 2022.62);
  assert.equal(short.yearly.length, 3);
  const long = rentVsBuy({ price: 400000, rent: 2200, years: 25 });
  assert.equal(long.winner, 'buy');
  assert.equal(long.breakEven, short.breakEven, 'break-even does not depend on how long you stay');
  assert.ok(long.breakEven > 3 && long.breakEven < 25);
  assert.equal(rentVsBuy({ price: 300000, rent: 1500, downPct: 10 }).pmiLikely, true);
  assert.throws(() => rentVsBuy({ price: 0 }), /home price/);
});

test('sources cited, verify-with-servicer note, no network calls', () => {
  const src = readFileSync(new URL('../lib/student-loans.js', import.meta.url), 'utf8');
  for (const u of ['edfinancial.studentaid.gov/income-driven-repaymentinformation-center/rap', 'studentaid.gov/articles/save', 'aspe.hhs.gov']) assert.ok(src.includes(u), u);
  const text = readFileSync(new URL('../lib/text-extra.js', import.meta.url), 'utf8');
  assert.match(text, /Verify with your loan servicer/);
  for (const f of ['../lib/student-loans.js', '../lib/rent-vs-buy.js', '../lib/text-extra.js']) assert.doesNotMatch(readFileSync(new URL(f, import.meta.url), 'utf8'), /fetch\(/);
});
