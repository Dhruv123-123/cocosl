import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import * as A from '../lib/afford.js';

const today = '2026-11-07';
const byKey = (r) => Object.fromEntries(r.options.map((o) => [o.key, o]));

test('loan payment math', () => {
  assert.equal(Math.round(A.loanPayment(20000, 6, 60) * 100) / 100, 386.66);
  assert.equal(A.loanPayment(1200, 0, 12), 100);
  assert.equal(A.loanPayment(0, 7, 60), 0);
});

test('car: all-in price, three options, and the warnings', () => {
  const r = A.compare({ kind: 'car', savings: 8000, keepSaved: 3000, takeHome: 4500, bills: 3000 }, today);
  assert.equal(r.upfront, 30560, '28,000 + 7% tax + 600 fees');
  assert.equal(r.financed, 27560);
  assert.equal(r.leftover, 1500);
  const o = byKey(r);
  assert.equal(o.cash.verdict, 'no');
  assert.equal(o.loan.payment, Math.round(A.loanPayment(27560, 7.5, 60) * 100) / 100);
  assert.equal(o.loan.monthly, Math.round((o.loan.payment + 250) * 100) / 100, 'running costs count');
  assert.ok(Math.abs(o.loan.total - (3000 + o.loan.payment * 60)) < 0.5, 'down payment plus 60 payments');
  assert.ok(o.loan.interest > 5000 && o.loan.interest < 6000);
  assert.equal(o.loan.verdict, 'tight');
  const why = o.loan.reasons.join(' ');
  assert.match(why, /4 years or less/);
  assert.match(why, /less than 20% down/);
  assert.match(why, /18% of your take-home/);
  assert.equal(r.best, null);
  assert.equal(r.saveMonths, Math.ceil((30560 - 5000) / 1500));
  assert.match(r.tips.join(' '), /credit union/);
});

test('trade-in lowers the taxed price', () => {
  const r = A.compare({ kind: 'car', price: 20000, tradeIn: 5000, salesTax: 10, fees: 0 }, today);
  assert.equal(r.upfront, 16500);
});

test('phone: 0% installment beats paying cash out of a thin cushion', () => {
  const r = A.compare({ kind: 'phone', savings: 2000, keepSaved: 1000, takeHome: 3000, bills: 2500 }, today);
  const o = byKey(r);
  assert.equal(o.cash.verdict, 'tight');
  assert.equal(o.loan.verdict, 'yes');
  assert.equal(o.loan.interest, 0);
  assert.equal(r.best, 'loan');
  assert.match(o.bnpl.reasons.join(' '), /declined or split/);
  const paid = A.compare({ kind: 'phone', loanApr: 24 }, today);
  assert.match(byKey(paid).loan.reasons.join(' '), /0% installment/);
});

test('cash wins when it fits, and BNPL monthly plans show interest', () => {
  const r = A.compare({ kind: 'other', price: 1000, salesTax: 0, savings: 10000, keepSaved: 2000, takeHome: 5000, bills: 3000, bnplType: 'monthly', bnplApr: 30, bnplMonths: 12 }, today);
  const o = byKey(r);
  assert.equal(r.best, 'cash');
  assert.ok(o.bnpl.interest > 150, `interest ${o.bnpl.interest}`);
  assert.match(o.bnpl.reasons.join(' '), /adds \$\d+\.\d\d in interest/);
  assert.equal(o.bnpl.total, Math.round((1000 + o.bnpl.interest) * 100) / 100);
});

test('bad input falls back to presets', () => {
  const v = A.normalize({ kind: 'boat', price: 'abc', loanMonths: '500' });
  assert.equal(v.kind, 'car');
  assert.equal(v.price, A.PRESETS.car.price);
  assert.equal(v.loanMonths, 96);
});

test('page: private, offline, Budget Pro slot, paycheck link', () => {
  const html = readFileSync(new URL('../afford.html', import.meta.url), 'utf8');
  assert.match(html, /Nothing you type leaves this browser/);
  assert.match(html, /href="pricing\.html\?from=afford" data-upgrade="afford"/);
  assert.match(html, /money-calculators\/take-home-pay\//);
  assert.doesNotMatch(readFileSync(new URL('../afford.js', import.meta.url), 'utf8'), /fetch\(/);
  assert.match(readFileSync(new URL('../sw.js', import.meta.url), 'utf8'), /'afford\.html', 'afford\.js', 'lib\/afford\.js'/);
});
