// Pure calculator math for the Money Made Simple calculator suite.
// No DOM access here, so every function runs in the browser and under `node --test`.

const MAX_MONTHS = 1200; // 100 years: anything longer is treated as "never pays off"

const round2 = (n) => Math.round((n + Number.EPSILON) * 100) / 100;

function num(value, name, { min = 0, max = Infinity } = {}) {
  const n = Number(value);
  if (!Number.isFinite(n)) throw new RangeError(`${name} must be a number`);
  if (n < min || n > max) throw new RangeError(`${name} must be between ${min} and ${max}`);
  return n;
}

/**
 * Growth of an investment with a starting balance and a monthly contribution,
 * compounded monthly. Returns a year-by-year table.
 */
export function compoundGrowth({ initial = 0, monthly = 0, annualRate = 7, years = 30 }) {
  initial = num(initial, 'Starting amount');
  monthly = num(monthly, 'Monthly contribution');
  annualRate = num(annualRate, 'Annual return', { min: -50, max: 50 });
  years = Math.round(num(years, 'Years', { min: 1, max: 80 }));
  const r = annualRate / 100 / 12;
  let balance = initial;
  let contributed = initial;
  const rows = [];
  for (let y = 1; y <= years; y++) {
    for (let m = 0; m < 12; m++) {
      balance = balance * (1 + r) + monthly;
      contributed += monthly;
    }
    rows.push({ year: y, balance: round2(balance), contributed: round2(contributed), growth: round2(balance - contributed) });
  }
  return {
    finalBalance: round2(balance),
    totalContributed: round2(contributed),
    totalGrowth: round2(balance - contributed),
    rows,
  };
}

function cloneDebts(debts) {
  if (!Array.isArray(debts) || debts.length === 0) throw new RangeError('Add at least one debt');
  return debts.map((d, i) => ({
    name: String(d.name || `Debt ${i + 1}`),
    balance: num(d.balance, `${d.name || 'Debt'} balance`),
    apr: num(d.apr, `${d.name || 'Debt'} APR`, { max: 100 }),
    minPayment: num(d.minPayment, `${d.name || 'Debt'} minimum payment`),
    index: i,
  }));
}

/**
 * Simulate paying off several debts with a fixed total monthly budget
 * (sum of minimums + extra). Freed-up minimums roll into the target debt.
 * strategy: 'avalanche' (highest APR first) or 'snowball' (smallest balance first).
 */
export function debtPayoff(debts, { extra = 0, strategy = 'avalanche', schedule = false } = {}) {
  const list = cloneDebts(debts);
  extra = num(extra, 'Extra payment');
  if (!['avalanche', 'snowball'].includes(strategy)) throw new RangeError('Unknown strategy');
  const budget = list.reduce((s, d) => s + d.minPayment, 0) + extra;

  const order = [...list].sort((a, b) =>
    strategy === 'avalanche' ? b.apr - a.apr || a.balance - b.balance : a.balance - b.balance || b.apr - a.apr,
  );

  let month = 0;
  let totalInterest = 0;
  const paidOffMonth = {};
  const rows = [];
  while (list.some((d) => d.balance > 0.005)) {
    month++;
    if (month > MAX_MONTHS) {
      return { feasible: false, strategy, months: Infinity, totalInterest: Infinity, budget: round2(budget), order: order.map((d) => d.name), paidOff: [] };
    }
    // 1. Interest accrues.
    for (const d of list) {
      if (d.balance <= 0) continue;
      const interest = d.balance * (d.apr / 100 / 12);
      d.balance += interest;
      totalInterest += interest;
    }
    // 2. Pay minimums on every open debt.
    let available = budget;
    const paid = list.map(() => 0);
    for (const d of list) {
      if (d.balance <= 0) continue;
      const pay = Math.min(d.minPayment, d.balance, available);
      d.balance -= pay;
      paid[d.index] += pay;
      available -= pay;
    }
    // 3. Everything left goes to the target debts in strategy order.
    for (const d of order) {
      if (available <= 0) break;
      const live = list[d.index];
      if (live.balance <= 0) continue;
      const pay = Math.min(live.balance, available);
      live.balance -= pay;
      paid[live.index] += pay;
      available -= pay;
    }
    if (schedule) rows.push({ month, payments: paid.map(round2), balances: list.map((d) => round2(Math.max(0, d.balance))) });
    for (const d of list) {
      if (d.balance <= 0.005 && paidOffMonth[d.name] === undefined) {
        d.balance = 0;
        paidOffMonth[d.name] = month;
      }
    }
  }
  return {
    feasible: true,
    strategy,
    months: month,
    totalInterest: round2(totalInterest),
    budget: round2(budget),
    order: order.map((d) => d.name),
    paidOff: order.map((d) => ({ name: d.name, month: paidOffMonth[d.name] })),
    ...(schedule ? { names: list.map((d) => d.name), schedule: rows } : {}),
  };
}

