// Wedding budget planner (wedding-budget.html, presupuesto-boda.html). Pure functions, no DOM.
// Split a total budget into the usual categories, track each one's estimate, actual cost and what's paid,
// and work out the cost per guest and what to save each month until the day.
// The starting shares are a planning rule of thumb, not survey data: the reception (venue, catering, bar) takes about
// 42%, then photos, attire and the rest, with a 5% buffer for the extras every wedding has. Honeymoon starts at 0
// because many couples budget it separately. People change all of them.
// Categories match the Wedding Budget Sheet (products thread). The sheet paste (weddingTsv) fills its Budget tab
// columns Category, Budget, Actual, Paid; "Actual" carries the final cost, or the quote while there's no final cost.

export const CATEGORIES = [
  ['venue', 0.16, 'Venue', 'Lugar'],
  ['catering', 0.20, 'Catering', 'Banquete'],
  ['bar', 0.06, 'Bar and drinks', 'Bar y bebidas'],
  ['photo', 0.08, 'Photography', 'Fotografía'],
  ['video', 0.04, 'Videography', 'Video'],
  ['attire', 0.06, 'Attire', 'Vestuario'],
  ['beauty', 0.02, 'Hair and makeup', 'Peinado y maquillaje'],
  ['flowers', 0.07, 'Flowers and decor', 'Flores y decoración'],
  ['music', 0.06, 'Music and DJ', 'Música y DJ'],
  ['cake', 0.02, 'Cake and desserts', 'Pastel y postres'],
  ['stationery', 0.02, 'Invitations and stationery', 'Invitaciones y papelería'],
  ['rings', 0.03, 'Rings', 'Anillos'],
  ['transport', 0.02, 'Transportation', 'Transporte'],
  ['favors', 0.01, 'Favors', 'Recuerdos'],
  ['officiant', 0.02, 'Officiant and license', 'Oficiante y licencia'],
  ['rentals', 0.03, 'Rentals', 'Renta de mobiliario'],
  ['planner', 0.04, 'Planner or coordinator', 'Organizador o coordinador'],
  ['gifts', 0.01, 'Gifts', 'Regalos'],
  ['honeymoon', 0, 'Honeymoon', 'Luna de miel'],
  ['buffer', 0.05, 'Buffer for extras', 'Colchón para extras'],
];
// Venue, catering and bar grow with every guest, so "per guest" for the reception adds those three.
export const PER_HEAD = ['venue', 'catering', 'bar'];
export const KEYS = CATEGORIES.map((c) => c[0]);
export const nameOf = (key, lang = 'en') => { const c = CATEGORIES.find((x) => x[0] === key); return c ? c[lang === 'es' ? 3 : 2] : key; };

const num = (v) => { const x = Number(String(v ?? '').replace(/[$,\s]/g, '')); return Number.isFinite(x) && x >= 0 ? x : 0; };
const r2 = (n) => Math.round((n + Number.EPSILON) * 100) / 100;
const isDay = (s) => typeof s === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(s) && new Date(`${s}T00:00:00Z`).toISOString().slice(0, 10) === s;

/** Whole-dollar budget per category that adds up exactly to the total (the venue takes the rounding). */
export function splitBudget(total) {
  const t = Math.round(num(total));
  const out = Object.fromEntries(CATEGORIES.map(([k, share]) => [k, Math.floor(t * share)]));
  out.venue += t - Object.values(out).reduce((a, b) => a + b, 0);
  return out;
}

/** Months to save: whole months from today to the month before the wedding, at least 1. */
export function monthsUntil(today, date) {
  if (!isDay(date) || date <= today) return 0;
  const [y1, m1] = today.split('-').map(Number); const [y2, m2] = date.split('-').map(Number);
  return Math.max(1, (y2 - y1) * 12 + (m2 - m1));
}

/**
 * state: { total, guests, date, saved, rows: { key: { budget, estimate, actual, paid } } }
 * For each row the expected cost is the actual if known, else the estimate, else the budget.
 */
export function summary(state, today) {
  const total = num(state.total);
  const guests = Math.round(num(state.guests));
  const rows = KEYS.map((k) => {
    const r = state.rows?.[k] || {};
    const budget = num(r.budget); const estimate = num(r.estimate); const actual = num(r.actual); const paid = num(r.paid);
    const expected = actual || estimate || budget;
    return { key: k, budget, estimate, actual, paid, expected, owed: r2(Math.max(0, expected - paid)), over: expected > budget && budget > 0 ? r2(expected - budget) : 0 };
  });
  const expected = r2(rows.reduce((t, r) => t + r.expected, 0));
  const paid = r2(rows.reduce((t, r) => t + r.paid, 0));
  const owed = r2(rows.reduce((t, r) => t + r.owed, 0));
  const saved = num(state.saved);
  const months = monthsUntil(today, state.date);
  const toSave = r2(Math.max(0, owed - saved));
  return {
    total, guests, rows, expected, paid, owed, saved, months,
    left: r2(total - expected),
    perGuest: guests ? r2(expected / guests) : null,
    venuePerGuest: guests ? r2(rows.filter((r) => PER_HEAD.includes(r.key)).reduce((t, r) => t + r.expected, 0) / guests) : null,
    monthly: months ? r2(toSave / months) : null,
    toSave,
    overRows: rows.filter((r) => r.over > 0).map((r) => r.key),
  };
}

const csvCell = (s) => (/[",\n]/.test(String(s)) ? `"${String(s).replace(/"/g, '""')}"` : String(s));
export function weddingCsv(sum, lang = 'en') {
  const head = lang === 'es' ? ['Categoría', 'Presupuesto', 'Cotización', 'Costo real', 'Pagado', 'Falta pagar'] : ['Category', 'Budget', 'Estimate', 'Actual', 'Paid', 'Still owed'];
  const rows = sum.rows.map((r) => [nameOf(r.key, lang), r.budget, r.estimate || '', r.actual || '', r.paid || '', r.owed]);
  rows.push([lang === 'es' ? 'Total' : 'Total', r2(sum.rows.reduce((t, r) => t + r.budget, 0)), '', '', sum.paid, sum.owed]);
  return `${[head, ...rows].map((r) => r.map(csvCell).join(',')).join('\r\n')}\r\n`;
}
/** Tab-separated rows (no header) for the sheet's Budget tab: Category, Budget, Actual (final cost, else the quote), Paid. */
export const weddingTsv = (sum, lang = 'en') => sum.rows.map((r) => [nameOf(r.key, lang), r.budget, r.actual || r.estimate || '', r.paid || ''].join('\t')).join('\n');
