import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { q4Plan, Q4_DUE, FILE_BY } from '../lib/q4.js';
import { quarterlyPlan } from '../lib/tax.js';

const near = (a, b, tol = 1) => assert.ok(Math.abs(a - b) <= tol, `${a} not within ${tol} of ${b}`);

test('dates: Jan 15, 2027 payment, Feb 1, 2027 file-early option', () => {
  assert.equal(Q4_DUE.toISOString().slice(0, 10), '2027-01-15');
  assert.equal(FILE_BY.toISOString().slice(0, 10), '2027-02-01');
});

test('on track: safe harbor of $6,500 with three payments made leaves one quarter', () => {
  const p = q4Plan({ profit: 60000, priorYearTax: 6500, priorYearAgi: 52000, paidSoFar: 4875 });
  near(p.jan15, 1625);
  near(p.q4Share, 1625);
  assert.equal(p.behind, 0);
  near(p.fileEarlyInstead, 12037 - 4875, 2);
});

test('nothing paid yet: Jan 15 covers the whole year, most of it catch-up', () => {
  const p = q4Plan({ profit: 60000 });
  near(p.jan15, 0.9 * 12037, 2);
  near(p.behind, 0.75 * 0.9 * 12037, 2);
  near(p.q4Share, 0.25 * 0.9 * 12037, 2);
  near(p.afterJan15, 0.1 * 12037, 2);
});

test('agrees with the main calculator at Q4, and handles withholding and zero', () => {
  const v = { profit: 40000, w2Wages: 50000, withholding: 4000, paidSoFar: 1000 };
  assert.equal(q4Plan(v).jan15, quarterlyPlan({ ...v, nextQuarter: 4 }).thisPayment);
  assert.equal(q4Plan({}).jan15, 0);
  assert.equal(q4Plan({ profit: 20000, paidSoFar: 99999 }).jan15, 0);
});

test('Q4 page: no outside links, FAQ schema, the Feb 1 option and the tax-year warning', () => {
  const html = readFileSync(new URL('../q4/index.html', import.meta.url), 'utf8');
  for (const s of ['January 15, 2027', 'February 1, 2027', 'tax year 2026', '"@type":"FAQPage"', 'Sept', '1040-ES']) assert.ok(html.includes(s), s);
  assert.ok(!/<a [^>]*href="https?:/.test(html));
});