/** Run both strategies and say which saves more and by how much. */
export function compareDebtStrategies(debts, extra = 0) {
  const avalanche = debtPayoff(debts, { extra, strategy: 'avalanche' });
  const snowball = debtPayoff(debts, { extra, strategy: 'snowball' });
  const interestSaved = avalanche.feasible && snowball.feasible ? round2(snowball.totalInterest - avalanche.totalInterest) : null;
  return { avalanche, snowball, interestSaved, monthsSaved: avalanche.feasible && snowball.feasible ? snowball.months - avalanche.months : null };
}

/**
 * Months of essential costs to keep, by how steady the household's income is. Common guidance is
 * 3 to 6 months; we go higher for income that can stop suddenly or take long to replace.
 */
export const STABILITY = { steady: 3, average: 4, variable: 6, unstable: 9 };

/** How long until a target emergency fund is reached. monthsTarget 0 = use the suggestion for `stability`. */
export function emergencyFund({ monthlyExpenses, monthsTarget = 3, currentSaved = 0, monthlySave = 0, apy = 0, stability = '' }) {
  monthlyExpenses = num(monthlyExpenses, 'Monthly expenses');
  const suggested = STABILITY[stability] || STABILITY.average;
  if (!Number(monthsTarget)) monthsTarget = suggested;
  monthsTarget = num(monthsTarget, 'Months of expenses', { min: 1, max: 24 });
  currentSaved = num(currentSaved, 'Already saved');
  monthlySave = num(monthlySave, 'Monthly saving');
  apy = num(apy, 'APY', { max: 20 });
  const target = round2(monthlyExpenses * monthsTarget);
  const gap = round2(Math.max(0, target - currentSaved));
  const base = { target, gap, monthsTarget, suggested, starterGoal: Math.min(1000, target) };
  // Milestones on the way: a $1,000 starter fund, one month of costs, half the goal, the goal.
  const marks = [['starter', Math.min(1000, target)], ['oneMonth', Math.min(monthlyExpenses, target)], ['half', round2(target / 2)], ['target', target]]
    .filter(([, amt], i, all) => amt > 0 && all.findIndex(([, a]) => a === amt) === i)
    .sort((a, b) => a[1] - b[1]);
  const milestones = marks.map(([key, amount]) => ({ key, amount, months: currentSaved >= amount ? 0 : null }));
  if (gap === 0) return { ...base, months: 0, reachable: true, milestones };
  if (monthlySave <= 0 && apy <= 0) return { ...base, months: Infinity, reachable: false, milestones };
  const r = Math.pow(1 + apy / 100, 1 / 12) - 1;
  let bal = currentSaved;
  let months = 0;
  while (bal < target) {
    months++;
    if (months > MAX_MONTHS) return { ...base, months: Infinity, reachable: false, milestones };
    bal = bal * (1 + r) + monthlySave;
    for (const m of milestones) if (m.months === null && bal >= m.amount) m.months = months;
  }
  return { ...base, months, reachable: true, milestones };
}

/** Interest earned in a high-yield savings account vs a typical big-bank savings rate. */
export function savingsInterest({ balance, apy, months = 12, monthlyDeposit = 0, compareApy = 0.01 }) {
  balance = num(balance, 'Balance');
  apy = num(apy, 'APY', { max: 20 });
  months = Math.round(num(months, 'Months', { min: 1, max: 600 }));
  monthlyDeposit = num(monthlyDeposit, 'Monthly deposit');
  compareApy = num(compareApy, 'Comparison APY', { max: 20 });
  const grow = (rateApy) => {
    const r = Math.pow(1 + rateApy / 100, 1 / 12) - 1;
    let b = balance;
    for (let i = 0; i < months; i++) b = b * (1 + r) + monthlyDeposit;
    return b;
  };
  const deposits = balance + monthlyDeposit * months;
  const hy = grow(apy);
  const bank = grow(compareApy);
  return {
    finalBalance: round2(hy),
    interest: round2(hy - deposits),
    compareInterest: round2(bank - deposits),
    difference: round2(hy - bank),
  };
}

/**
 * The credit card minimum-payment trap: what paying only the minimum costs
 * versus a fixed monthly payment. Minimum = max(floor, interest + percent of balance).
 */
export function minimumPaymentTrap({ balance, apr, minPercent = 1, minFloor = 25, fixedPayment }) {
  balance = num(balance, 'Balance');
  apr = num(apr, 'APR', { max: 100 });
  minPercent = num(minPercent, 'Minimum percent', { max: 100 });
  minFloor = num(minFloor, 'Minimum floor');
  const r = apr / 100 / 12;
  const run = (paymentFor) => {
    let b = balance;
    let months = 0;
    let interest = 0;
    while (b > 0.005) {
      months++;
      if (months > MAX_MONTHS) return { months: Infinity, interest: Infinity, paid: Infinity };
      const i = b * r;
      interest += i;
      b += i;
      const pay = Math.min(b, paymentFor(b, i));
      if (pay <= i && b > 0.005 && pay < b) return { months: Infinity, interest: Infinity, paid: Infinity };
      b -= pay;
    }
    return { months, interest: round2(interest), paid: round2(balance + interest) };
  };
  const minimum = run((b, i) => Math.max(minFloor, i + (b - i) * (minPercent / 100)));
  const result = { minimumOnly: minimum };
  if (fixedPayment !== undefined && fixedPayment !== '' && fixedPayment !== null) {
    const fp = num(fixedPayment, 'Fixed payment');
    result.fixed = run(() => fp);
    if (Number.isFinite(result.fixed.interest) && Number.isFinite(minimum.interest)) {
      result.interestSaved = round2(minimum.interest - result.fixed.interest);
    }
  }
  return result;
}

