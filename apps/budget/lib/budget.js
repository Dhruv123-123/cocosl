// The 20-Minute Budget app: data model and math. Pure functions, no DOM, so it is fully testable.
// State is plain JSON kept in the browser (localStorage); nothing is sent to a server.

export const SCHEMA_VERSION = 1;

export const DEFAULT_CATEGORIES = [
  ['Rent / housing', 'needs'], ['Groceries', 'needs'], ['Transport', 'needs'], ['Bills & phone', 'needs'],
  ['Eating out', 'wants'], ['Fun & shopping', 'wants'], ['Savings', 'savings'], ['Debt payoff', 'savings'],
];

const uid = () => Math.random().toString(36).slice(2, 10);
export const monthOf = (date) => String(date).slice(0, 7);
export const thisMonth = (now = new Date()) => `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
const cents = (n) => Math.round(Number(n) * 100) / 100;

export function createState(now = new Date()) {
  return {
    version: SCHEMA_VERSION,
    currency: 'USD',
    months: { [thisMonth(now)]: { income: 0, plan: {} } },
    categories: DEFAULT_CATEGORIES.map(([name, group]) => ({ id: uid(), name, group })),
    transactions: [],
    goals: [],
  };
}

/** Load saved JSON safely; anything unreadable falls back to a fresh state. */
export function loadState(json, now = new Date()) {
  try {
    const s = typeof json === 'string' ? JSON.parse(json) : json;
    if (!s || typeof s !== 'object' || !Array.isArray(s.categories) || !Array.isArray(s.transactions)) return createState(now);
    s.version ??= SCHEMA_VERSION;
    s.months ??= {};
    s.goals ??= [];
    s.currency ??= 'USD';
    return s;
  } catch {
    return createState(now);
  }
}

export function ensureMonth(state, month) {
  if (!state.months[month]) {
    // New month starts from the most recent month's plan, so you don't re-type it.
    const prev = Object.keys(state.months).filter((m) => m < month).sort().at(-1);
    const base = prev ? state.months[prev] : { income: 0, plan: {} };
    state.months[month] = { income: base.income, plan: { ...base.plan } };
  }
  return state.months[month];
}

export function addCategory(state, name, group = 'wants', { limit = Infinity } = {}) {
  name = String(name || '').trim();
  if (!name) throw new Error('Give the category a name');
  if (state.categories.length >= limit) throw new LimitError('categories', limit);
  if (state.categories.some((c) => c.name.toLowerCase() === name.toLowerCase())) throw new Error('That category already exists');
  const cat = { id: uid(), name: name.slice(0, 40), group: ['needs', 'wants', 'savings'].includes(group) ? group : 'wants' };
  state.categories.push(cat);
  return cat;
}

export function removeCategory(state, id) {
  state.categories = state.categories.filter((c) => c.id !== id);
  for (const t of state.transactions) if (t.categoryId === id) t.categoryId = null;
  for (const m of Object.values(state.months)) delete m.plan[id];
}

export function setPlan(state, month, categoryId, amount) {
  const m = ensureMonth(state, month);
  m.plan[categoryId] = Math.max(0, cents(amount) || 0);
}

export function setIncome(state, month, amount) {
  ensureMonth(state, month).income = Math.max(0, cents(amount) || 0);
}

/** amount > 0 is spending; negative is a refund or money back. */
export function addTransaction(state, { date, amount, categoryId = null, note = '' }) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) throw new Error('Use a date like 2026-11-07');
  const a = cents(amount);
  if (!Number.isFinite(a) || a === 0) throw new Error('Enter an amount');
  const tx = { id: uid(), date, amount: a, categoryId, note: String(note).slice(0, 120) };
  state.transactions.push(tx);
  ensureMonth(state, monthOf(date));
  return tx;
}

export function removeTransaction(state, id) {
  state.transactions = state.transactions.filter((t) => t.id !== id);
}

/** Everything the dashboard shows for one month. */
export function summarize(state, month) {
  const m = state.months[month] || { income: 0, plan: {} };
  const txs = state.transactions.filter((t) => monthOf(t.date) === month);
  const spentBy = {};
  for (const t of txs) spentBy[t.categoryId ?? 'none'] = cents((spentBy[t.categoryId ?? 'none'] || 0) + t.amount);
  const rows = state.categories.map((c) => {
    const planned = m.plan[c.id] || 0;
    const spent = spentBy[c.id] || 0;
    return { id: c.id, name: c.name, group: c.group, planned, spent, left: cents(planned - spent), over: spent > planned && planned >= 0 && spent > 0 && spent - planned > 0.004 };
  });
  const planned = cents(rows.reduce((s, r) => s + r.planned, 0));
  const spent = cents(txs.reduce((s, t) => s + t.amount, 0));
  const byGroup = { needs: 0, wants: 0, savings: 0 };
  for (const r of rows) byGroup[r.group] = cents(byGroup[r.group] + r.planned);
  return {
    month,
    income: m.income,
    planned,
    spent,
    unassigned: cents(m.income - planned), // "give every dollar a job": aim for 0
    leftToSpend: cents(planned - spent),
    uncategorized: spentBy.none || 0,
    rows,
    split: splitCheck(m.income, byGroup),
    transactions: txs.sort((a, b) => b.date.localeCompare(a.date)),
  };
}

/** Compare the plan with the 50/30/20 guideline (needs/wants/savings). */
export function splitCheck(income, byGroup) {
  if (!income) return null;
  const pct = (v) => Math.round((v / income) * 100);
  return {
    needs: { planned: byGroup.needs, pct: pct(byGroup.needs), target: 50 },
    wants: { planned: byGroup.wants, pct: pct(byGroup.wants), target: 30 },
    savings: { planned: byGroup.savings, pct: pct(byGroup.savings), target: 20 },
  };
}

/** Money for a savings goal: monthly amount needed to hit it by the deadline. */
export function goalPlan({ target, saved = 0, deadline }, now = new Date()) {
  const [y, mo] = deadline.split('-').map(Number);
  const months = Math.max(1, (y - now.getFullYear()) * 12 + (mo - (now.getMonth() + 1)));
  const remaining = Math.max(0, target - saved);
  return { months, monthly: cents(remaining / months), remaining: cents(remaining), done: remaining === 0 };
}

// ---------- CSV ----------

/** RFC 4180-ish CSV parser: handles quotes, escaped quotes, commas and newlines in fields. */
export function parseCsv(text) {
  const rows = [];
  let row = [], field = '', q = false;
  text = String(text).replace(/^﻿/, '');
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (q) {
      if (c === '"' && text[i + 1] === '"') { field += '"'; i++; }
      else if (c === '"') q = false;
      else field += c;
    } else if (c === '"') q = true;
    else if (c === ',') { row.push(field); field = ''; }
    else if (c === '\n' || c === '\r') {
      if (c === '\r' && text[i + 1] === '\n') i++;
      row.push(field); rows.push(row); row = []; field = '';
    } else field += c;
  }
  if (field !== '' || row.length) { row.push(field); rows.push(row); }
  return rows.filter((r) => r.some((f) => f.trim() !== ''));
}

function parseDate(s) {
  s = s.trim();
  let m = /^(\d{4})-(\d{1,2})-(\d{1,2})/.exec(s);
  if (m) return `${m[1]}-${m[2].padStart(2, '0')}-${m[3].padStart(2, '0')}`;
  m = /^(\d{1,2})\/(\d{1,2})\/(\d{2,4})$/.exec(s); // US banks: MM/DD/YYYY
  if (m) { const y = m[3].length === 2 ? '20' + m[3] : m[3]; return `${y}-${m[1].padStart(2, '0')}-${m[2].padStart(2, '0')}`; }
  return null;
}

const parseAmount = (s) => {
  if (s == null) return NaN;
  s = String(s).trim();
  if (!s) return NaN;
  const neg = /^\(.*\)$/.test(s) || /^-/.test(s) || /-$/.test(s);
  const n = Number(s.replace(/[()$,\s-]/g, ''));
  return neg ? -n : n;
};

/**
 * Turn a bank's CSV export into transactions. Finds the date, description and amount columns
 * by header name. Handles one signed "Amount" column or separate Debit / Credit columns.
 * Bank exports usually show spending as negative; we flip it so spending is positive.
 * Returns { transactions, skipped }.
 */
export function importBankCsv(text, { spendingIsNegative = 'auto' } = {}) {
  const rows = parseCsv(text);
  if (rows.length < 2) return { transactions: [], skipped: 0, error: 'No rows found' };
  const header = rows[0].map((h) => h.trim().toLowerCase());
  const find = (...names) => header.findIndex((h) => names.some((n) => h === n || h.includes(n)));
  const di = find('transaction date', 'posted date', 'posting date', 'date', 'fecha');
  const ni = find('description', 'payee', 'merchant', 'name', 'memo', 'details', 'descripción', 'descripcion', 'concepto', 'detalle', 'comercio');
  const ai = header.findIndex((h) => h === 'amount' || /^amount\b/.test(h) || /^(monto|importe|cantidad)\b/.test(h));
  const debit = find('debit', 'withdrawal', 'money out', 'cargo', 'débito', 'debito', 'retiro');
  const credit = find('credit', 'deposit', 'money in', 'abono', 'crédito', 'credito', 'depósito', 'deposito');
  if (di < 0 || (ai < 0 && debit < 0)) return { transactions: [], skipped: rows.length - 1, error: 'Could not find Date and Amount columns' };

  const body = rows.slice(1);
  let flip = spendingIsNegative;
  if (flip === 'auto' && ai >= 0) {
    // Most rows are purchases. If most amounts are negative, the bank shows spending as negative.
    const amts = body.map((r) => parseAmount(r[ai])).filter(Number.isFinite);
    flip = amts.filter((a) => a < 0).length >= amts.length / 2;
  }
  const transactions = [];
  let skipped = 0;
  for (const r of body) {
    const date = parseDate(r[di] || '');
    let amount;
    if (ai >= 0) {
      amount = parseAmount(r[ai]);
      if (flip) amount = -amount;
    } else {
      const d = parseAmount(r[debit]);
      const c = parseAmount(r[credit]);
      amount = (Number.isFinite(d) ? Math.abs(d) : 0) - (Number.isFinite(c) ? Math.abs(c) : 0);
    }
    if (!date || !Number.isFinite(amount) || amount === 0) { skipped++; continue; }
    transactions.push({ date, amount: cents(amount), note: (ni >= 0 ? r[ni] : '').trim().slice(0, 120) });
  }
  return { transactions, skipped };
}

/** Simple keyword auto-categorising for imported rows. Returns a category id or null. */
export function guessCategory(state, note) {
  const n = note.toLowerCase();
  const rules = [
    [/rent|mortgage|landlord|apartment/, 'rent'], [/grocer|safeway|kroger|aldi|trader joe|whole foods|walmart|costco|target|lidl|publix/, 'grocer'],
    [/uber|lyft|shell|chevron|exxon|bp |gas|transit|metro|parking|toll/, 'transport'], [/verizon|at&t|t-mobile|comcast|xfinity|electric|water|utility|internet|phone/, 'bill'],
    [/restaurant|cafe|coffee|starbucks|mcdonald|chipotle|doordash|grubhub|uber eats|pizza|bar /, 'eating'], [/amazon|netflix|spotify|steam|cinema|movie|hulu|disney/, 'fun'],
  ];
  for (const [re, key] of rules) {
    if (re.test(n)) {
      const cat = state.categories.find((c) => c.name.toLowerCase().includes(key));
      if (cat) return cat.id;
    }
  }
  return null;
}

const csvField = (v) => (/[",\n]/.test(String(v)) ? `"${String(v).replace(/"/g, '""')}"` : String(v));

export function exportCsv(state) {
  const name = Object.fromEntries(state.categories.map((c) => [c.id, c.name]));
  const lines = [['Date', 'Amount', 'Category', 'Note'].join(',')];
  for (const t of [...state.transactions].sort((a, b) => a.date.localeCompare(b.date))) {
    lines.push([t.date, t.amount.toFixed(2), name[t.categoryId] || '', t.note].map(csvField).join(','));
  }
  return lines.join('\n') + '\n';
}

export class LimitError extends Error {
  constructor(feature, limit) {
    super(`The free plan includes ${limit} ${feature}. Upgrade to Pro for unlimited.`);
    this.feature = feature;
    this.limit = limit;
  }
}
