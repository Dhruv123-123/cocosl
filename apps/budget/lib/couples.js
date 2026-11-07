// "Money date" couples budget: split shared expenses 50/50, by income, or a custom split,
// see who pays what (into a joint account, or to settle up), and keep a monthly check-in checklist.
// Pure functions, no DOM. The page saves everything in localStorage only.

const cents = (n) => Math.round(n * 100) / 100;
const amt = (v) => { const x = Number(String(v ?? '').replace(/[$,\s]/g, '')); return Number.isFinite(x) && x >= 0 ? cents(x) : NaN; };
const uid = () => Math.random().toString(36).slice(2, 10);

export const METHODS = { equal: 'Split 50/50', income: 'Split by income', custom: 'Our own split' };
export const CATEGORIES = { home: 'Rent or mortgage', utilities: 'Utilities and internet', groceries: 'Groceries', transport: 'Car and transport', insurance: 'Insurance', kids: 'Kids and pets', subscriptions: 'Subscriptions', savings: 'Shared savings goal', fun: 'Dates and fun', other: 'Other' };
export const PAID_BY = { a: 'Partner 1', b: 'Partner 2', joint: 'Joint account' };

// The monthly money date. Keep it short and kind: about 30 minutes.
export const CHECKLIST = [
  { id: 'win', text: 'Start with a win: one money thing that went well this month' },
  { id: 'review', text: 'Look at last month: did shared spending match the plan?' },
  { id: 'settle', text: 'Settle up, or move this month\'s amounts into the joint account' },
  { id: 'bills', text: 'Check bills and subscriptions: anything to cancel or call about?' },
  { id: 'coming', text: 'Big expenses coming in the next 3 months (trips, gifts, car, medical)' },
  { id: 'goals', text: 'Progress on shared goals: emergency fund, debt, a trip, a home' },
  { id: 'fun', text: 'Each person\'s no-questions-asked fun money for next month' },
  { id: 'next', text: 'Pick the date and place for next month\'s money date' },
];

export function emptyPlan() {
  return { v: 1, partners: [{ name: '', income: 0 }, { name: '', income: 0 }], method: 'income', customA: 50, expenses: [], checks: {}, notes: {} };
}

export function loadPlan(json) {
  try {
    const p = typeof json === 'string' ? JSON.parse(json) : json;
    if (!p || !Array.isArray(p.expenses) || !Array.isArray(p.partners) || p.partners.length !== 2) return emptyPlan();
    const base = emptyPlan();
    return {
      ...base, ...p,
      method: METHODS[p.method] ? p.method : 'income',
      partners: p.partners.map((x) => ({ name: String(x?.name || '').slice(0, 30), income: Number.isFinite(+x?.income) && +x.income >= 0 ? +x.income : 0 })),
      expenses: p.expenses.filter((e) => e && e.id && e.name && Number.isFinite(+e.amount)).map((e) => ({ ...e, amount: +e.amount, paidBy: PAID_BY[e.paidBy] ? e.paidBy : 'joint', category: CATEGORIES[e.category] ? e.category : 'other' })),
      checks: p.checks && typeof p.checks === 'object' ? p.checks : {},
      notes: p.notes && typeof p.notes === 'object' ? p.notes : {},
    };
  } catch { return emptyPlan(); }
}

export const names = (plan) => [plan.partners[0].name || 'Partner 1', plan.partners[1].name || 'Partner 2'];

export function setPartner(plan, i, { name, income }) {
  if (name !== undefined) plan.partners[i].name = String(name).trim().slice(0, 30);
  if (income !== undefined) { const v = amt(income); plan.partners[i].income = Number.isNaN(v) ? 0 : v; }
}

export function setMethod(plan, method, customA) {
  if (!METHODS[method]) throw new RangeError('Pick how to split');
  plan.method = method;
  if (customA !== undefined) { const v = Number(customA); if (Number.isFinite(v)) plan.customA = Math.min(100, Math.max(0, v)); }
}