/**
 * Roth vs Traditional with the same pre-tax dollars.
 * Roth: pay tax now at currentRate, withdraw tax-free.
 * Traditional: invest the full amount, pay tax at retirementRate on withdrawal.
 */
export function rothVsTraditional({ annualContribution, currentRate, retirementRate, years, annualReturn = 7 }) {
  const c = num(annualContribution, 'Annual contribution');
  const tNow = num(currentRate, 'Tax rate now', { max: 60 }) / 100;
  const tLater = num(retirementRate, 'Tax rate in retirement', { max: 60 }) / 100;
  years = Math.round(num(years, 'Years', { min: 1, max: 70 }));
  const g = num(annualReturn, 'Annual return', { min: -50, max: 50 }) / 100;
  const fv = (yearly) => {
    let b = 0;
    for (let y = 0; y < years; y++) b = (b + yearly) * (1 + g);
    return b;
  };
  const traditionalPreTax = fv(c);
  const traditional = traditionalPreTax * (1 - tLater);
  const roth = fv(c * (1 - tNow));
  const diff = roth - traditional;
  let winner = 'tie';
  if (Math.abs(diff) > 0.5) winner = diff > 0 ? 'roth' : 'traditional';
  return {
    roth: round2(roth),
    traditional: round2(traditional),
    traditionalBeforeTax: round2(traditionalPreTax),
    difference: round2(Math.abs(diff)),
    winner,
  };
}

import { STANDARD_DEDUCTION, BRACKETS, SOCIAL_SECURITY, MEDICARE } from './tax2026.js';
import { stateIncomeTax } from './state-tax-2026.js';

/** Federal income tax on taxable income using the brackets for the filing status. */
export function federalIncomeTax(taxable, filing = 'single') {
  let tax = 0;
  let lower = 0;
  for (const [upper, rate] of BRACKETS[filing]) {
    if (taxable <= lower) break;
    tax += (Math.min(taxable, upper) - lower) * rate;
    lower = upper;
  }
  return round2(tax);
}

/**
 * Estimated take-home pay for a W-2 salary. Pre-tax 401(k) lowers income tax but not FICA;
 * pre-tax health premiums (cafeteria plan) lower both. State tax is a flat effective rate you enter.
 */
// state: a two-letter code from lib/state-tax-2026.js, or 'custom' (or empty) to use a flat stateRate % of AGI.
export function takeHomePay({ salary, filing = 'single', pretax401k = 0, pretaxHealth = 0, stateRate = 0, payPeriods = 26, state = 'custom' }) {
  salary = num(salary, 'Salary', { max: 1e8 });
  if (!['single', 'married'].includes(filing)) throw new RangeError('Filing status must be single or married');
  pretax401k = num(pretax401k, '401(k) contribution', { max: salary });
  pretaxHealth = num(pretaxHealth, 'Health premiums', { max: salary });
  stateRate = num(stateRate, 'State tax rate', { max: 20 });
  payPeriods = Math.round(num(payPeriods, 'Pay periods', { min: 1, max: 52 }));
  const ficaWages = Math.max(0, salary - pretaxHealth);
  const agi = Math.max(0, salary - pretax401k - pretaxHealth);
  const taxable = Math.max(0, agi - STANDARD_DEDUCTION[filing]);
  const federal = federalIncomeTax(taxable, filing);
  const socialSecurity = round2(Math.min(ficaWages, SOCIAL_SECURITY.wageBase) * SOCIAL_SECURITY.rate);
  const medicare = round2(ficaWages * MEDICARE.rate + Math.max(0, ficaWages - MEDICARE.additionalThreshold[filing]) * MEDICARE.additionalRate);
  const useTable = state && state !== 'custom';
  const stateInfo = useTable ? stateIncomeTax(state, { wages: salary, filing, pretax401k, pretaxHealth }) : null;
  const stateTax = useTable ? stateInfo.tax : round2(agi * (stateRate / 100));
  const takeHome = round2(salary - pretax401k - pretaxHealth - federal - socialSecurity - medicare - stateTax);
  const marginal = (BRACKETS[filing].find(([upper]) => taxable <= upper) || [0, 0.37])[1];
  return {
    salary, taxable: round2(taxable), federal, socialSecurity, medicare, state: stateTax, stateInfo, pretax401k, pretaxHealth, takeHome,
    effectiveState: salary ? stateTax / salary : 0,
    perPaycheck: round2(takeHome / payPeriods), perMonth: round2(takeHome / 12),
    effectiveFederal: salary ? federal / salary : 0, marginal,
  };
}

export const _internal = { MAX_MONTHS, round2 };
