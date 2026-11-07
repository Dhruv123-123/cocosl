import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  compoundGrowth, debtPayoff, compareDebtStrategies, emergencyFund,
  savingsInterest, minimumPaymentTrap, rothVsTraditional,
} from '../lib/calc.js';

const close = (a, b, tol = 0.02) => assert.ok(Math.abs(a - b) <= tol, `${a} not within ${tol} of ${b}`);

test('compound growth at 0% is just contributions', () => {
  const r = compoundGrowth({ initial: 1000, monthly: 100, annualRate: 0, years: 10 });
  assert.equal(r.finalBalance, 13000);
  assert.equal(r.totalGrowth, 0);
  assert.equal(r.rows.length, 10);
});

test('compound growth matches the closed-form annuity formula', () => {
  const r = compoundGrowth({ initial: 0, monthly: 200, annualRate: 6, years: 30 });
  const i = 0.06 / 12;
  const n = 360;
  close(r.finalBalance, 200 * ((Math.pow(1 + i, n) - 1) / i), 0.05);
});

test('compound growth rejects nonsense input', () => {
  assert.throws(() => compoundGrowth({ initial: -5, years: 10 }), RangeError);
  assert.throws(() => compoundGrowth({ initial: 'abc', years: 10 }), RangeError);
});

const debts = [
  { name: 'Card A', balance: 3000, apr: 24.99, minPayment: 90 },
  { name: 'Car', balance: 8000, apr: 6.5, minPayment: 220 },
  { name: 'Store card', balance: 600, apr: 29.99, minPayment: 30 },
];

test('avalanche targets highest APR first, snowball smallest balance first', () => {
  const a = debtPayoff(debts, { extra: 200, strategy: 'avalanche' });
  const s = debtPayoff(debts, { extra: 200, strategy: 'snowball' });
  assert.deepEqual(a.order, ['Store card', 'Card A', 'Car']);
  assert.deepEqual(s.order, ['Store card', 'Card A', 'Car']);
  assert.ok(a.feasible && s.feasible);
});

test('avalanche never costs more interest than snowball', () => {
  const mixed = [
    { name: 'Big high APR', balance: 9000, apr: 27, minPayment: 200 },
    { name: 'Small low APR', balance: 500, apr: 4, minPayment: 25 },
  ];
  const c = compareDebtStrategies(mixed, 150);
  assert.ok(c.avalanche.totalInterest <= c.snowball.totalInterest);
  assert.ok(c.interestSaved >= 0);
  assert.deepEqual(c.snowball.order, ['Small low APR', 'Big high APR']);
});

test('a single debt payoff matches the amortization count', () => {
  const r = debtPayoff([{ name: 'Loan', balance: 1000, apr: 12, minPayment: 100 }]);
  assert.equal(r.months, 11); // 1000 at 1%/mo with $100 payments takes 10.6 months
  assert.ok(r.totalInterest > 50 && r.totalInterest < 60);
});

test('debt that grows faster than the payment is flagged infeasible', () => {
  const r = debtPayoff([{ name: 'Bad', balance: 10000, apr: 30, minPayment: 100 }]);
  assert.equal(r.feasible, false);
});

test('emergency fund months', () => {
  const r = emergencyFund({ monthlyExpenses: 2000, monthsTarget: 3, currentSaved: 1000, monthlySave: 500 });
  assert.equal(r.target, 6000);
  assert.equal(r.gap, 5000);
  assert.equal(r.months, 10);
  assert.equal(emergencyFund({ monthlyExpenses: 2000, monthsTarget: 3, currentSaved: 7000 }).months, 0);
  assert.equal(emergencyFund({ monthlyExpenses: 2000, monthsTarget: 3 }).reachable, false);
});

test('high-yield savings beats a 0.01% account', () => {
  const r = savingsInterest({ balance: 10000, apy: 4, months: 12 });
  close(r.interest, 400, 0.5);
  assert.ok(r.difference > 395);
});

test('minimum payment trap costs far more than a fixed payment', () => {
  const r = minimumPaymentTrap({ balance: 5000, apr: 22, fixedPayment: 250 });
  assert.ok(r.minimumOnly.months > 100);
  assert.ok(r.fixed.months < 30);
  assert.ok(r.interestSaved > 3000);
});

test('fixed payment below the monthly interest never pays off', () => {
  const r = minimumPaymentTrap({ balance: 10000, apr: 24, fixedPayment: 150 });
  assert.equal(r.fixed.months, Infinity);
  assert.equal(r.interestSaved, undefined);
});

test('Roth vs Traditional: equal tax rates tie, lower rate later favors Traditional', () => {
  const tie = rothVsTraditional({ annualContribution: 6000, currentRate: 22, retirementRate: 22, years: 30 });
  assert.equal(tie.winner, 'tie');
  const trad = rothVsTraditional({ annualContribution: 6000, currentRate: 32, retirementRate: 12, years: 30 });
  assert.equal(trad.winner, 'traditional');
  const roth = rothVsTraditional({ annualContribution: 6000, currentRate: 12, retirementRate: 24, years: 30 });
  assert.equal(roth.winner, 'roth');
});

test('payoff schedule: payments add up and balances reach zero', () => {
  const r = debtPayoff(debts, { extra: 200, strategy: 'avalanche', schedule: true });
  assert.equal(r.schedule.length, r.months);
  assert.deepEqual(r.names, ['Card A', 'Car', 'Store card']);
  for (const row of r.schedule.slice(0, -1)) close(row.payments.reduce((a, b) => a + b, 0), r.budget, 0.05);
  assert.deepEqual(r.schedule.at(-1).balances, [0, 0, 0]);
  const totalPaid = r.schedule.reduce((s, row) => s + row.payments.reduce((a, b) => a + b, 0), 0);
  close(totalPaid, 3000 + 8000 + 600 + r.totalInterest, 0.5);
  assert.equal(debtPayoff(debts).schedule, undefined);
});
