import test from 'node:test';
import assert from 'node:assert/strict';
import { ratePlan } from '../lib/rate.js';
import { federalTax } from '../lib/tax.js';

test("matches the paid kit's worked example: $55K take-home is $75/hour", () => {
  const p = ratePlan({ takeHome: 55000, health: 6000, retirement: 5000, costs: 6000, weeks: 48, hoursPerWeek: 25 });
  assert.equal(p.profit, 84000);
  assert.equal(p.revenue, 90000);
  assert.equal(p.hours, 1200);
  assert.equal(p.hourly, 75);
  assert.equal(p.day, 450);
  assert.ok(p.leftAfterTax >= p.afterTax && p.leftAfterTax - p.afterTax < 1000);
});

test('profit is the smallest $1,000 step that covers the target after tax', () => {
  const p = ratePlan({ takeHome: 40000 });
  const left = (x) => x - federalTax({ profit: x }).total;
  assert.ok(left(p.profit) >= 40000 && left(p.profit - 1000) < 40000);
});

test('state tax and fewer billable hours raise the rate', () => {
  const base = ratePlan({ takeHome: 60000 });
  assert.ok(ratePlan({ takeHome: 60000, stateRate: 0.05 }).hourly > base.hourly);
  assert.ok(ratePlan({ takeHome: 60000, hoursPerWeek: 20 }).hourly > base.hourly);
  assert.ok(ratePlan({ takeHome: 60000, status: 'mfj' }).hourly < base.hourly);
});

test('edge cases: zero hours, zero target, bad input, very high targets', () => {
  assert.equal(ratePlan({ takeHome: 50000, hoursPerWeek: 0 }).hourly, 0);
  assert.equal(ratePlan({}).profit, 0);
  assert.equal(ratePlan({ takeHome: 'abc', costs: -5 }).revenue, 0);
  assert.equal(ratePlan({ takeHome: 900000 }).tooHigh, true);
  assert.equal(ratePlan({ takeHome: 55000 }).tooHigh, false);
});
