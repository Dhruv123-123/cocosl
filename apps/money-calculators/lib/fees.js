// 401(k) fee checker. You type in the funds you hold (name, category, expense ratio, balance),
// usually from your plan's yearly fee disclosure. It shows what each fund costs in dollars a year,
// your average expense ratio, how much fees could take out of your balance over the years, and
// the lowest-cost fund in each category among the funds you entered. It's education, not advice:
// it never says which fund to pick, because cost isn't the only thing that matters.

export const CATEGORIES = ['us-stock', 'intl-stock', 'bond', 'target-date', 'stable', 'other'];

const round2 = (n) => Math.round((n + Number.EPSILON) * 100) / 100;

/** Future value of `balance` plus `monthly` each month for `years` at a yearly return (%), compounded monthly. */
export function growth(balance, monthly, years, ratePct) {
  const r = ratePct / 100 / 12;
  let v = balance;
  for (let m = 0; m < Math.round(years * 12); m++) v = v * (1 + r) + monthly;
  return v;
}

function check(funds, { monthly, years, annualReturn }) {
  if (!Array.isArray(funds) || !funds.length) throw new Error('Add at least one fund.');
  funds.forEach((f, i) => {
    if (!(f.balance >= 0) || !Number.isFinite(f.balance)) throw new Error(`Fund ${i + 1}: enter the balance (0 is fine).`);
    if (!(f.expenseRatio >= 0) || f.expenseRatio > 5) throw new Error(`Fund ${i + 1}: enter the expense ratio as a percent, like 0.05 or 0.85.`);
  });
  if (!(monthly >= 0)) throw new Error('Monthly contribution must be 0 or more.');
  if (!(years >= 1 && years <= 60)) throw new Error('Years must be between 1 and 60.');
  if (!(annualReturn >= 0 && annualReturn <= 15)) throw new Error('Use a yearly return between 0% and 15%.');
}

export function analyzeFees(funds, { monthly = 0, years = 30, annualReturn = 7 } = {}) {
  funds = funds.map((f, i) => ({ name: String(f.name || '').trim() || `Fund ${i + 1}`, category: CATEGORIES.includes(f.category) ? f.category : 'other', expenseRatio: Number(f.expenseRatio), balance: Number(f.balance) }));
  check(funds, { monthly, years, annualReturn });
  const total = funds.reduce((s, f) => s + f.balance, 0);
  // Weight by balance; with no balance yet, weight funds equally.
  const weight = (f) => (total > 0 ? f.balance / total : 1 / funds.length);
  const avgEr = funds.reduce((s, f) => s + weight(f) * f.expenseRatio, 0);

  const cheapest = {};
  for (const f of funds) if (!cheapest[f.category] || f.expenseRatio < cheapest[f.category].expenseRatio) cheapest[f.category] = f;
  const lowEr = funds.reduce((s, f) => s + weight(f) * cheapest[f.category].expenseRatio, 0);

  const gross = growth(total, monthly, years, annualReturn);
  const net = growth(total, monthly, years, annualReturn - avgEr);
  const low = growth(total, monthly, years, annualReturn - lowEr);
  const rows = funds.map((f) => {
    const c = cheapest[f.category];
    return { ...f, yearlyFee: round2(f.balance * f.expenseRatio / 100), cheaperInCategory: c !== f && c.expenseRatio < f.expenseRatio ? { name: c.name, expenseRatio: c.expenseRatio } : null };
  });
  return {
    funds: rows,
    total: round2(total),
    avgExpenseRatio: Math.round(avgEr * 1000) / 1000,
    yearlyFees: round2(rows.reduce((s, f) => s + f.yearlyFee, 0)),
    endNoFees: round2(gross),
    endWithFees: round2(net),
    feeDrag: round2(gross - net),
    lowestCostEnd: round2(low),
    lowestCostGap: round2(low - net),
    years, monthly, annualReturn,
  };
}
