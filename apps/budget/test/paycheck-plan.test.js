import { test } from 'node:test';
import assert from 'node:assert/strict';
import { monthlyIncome, split503020, zeroBased, planCsv, parsePlanCsv, PLAN_KEYS, bucketOf } from '../lib/paycheck-plan.js';
import { CAT } from '../lib/dashboard.js';

test('every two weeks: plan on two checks, the two extra checks are left over', () => {
  const m = monthlyIncome({ pay: 1600, freq: 'biweekly' });
  assert.equal(m.monthly, 3200);
  assert.equal(m.average, 3466.67);
  assert.equal(m.extraChecks, 2);
  assert.equal(m.extra, 3200);
  assert.equal(monthlyIncome({ pay: 1600, freq: 'biweekly', planOn: 'average' }).monthly, 3466.67);
  assert.equal(monthlyIncome({ pay: 2000, freq: 'semimonthly' }).monthly, 4000);
  assert.equal(monthlyIncome({ pay: 500, freq: 'weekly' }).extra, 2000);
  assert.throws(() => monthlyIncome({ pay: 0 }, 'Escribe tu pago.'), /Escribe/);
});

test('50/30/20 adds up exactly, in whole dollars', () => {
  const s = split503020(3467);
  assert.deepEqual(s.buckets, { needs: 1734, wants: 1040, savings: 693 });
  const total = Object.values(s.amounts).reduce((a, b) => a + b, 0);
  assert.equal(total, 3467);
  for (const b of ['needs', 'wants', 'savings']) {
    assert.equal(Object.entries(s.amounts).filter(([k]) => bucketOf(k) === b).reduce((t, [, v]) => t + v, 0), s.buckets[b]);
  }
  assert.equal(s.amounts.savings, 693);
});

test('zero-based: what is left, over budget, and the bucket shares', () => {
  const z = zeroBased(3000, { housing: 1500, groceries: '400', dining: 300, savings: 600 });
  assert.equal(z.planned, 2800);
  assert.equal(z.left, 200);
  assert.equal(z.balanced, false);
  assert.deepEqual(z.pct, { needs: 63, wants: 10, savings: 20 });
  assert.equal(zeroBased(3000, { housing: 3000 }).balanced, true);
  assert.equal(zeroBased(3000, { housing: 3100 }).over, true);
  assert.deepEqual(zeroBased(1000, { housing: -5, nope: 50 }).amounts, {});
});

test('plan keys are real dashboard categories', () => {
  for (const k of PLAN_KEYS) assert.ok(CAT[k], k);
});

test('the plan CSV round-trips in both languages and is not mistaken for a bank file', () => {
  const amounts = { housing: 1500, dining: 250, savings: 600 };
  for (const lang of ['en', 'es']) {
    const csv = planCsv(amounts, lang);
    assert.deepEqual(parsePlanCsv(csv), amounts);
  }
  assert.match(planCsv(amounts, 'en'), /^Category,Monthly budget\r\nRent & housing,1500\r\n/);
  assert.equal(parsePlanCsv('Date,Description,Amount\n2026-10-01,RENT,-1500'), null);
  assert.deepEqual(parsePlanCsv('"Categoría","Presupuesto mensual"\n"Supermercado","$450"'), { groceries: 450 });
});