export function addExpense(plan, { name, amount, paidBy = 'joint', category = 'other' }) {
  const n = String(name || '').trim().slice(0, 60);
  if (!n) throw new RangeError('Name the expense');
  const a = amt(amount);
  if (Number.isNaN(a) || a <= 0) throw new RangeError('Enter the monthly amount');
  const e = { id: uid(), name: n, amount: a, paidBy: PAID_BY[paidBy] ? paidBy : 'joint', category: CATEGORIES[category] ? category : 'other' };
  plan.expenses.push(e);
  return e;
}

export function removeExpense(plan, id) { plan.expenses = plan.expenses.filter((e) => e.id !== id); }

/** Partner 1's share of shared costs, 0..1, and why. */
export function shareA(plan) {
  if (plan.method === 'equal') return { a: 0.5, reason: 'equal' };
  if (plan.method === 'custom') return { a: plan.customA / 100, reason: 'custom' };
  const [x, y] = plan.partners.map((p) => p.income || 0);
  if (x + y <= 0) return { a: 0.5, reason: 'no-income' }; // fall back to 50/50 until incomes are in
  return { a: x / (x + y), reason: 'income' };
}

/** Split an amount in cents so the two parts always add up exactly. */
export function splitAmount(total, a) {
  const first = cents(total * a);
  return [first, cents(total - first)];
}

export function summary(plan) {
  const { a, reason } = shareA(plan);
  const total = cents(plan.expenses.reduce((t, e) => t + e.amount, 0));
  const [owedA, owedB] = splitAmount(total, a);
  const paid = { a: 0, b: 0, joint: 0 };
  for (const e of plan.expenses) paid[e.paidBy] = cents(paid[e.paidBy] + e.amount);
  // Joint account: each puts in their share of what the joint account pays.
  const [jointA, jointB] = splitAmount(paid.joint, a);
  // Settle up: what each paid personally versus their share of personally paid bills.
  const personal = cents(paid.a + paid.b);
  const [fairA] = splitAmount(personal, a);
  const diff = cents(paid.a - fairA); // > 0: partner 1 paid more than their share, partner 2 owes them
  const settle = Math.abs(diff) < 0.01 ? null : diff > 0 ? { from: 1, to: 0, amount: diff } : { from: 0, to: 1, amount: -diff };
  const incomes = plan.partners.map((p) => p.income || 0);
  const left = [cents(incomes[0] - owedA), cents(incomes[1] - owedB)];
  const byCategory = {};
  for (const e of plan.expenses) byCategory[e.category] = cents((byCategory[e.category] || 0) + e.amount);
  return {
    shareA: a, shareB: 1 - a, reason, total, owed: [owedA, owedB], paid, joint: [jointA, jointB], settle,
    incomes, left, pctOfIncome: incomes.map((inc, i) => (inc ? [owedA, owedB][i] / inc : null)), byCategory,
  };
}

export const monthKey = (d = new Date()) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;

export function toggleCheck(plan, month, id) {
  if (!CHECKLIST.some((c) => c.id === id)) return false;
  const list = new Set(plan.checks[month] || []);
  if (list.has(id)) list.delete(id); else list.add(id);
  plan.checks[month] = [...list];
  return list.has(id);
}

export function progress(plan, month) {
  const done = (plan.checks[month] || []).filter((id) => CHECKLIST.some((c) => c.id === id)).length;
  return { done, total: CHECKLIST.length, complete: done === CHECKLIST.length };
}

/** Months in a row (ending with `month` or the one before it) with a finished money date. */
export function streak(plan, month) {
  let [y, m] = month.split('-').map(Number);
  const key = () => `${y}-${String(m).padStart(2, '0')}`;
  const back = () => { m -= 1; if (!m) { m = 12; y -= 1; } };
  if (!progress(plan, key()).complete) back();
  let n = 0;
  while (progress(plan, key()).complete && n < 600) { n++; back(); }
  return n;
}

export function setNote(plan, month, text) {
  const t = String(text || '').slice(0, 2000);
  if (t) plan.notes[month] = t; else delete plan.notes[month];
}
