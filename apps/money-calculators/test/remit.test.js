import { test } from 'node:test';
import assert from 'node:assert/strict';
import { remittanceCost } from '../lib/remit.js';

test('fee on top plus a 2% markup: $300 at 18.50 market', () => {
  const r = remittanceCost({ amount: 300, fee: 5, midRate: 18.5, markupPct: 2, perYear: 12 });
  assert.equal(r.paid, 305);
  assert.equal(r.markupCost, 6);
  assert.equal(r.totalCost, 11);
  assert.equal(r.effRate, 18.13);
  assert.equal(r.arrives, 5439);
  assert.equal(r.ideal, 5642.5);
  assert.equal(r.lost, 203.5);
  assert.equal(r.yearCost, 132);
  assert.equal(r.overTarget, true);
  assert.equal(r.tax, 0);
});

test('a quoted rate overrides the typed markup', () => {
  const r = remittanceCost({ amount: 200, fee: 0, midRate: 20, quotedRate: 19.5, markupPct: 10 });
  assert.equal(r.rateFrom, 'quoted');
  assert.equal(r.markupPct, 2.5);
  assert.equal(r.markupCost, 5);
  assert.equal(r.arrives, 3900);
  assert.equal(r.overTarget, false);
});

test('fee taken from the amount and paid in cash adds the 1% tax', () => {
  const r = remittanceCost({ amount: 500, fee: 10, midRate: 17, markupPct: 0, feeMode: 'inside', pay: 'cash' });
  assert.equal(r.converted, 490);
  assert.equal(r.tax, 5);
  assert.equal(r.paid, 505);
  assert.equal(r.totalCost, 15);
  assert.equal(r.arrives, 8330);
});

test('no market rate: shows what arrives in dollars', () => {
  const r = remittanceCost({ amount: 100, fee: 3, markupPct: 3 });
  assert.equal(r.arrives, null);
  assert.equal(r.arrivesUsd, 97);
  assert.equal(r.lost, null);
});

test('percentage fee and errors in the caller language', () => {
  assert.equal(remittanceCost({ amount: 1000, fee: 0, feePct: 1.5 }).fees, 15);
  assert.throws(() => remittanceCost({ amount: 0 }, { amount: 'Escribe la cantidad.' }), /Escribe la cantidad/);
  assert.throws(() => remittanceCost({ amount: 100, markupPct: 80 }), /markup/);
  assert.throws(() => remittanceCost({ amount: 100, perYear: 60 }), /52/);
});
