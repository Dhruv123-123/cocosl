import { test } from 'node:test';
import assert from 'node:assert/strict';
import { rateFor, profitFor, keepFromProfit, taxes } from '../lib/rate.js';

test('defaults: $60k take-home needs about $110 an hour', () => {
  const r = rateFor({});
  assert.equal(r.workWeeks, 46);
  assert.equal(r.billableHours, 1104);
  assert.equal(r.quote, 110);
  assert.equal(r.day, 880);
  assert.ok(Math.abs(keepFromProfit(r.profit, { health: 5400, retire: 3600, bracket: 22, stateRate: 5 }) - 60000) < 0.05);
  assert.ok(Math.abs(r.revenue * 0.9 - (r.profit + r.costsYear)) < 0.05);
});

test('profitFor inverts keepFromProfit', () => {
  const o = { health: 0, retire: 0, bracket: 12, stateRate: 0 };
  for (const want of [10000, 45000, 250000]) assert.ok(Math.abs(keepFromProfit(profitFor(want, o), o) - want) < 0.05, String(want));
});

test('self-employment tax stops growing at the Social Security wage base', () => {
  const a = taxes(300000, { bracket: 0 }).se;
  const b = taxes(400000, { bracket: 0 }).se;
  assert.equal(Math.round(b - a), Math.round(100000 * 0.9235 * 0.029));
});

test('fewer billable hours means a higher rate, and the current-rate check', () => {
  assert.ok(rateFor({ billable: 40 }).quote > rateFor({ billable: 70 }).quote);
  const r = rateFor({ current: 50 });
  assert.ok(r.current.gap < 0);
  assert.ok(rateFor({ current: 200 }).current.gap > 0);
  assert.equal(rateFor({ current: '' }).current, null);
});

test('bad input falls back to sensible values', () => {
  const r = rateFor({ takeHome: 'abc', hours: 0, billable: 500, bracket: 99 });
  assert.equal(r.input.takeHome, 60000);
  assert.equal(r.input.hours, 1);
  assert.equal(r.input.billable, 100);
  assert.equal(r.input.bracket, 22);
});
