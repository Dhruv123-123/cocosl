// Federal tax math for US freelancers (Schedule C sole proprietors). Pure functions, no DOM.
// Same method as launch/1099-money/product/build_tracker.py, so the free tool and the paid
// tracker agree. 2026 figures: re-check every January (IRS Rev. Proc. 2025-32, SSA wage base).

export const TAX_YEAR = 2026;

export const TABLES = {
  brackets: {
    single: [[0, 0.10], [12400, 0.12], [50400, 0.22], [105700, 0.24], [201775, 0.32], [256225, 0.35], [640600, 0.37]],
    mfj: [[0, 0.10], [24800, 0.12], [100800, 0.22], [211400, 0.24], [403550, 0.32], [512450, 0.35], [768700, 0.37]],
  },
  standardDeduction: { single: 16100, mfj: 32200 },
  ssWageBase: 184500,
  ssRate: 0.124,
  medicareRate: 0.029,
  netEarningsFactor: 0.9235,
  qbiRate: 0.2,
  safeHarborHighAgi: 150000,
};

// Due dates for a tax year's four estimated payments (weekend/holiday rollovers not applied).
export function dueDates(year = TAX_YEAR) {
  return [
    { q: 1, label: 'Q1', covers: 'Jan 1 – Mar 31', date: new Date(Date.UTC(year, 3, 15)) },
    { q: 2, label: 'Q2', covers: 'Apr 1 – May 31', date: new Date(Date.UTC(year, 5, 15)) },
    { q: 3, label: 'Q3', covers: 'Jun 1 – Aug 31', date: new Date(Date.UTC(year, 8, 15)) },
    { q: 4, label: 'Q4', covers: 'Sep 1 – Dec 31', date: new Date(Date.UTC(year + 1, 0, 15)) },
  ];
}

// Which payment is next on `today` (1-4), or 5 when the Q4 deadline has passed.
export function nextPayment(today = new Date(), year = TAX_YEAR) {
  const t = Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate());
  const next = dueDates(year).find((d) => t <= d.date.getTime());
  return next ? next.q : 5;
}

export function incomeTax(taxable, status = 'single') {
  const b = TABLES.brackets[status] || TABLES.brackets.single;
  let tax = 0;
  for (let i = 0; i < b.length; i++) {
    const [lo, rate] = b[i];
    const hi = i + 1 < b.length ? b[i + 1][0] : Infinity;
    if (taxable > lo) tax += (Math.min(taxable, hi) - lo) * rate;
  }
  return tax;
}

const n = (x) => (Number.isFinite(+x) ? Math.max(0, +x) : 0);

// Full-year federal tax on freelance profit (plus optional W-2 wages).
export function federalTax({ profit = 0, status = 'single', w2Wages = 0 } = {}) {
  profit = n(profit); w2Wages = n(w2Wages);
  status = status === 'mfj' ? 'mfj' : 'single';
  const T = TABLES;
  const netEarnings = profit * T.netEarningsFactor < 400 ? 0 : profit * T.netEarningsFactor;
  const ssBase = Math.min(netEarnings, Math.max(0, T.ssWageBase - w2Wages));
  const seTax = ssBase * T.ssRate + netEarnings * T.medicareRate;
  const halfSe = seTax / 2;
  const agi = profit - halfSe + w2Wages;
  const std = T.standardDeduction[status];
  const preQbi = Math.max(0, agi - std);
  const qbi = Math.min(T.qbiRate * Math.max(0, profit - halfSe), T.qbiRate * preQbi);
  const taxable = Math.max(0, preQbi - qbi);
  const incTax = incomeTax(taxable, status);
  const total = seTax + incTax;
  // Tax caused by the freelance income alone (what the set-aside has to cover).
  const withoutFreelance = w2Wages > 0 ? incomeTax(Math.max(0, w2Wages - std), status) : 0;
  return {
    profit, netEarnings, seTax, halfSe, agi, standardDeduction: std, qbi, taxable, incomeTax: incTax, total,
    freelanceShare: Math.max(0, total - withoutFreelance),
    effectiveRate: profit > 0 ? Math.max(0, total - withoutFreelance) / profit : 0,
  };
}

// What to pay each quarter to stay clear of the underpayment penalty.
export function quarterlyPlan({
  profit = 0, status = 'single', w2Wages = 0, withholding = 0,
  priorYearTax = 0, priorYearAgi = 0, paidSoFar = 0, stateRate = 0, nextQuarter = 1,
} = {}) {
  const fed = federalTax({ profit, status, w2Wages });
  withholding = n(withholding); priorYearTax = n(priorYearTax); paidSoFar = n(paidSoFar);
  const currentYear = 0.9 * fed.total;
  const safeHarborRate = n(priorYearAgi) > TABLES.safeHarborHighAgi ? 1.1 : 1.0;
  const safeHarbor = priorYearTax > 0 ? priorYearTax * safeHarborRate : null;
  const required = safeHarbor === null ? currentYear : Math.min(currentYear, safeHarbor);
  const method = safeHarbor !== null && safeHarbor <= currentYear ? 'safe-harbor' : 'current-year';
  const needFromEstimates = Math.max(0, required - withholding);
  const q = Math.min(Math.max(1, Math.round(nextQuarter) || 1), 5);
  const left = Math.max(0, 5 - q);
  // Required cumulative by each deadline is 25/50/75/100% of the annual requirement.
  const dueBy = (k) => Math.max(0, needFromEstimates * (k / 4) - paidSoFar);
  const schedule = dueDates().map((d) => ({ ...d, cumulativeRequired: needFromEstimates * (d.q / 4) }));
  const thisPayment = q <= 4 ? dueBy(q) : 0;
  const perRemaining = left ? Math.max(0, needFromEstimates - paidSoFar) / left : 0;
  const balanceAtFiling = Math.max(0, fed.total - withholding - Math.max(paidSoFar, needFromEstimates));
  const state = n(profit) * Math.min(n(stateRate), 0.2);
  const setAsideRate = fed.profit > 0 ? (fed.freelanceShare + state) / fed.profit : 0;
  return {
    ...fed, currentYear, safeHarbor, safeHarborRate, required, method, needFromEstimates,
    nextQuarter: q, thisPayment, perRemaining, schedule, balanceAtFiling, state, setAsideRate,
    owesEstimates: fed.total - withholding >= 1000,
  };
}
