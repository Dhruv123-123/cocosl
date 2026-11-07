import { test } from 'node:test';
import assert from 'node:assert/strict';
import { estimate, rateFor, normalizeTrip, mileageSummary, mileageCsv, DEDUCTIONS, deductionsFor, YEARS } from '../lib/ten99.js';

test('both tax years have four dates', () => {
  assert.deepEqual(YEARS, [2026, 2027]);
  const e = estimate({ year: 2027, profit: 60000 }, '2026-11-07');
  assert.deepEqual(e.quarters.map((q) => q.due), ['2027-04-15', '2027-06-15', '2027-09-15', '2028-01-18']);
});

test('estimate: SE tax, income tax after half SE and QBI, 90% rule vs safe harbor', () => {
  const e = estimate({ year: 2027, profit: 60000, bracket: 22 }, '2026-11-07');
  // SE: 60000 * 0.9235 = 55410 * 0.153 = 8477.73
  assert.equal(e.se, 8477.73);
  // income: (60000 - 4238.865) * 0.8 * 0.22 = 9813.96
  assert.equal(e.income, 9813.96);
  assert.equal(e.federal, 18291.69);
  assert.equal(e.ninety, 16462.52);
  assert.equal(e.method, 'ninety');
  assert.equal(e.quarters[0].even, 4115.63);
  const s = estimate({ year: 2027, profit: 60000, bracket: 22, lastYearTax: 12000 }, '2026-11-07');
  assert.equal(s.method, 'safe');
  assert.equal(s.required, 12000);
  assert.equal(estimate({ year: 2027, profit: 60000, bracket: 22, lastYearTax: 12000, highIncome: true }, '2026-11-07').required, 13200);
});

test('estimate: past quarters drop out and what is left is spread over the rest, to the cent', () => {
  const e = estimate({ year: 2026, profit: 40000, bracket: 12, paid: [1000, 1000, 0, 0] }, '2026-11-07');
  assert.deepEqual(e.quarters.map((q) => q.past), [true, true, true, false]);
  assert.equal(e.next.due, '2027-01-15');
  assert.equal(e.quarters[3].suggested, e.left);
  const f = estimate({ year: 2027, profit: 40000, bracket: 12 }, '2026-11-07');
  assert.equal(Math.round(f.quarters.reduce((t, q) => t + q.suggested, 0) * 100), Math.round(f.required * 100));
  assert.equal(estimate({ year: 2027, profit: 3000 }, '2026-11-07').owesNothing, true);
});

test('2027 uses the 2027 Social Security wage base', () => {
  const hi = estimate({ year: 2027, profit: 250000, bracket: 32 }, '2026-11-07');
  assert.equal(hi.se, Math.round((192300 * 0.124 + 250000 * 0.9235 * 0.029) * 100) / 100);
  assert.ok(estimate({ year: 2026, profit: 250000, bracket: 32 }, '2026-11-07').se < hi.se);
});

test('mileage rates by date, 2027 provisional', () => {
  assert.deepEqual(rateFor('2026-03-01'), { rate: 0.725, provisional: false });
  assert.deepEqual(rateFor('2026-07-01'), { rate: 0.76, provisional: false });
  assert.equal(rateFor('2027-02-01').provisional, true);
});

test('mileage log: validation, totals and an IRS-style CSV', () => {
  assert.equal(normalizeTrip({ date: '2026-02-30', miles: 5, purpose: 'x' }).error, 'date');
  assert.equal(normalizeTrip({ date: '2026-02-03', miles: 0, purpose: 'x' }).error, 'miles');
  assert.equal(normalizeTrip({ date: '2026-02-03', miles: 5, purpose: ' ' }).error, 'purpose');
  const trips = [
    normalizeTrip({ id: 'a', date: '2026-06-30', miles: 10, purpose: 'Client meeting, Acme', from: 'Home', to: 'Acme HQ' }),
    normalizeTrip({ id: 'b', date: '2026-07-01', miles: 20.25, purpose: 'Deliveries' }),
    normalizeTrip({ id: 'c', date: '2027-01-05', miles: 5, purpose: 'Bank' }),
  ];
  const s = mileageSummary(trips, 2026);
  assert.equal(s.rows.length, 2);
  assert.equal(s.miles, 30.3);
  assert.equal(s.deduction, 7.25 + 15.43);
  assert.equal(s.provisional, false);
  assert.equal(mileageSummary(trips, 2027).provisional, true);
  const csv = mileageCsv(s);
  assert.match(csv, /^Date,Business purpose,From,To,Miles,IRS rate,Deduction\r\n2026-06-30,"Client meeting, Acme",Home,Acme HQ,10,0.725,7.25\r\n/);
  assert.match(csv, /\r\nTotal,,,,30.3,,22.68\r\n$/);
});

test('deduction checklist filters by kind of work', () => {
  assert.equal(new Set(DEDUCTIONS.map((d) => d.id)).size, DEDUCTIONS.length);
  assert.ok(deductionsFor('drivers').some((d) => d.id === 'mileage'));
  assert.ok(!deductionsFor('sellers').some((d) => d.id === 'mileage'));
  assert.equal(deductionsFor('all').length, DEDUCTIONS.length);
});
