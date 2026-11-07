// Quarterly tax set-aside for freelancers (set-aside/ page). Pure functions, no DOM.
// Self-employment tax: 15.3% on 92.35% of profit (IRS Schedule SE). QBI deduction: 20% (sec. 199A).
// Estimated tax periods and due dates: IRS Form 1040-ES (2026), https://www.irs.gov/forms-pubs/about-form-1040-es
// and Publication 505. 2027 dates apply the weekend and holiday rule (Jan 15 2028 is a Saturday and
// Jan 17 is Martin Luther King Jr. Day); check them against the 2027 Form 1040-ES when it's out.
// Safe harbor: no underpayment penalty if you pay 100% of last year's tax (110% if last year's AGI was over $150,000).
import { SE_FACTOR, QBI } from './sidehustle.js';

export const SE_RATE = 0.153;
export const QUARTERS = {
  2026: [
    { q: 1, from: '2026-01-01', to: '2026-03-31', due: '2026-04-15' }, { q: 2, from: '2026-04-01', to: '2026-05-31', due: '2026-06-15' },
    { q: 3, from: '2026-06-01', to: '2026-08-31', due: '2026-09-15' }, { q: 4, from: '2026-09-01', to: '2026-12-31', due: '2027-01-15' },
  ],
  2027: [
    { q: 1, from: '2027-01-01', to: '2027-03-31', due: '2027-04-15' }, { q: 2, from: '2027-04-01', to: '2027-05-31', due: '2027-06-15' },
    { q: 3, from: '2027-06-01', to: '2027-08-31', due: '2027-09-15' }, { q: 4, from: '2027-09-01', to: '2027-12-31', due: '2028-01-18' },
  ],
};
export const BRACKETS = [0, 10, 12, 22, 24, 32, 35, 37];
const cents = (n) => Math.round(n * 100) / 100;
const num = (v, d = 0) => { const x = Number(v); return Number.isFinite(x) && x >= 0 ? x : d; };

/** Share of each dollar received to set aside: SE tax + income tax on what's left after half SE tax and QBI + state. */
export function rate({ bracket = 12, stateRate = 0, costsPct = 10 } = {}) {
  const profitShare = 1 - Math.min(100, num(costsPct)) / 100;
  const se = SE_RATE * SE_FACTOR;
  const income = (num(bracket) / 100) * (1 - se / 2) * (1 - QBI);
  const state = Math.min(15, num(stateRate)) / 100;
  const exact = profitShare * (se + income + state);
  return { exact, pct: Math.ceil(exact * 100), se: profitShare * se, income: profitShare * income, state: profitShare * state };
}

export const setAside = (amount, pct) => cents(num(amount) * (num(pct) / 100));

export function quarterOf(iso) {
  const y = String(iso).slice(0, 4);
  return (QUARTERS[y] || []).find((p) => iso >= p.from && iso <= p.to) || null;
}

/** Current or next quarter whose due date is on or after today. */
export function nextDue(today) {
  for (const y of Object.keys(QUARTERS).sort()) for (const p of QUARTERS[y]) if (p.due >= today) return { year: Number(y), ...p };
  return null;
}
export const daysUntil = (from, to) => Math.round((Date.parse(`${to}T00:00:00Z`) - Date.parse(`${from}T00:00:00Z`)) / 86400000);

/** payments: [{ date, amount, pct }]; paid: { 'YYYY-Qn': amount sent to the IRS }. */
export function quarters(payments, year, paid = {}) {
  return (QUARTERS[year] || []).map((p) => {
    const inQ = payments.filter((x) => x.date >= p.from && x.date <= p.to);
    const income = cents(inQ.reduce((t, x) => t + num(x.amount), 0));
    const reserved = cents(inQ.reduce((t, x) => t + setAside(x.amount, x.pct), 0));
    const key = `${year}-Q${p.q}`;
    return { ...p, key, count: inQ.length, income, reserved, sent: num(paid[key]) };
  });
}

/** Safe harbor quarterly payment from last year's total tax (Form 1040 line 24). */
export function safeHarbor(lastYearTax, highIncome = false) {
  const t = num(lastYearTax);
  if (!t) return null;
  const year = cents(t * (highIncome ? 1.1 : 1));
  return { year, quarter: cents(year / 4) };
}

export function yearTotals(qs) {
  const income = cents(qs.reduce((t, q) => t + q.income, 0));
  const reserved = cents(qs.reduce((t, q) => t + q.reserved, 0));
  const sent = cents(qs.reduce((t, q) => t + q.sent, 0));
  return { income, reserved, sent, stillHeld: cents(reserved - sent) };
}
