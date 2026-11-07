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

/** How long until a target emergency fund is reached. */
export function emergencyFund({ monthlyExpenses, monthsTarget = 3, currentSaved = 0, monthlySave = 0, apy = 0 }) {
  monthlyExpenses = num(monthlyExpenses, 'Monthly expenses');
  monthsTarget = num(monthsTarget, 'Months of expenses', { min: 1, max: 24 });
  currentSaved = num(currentSaved, 'Already saved');
  monthlySave = num(monthlySave, 'Monthly saving');
  apy = num(apy, 'APY', { max: 20 });
  const target = round2(monthlyExpenses * monthsTarget);
  const gap = round2(Math.max(0, target - currentSaved));
  if (gap === 0) return { target, gap, months: 0, reachable: true };
  if (monthlySave <= 0 && apy <= 0) return { target, gap, months: Infinity, reachable: false };
  const r = Math.pow(1 + apy / 100, 1 / 12) - 1;
  let bal = currentSaved;
  let months = 0;
  while (bal < target) {
    months++;
    if (months > MAX_MONTHS) return { target, gap, months: Infinity, reachable: false };
    bal = bal * (1 + r) + monthlySave;
  }
  return { target, gap, months, reachable: true, starterGoal: Math.min(1000, target) };
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

export const _internal = { MAX_MONTHS, round2 };
