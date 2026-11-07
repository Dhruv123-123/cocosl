import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import * as S from '../lib/sidehustle.js';

test('self-employment tax: 15.3% on 92.35%, $400 floor, Social Security capped at the wage base', () => {
  assert.equal(S.seTax(10000), Math.round(10000 * 0.9235 * 0.153 * 100) / 100);
  assert.equal(S.seTax(400), 0, 'under $400 of net earnings');
  assert.equal(S.seTax(-50), 0);
  const big = S.seTax(300000);
  assert.equal(big, Math.round((184500 * 0.124 + 300000 * 0.9235 * 0.029) * 100) / 100);
});

test('driver: real car cost vs IRS mileage deduction, hourly before and after tax', () => {
  const r = S.profit({ kind: 'driver', gross: 600, hours: 25, miles: 400, carCost: 0.5, other: 15, weeks: 48, bracket: 12 });
  assert.equal(r.fees, 0);
  assert.equal(r.car, 200);
  assert.equal(r.mileageDeduction, 304, '400 miles at 76 cents');
  assert.equal(r.cashProfit, 385);
  assert.equal(r.year.taxable, (600 - 15 - 304) * 48);
  assert.equal(r.year.se, S.seTax(281 * 48));
  assert.equal(r.year.incomeTax, Math.round((281 * 48 - r.year.se / 2) * 0.8 * 0.12 * 100) / 100);
  assert.equal(r.hourly, 15.4);
  assert.equal(r.hourlyAfterTax, Math.round(((385 - r.taxWeek) / 25) * 100) / 100);
  assert.match(r.tips.join(' '), /\$304\.00 tax deduction/);
});

test('Etsy fees: 6.5% + 3% of sales, $0.25 an order, $0.20 a listing', () => {
  const r = S.profit({ kind: 'etsy', gross: 500, orders: 15, listings: 10, goods: 120, shipping: 70, other: 10, miles: 0, hours: 15 });
  assert.equal(r.fees, Math.round((500 * 0.095 + 15 * 0.25 + 10 * 0.2) * 100) / 100);
  assert.equal(r.costs, 200);
  assert.equal(r.cashProfit, Math.round((500 - r.fees - 200) * 100) / 100);
});

test('low pay is called out, bad input falls back to presets', () => {
  const r = S.profit({ kind: 'driver', gross: 200, hours: 30, miles: 500 });
  assert.ok(r.hourlyAfterTax < 7.25);
  assert.match(r.tips.join(' '), /federal minimum wage/);
  assert.match(r.tips.join(' '), /Long miles per hour/);
  const v = S.normalize({ kind: 'boat', gross: 'abc', bracket: '13', weeks: '99' });
  assert.equal(v.kind, 'driver');
  assert.equal(v.gross, S.KINDS.driver.gross);
  assert.equal(v.bracket, 12);
  assert.equal(v.weeks, 52);
  assert.equal(S.normalize({ bracket: '0' }).bracket, 0);
  assert.equal(S.profit({ kind: 'other', gross: 100, hours: 0 }).hourly, null);
});

test('page: sources, private, offline', () => {
  const src = readFileSync(new URL('../lib/sidehustle.js', import.meta.url), 'utf8');
  for (const u of ['irs.gov/newsroom/irs-sets-2026-business-standard-mileage-rate', 'ssa.gov/oact/cola/cbb', 'etsy.com/legal/fees']) assert.ok(src.includes(u), u);
  assert.doesNotMatch(readFileSync(new URL('../side-hustle.js', import.meta.url), 'utf8'), /fetch\(/);
  assert.match(readFileSync(new URL('../side-hustle.html', import.meta.url), 'utf8'), /Nothing you type leaves this browser/);
});
