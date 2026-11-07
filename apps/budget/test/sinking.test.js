import { test } from 'node:test';
import assert from 'node:assert/strict';
import { datedifMonths, monthsAhead, presetDate, normalizeFund, fundPlan, plan, fundsTsv, depositsTsv, plannerCsv } from '../lib/sinking.js';

test('DATEDIF months, like the spreadsheet', () => {
  assert.equal(datedifMonths('2026-11-07', '2027-05-07'), 6);
  assert.equal(datedifMonths('2026-11-07', '2027-05-06'), 5);
  assert.equal(datedifMonths('2026-01-31', '2026-02-28'), 0);
  assert.equal(datedifMonths('2026-11-07', '2026-11-30'), 0);
});

test('months left and save each month match the Pro sheet formulas', () => {
  const f = normalizeFund({ name: 'Car insurance', target: 900, due: '2027-05-07', saved: 150 });
  const p = fundPlan(f, '2026-11-07');
  assert.equal(p.monthsLeft, 7); // DATEDIF 6 + 1
  assert.equal(p.still, 750);
  assert.equal(p.monthly, 107.14);
  const past = fundPlan(normalizeFund({ name: 'Late', target: 300, due: '2026-11-01', saved: 100 }), '2026-11-07');
  assert.equal(past.monthsLeft, 0);
  assert.equal(past.monthly, 200);
  assert.equal(past.late, true);
  assert.equal(fundPlan(normalizeFund({ name: 'Done', target: 100, due: '2027-01-01', saved: 120 }), '2026-11-07').monthly, 0);
});

test('plan totals, per paycheck and order by date', () => {
  const funds = [
    normalizeFund({ name: 'Holidays', target: 800, due: '2026-12-01' }),
    normalizeFund({ name: 'Tires', target: 600, due: '2027-11-07' }),
  ];
  const p = plan(funds, '2026-11-07', { perPay: 2 });
  assert.equal(p.rows[0].name, 'Holidays');
  assert.equal(p.rows[0].monthly, 800); // DATEDIF 0 + 1 = 1 month
  assert.equal(p.rows[1].monthly, 46.15); // 12 + 1 = 13 months
  assert.equal(p.monthly, 846.15);
  assert.equal(p.perPaycheck, 423.08);
  assert.equal(p.next.name, 'Holidays');
});

test('validation', () => {
  assert.equal(normalizeFund({ target: 5, due: '2027-01-01' }).error, 'name');
  assert.equal(normalizeFund({ name: 'x', target: 0, due: '2027-01-01' }).error, 'target');
  assert.equal(normalizeFund({ name: 'x', target: 5, due: '2027-02-30' }).error, 'due');
});

test('preset dates', () => {
  assert.equal(monthsAhead('2026-11-07', 6), '2027-05-01');
  assert.equal(presetDate('Holidays and gifts', 0, '2026-11-07'), '2026-12-01');
  assert.equal(presetDate('Holidays and gifts', 0, '2026-12-15'), '2027-12-01');
  assert.equal(presetDate('Regreso a clases', 0, '2026-11-07'), '2027-08-01');
});

test('exports paste into the Pro sheet columns', () => {
  const funds = [normalizeFund({ name: 'Car insurance', target: 900, due: '2027-05-07', saved: 150 }), normalizeFund({ name: 'Trip', target: 1500, due: '2027-08-01' })];
  assert.equal(fundsTsv(funds), 'Car insurance\t900\t2027-05-07\nTrip\t1500\t2027-08-01');
  assert.equal(depositsTsv(funds, '2026-11-07'), '2026-11-07\tCar insurance\t150');
  assert.match(plannerCsv(plan(funds, '2026-11-07'), 'es'), /^Fondo,Meta,Para cuándo/);
});
