// Sinking-funds planner (sinking-funds.html, fondos-ahorro.html). Pure functions, no DOM.
// A sinking fund is money set aside a little each month for a bill you know is coming: car insurance, the
// holidays, repairs. The maths matches the Sinking Funds tab of Money Dashboard Pro exactly
// (launch/dashboard-pro/build.py): months left = 0 if the date has passed, else DATEDIF(today, due, "m") + 1;
// save each month = still to save / months left (all of it if no months are left).
// The export pastes into that tab: funds at A5 (Fund, Target, Needed by) and deposits at K5 (Date, Fund, Amount).

export const PRESETS = {
  en: [['Car insurance', 900, 6], ['Holidays and gifts', 800, 0], ['Car repairs and tires', 600, 12], ['Back to school', 400, 0], ['Vet and pet care', 500, 12], ['Annual subscriptions and memberships', 200, 9], ['Home repairs', 1000, 12], ['Travel', 1500, 8]],
  es: [['Seguro del carro', 900, 6], ['Fiestas y regalos', 800, 0], ['Reparaciones y llantas del carro', 600, 12], ['Regreso a clases', 400, 0], ['Veterinario y mascotas', 500, 12], ['Suscripciones y membresías anuales', 200, 9], ['Arreglos de la casa', 1000, 12], ['Viajes', 1500, 8]],
};

const isDay = (s) => typeof s === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(s) && new Date(`${s}T00:00:00Z`).toISOString().slice(0, 10) === s;
const num = (v) => { const x = Number(String(v ?? '').replace(/[$,\s]/g, '')); return Number.isFinite(x) ? x : NaN; };
const r2 = (n) => Math.round((n + Number.EPSILON) * 100) / 100;
const parts = (s) => s.split('-').map(Number);

/** Spreadsheet DATEDIF(start, end, "m"): whole months from start to end. */
export function datedifMonths(start, end) {
  const [y1, m1, d1] = parts(start); const [y2, m2, d2] = parts(end);
  let m = (y2 - y1) * 12 + (m2 - m1);
  if (d2 < d1) m -= 1;
  return Math.max(0, m);
}

/** A date `months` from today, on a given day of the month (clamped to the month's length). Preset helper. */
export function monthsAhead(today, months, day = 1) {
  const [y, m] = parts(today);
  const t = new Date(Date.UTC(y, m - 1 + months, 1));
  const last = new Date(Date.UTC(t.getUTCFullYear(), t.getUTCMonth() + 1, 0)).getUTCDate();
  t.setUTCDate(Math.min(day, last));
  return t.toISOString().slice(0, 10);
}

/** The next Dec 1 (holidays) or Aug 1 (school) when a preset has no fixed month count. */
export function presetDate(name, months, today) {
  if (months) return monthsAhead(today, months);
  const [y, m] = parts(today);
  const month = /school|clases/i.test(name) ? 8 : 12;
  const year = m < month ? y : y + 1;
  return `${year}-${String(month).padStart(2, '0')}-01`;
}

export function normalizeFund(f = {}) {
  const name = String(f.name || '').trim().slice(0, 60);
  const target = num(f.target);
  const saved = num(f.saved ?? 0);
  if (!name) return { error: 'name' };
  if (!(target > 0) || target > 1e7) return { error: 'target' };
  if (!isDay(f.due)) return { error: 'due' };
  if (!(saved >= 0) && String(f.saved ?? '') !== '') return { error: 'saved' };
  return { id: f.id || Math.random().toString(36).slice(2, 10), name, target: r2(target), due: f.due, saved: r2(saved >= 0 ? saved : 0) };
}

export function fundPlan(f, today) {
  const still = r2(Math.max(0, f.target - f.saved));
  const monthsLeft = f.due <= today ? 0 : datedifMonths(today, f.due) + 1;
  const monthly = still === 0 ? 0 : monthsLeft === 0 ? still : r2(still / monthsLeft);
  return { ...f, still, monthsLeft, monthly, done: f.saved >= f.target, late: monthsLeft === 0 && still > 0, pct: Math.min(1, f.saved / f.target) };
}

/** perPay: paychecks a month (4 weekly, 2 for every two weeks or twice a month, 1 monthly) to show a per-paycheck amount. */
export function plan(funds, today, { perPay = 2 } = {}) {
  const rows = funds.map((f) => fundPlan(f, today)).sort((a, b) => a.due.localeCompare(b.due));
  const monthly = r2(rows.reduce((t, r) => t + r.monthly, 0));
  return {
    rows,
    target: r2(rows.reduce((t, r) => t + r.target, 0)),
    saved: r2(rows.reduce((t, r) => t + r.saved, 0)),
    still: r2(rows.reduce((t, r) => t + r.still, 0)),
    monthly,
    perPaycheck: r2(monthly / (perPay || 1)),
    late: rows.filter((r) => r.late).length,
    next: rows.find((r) => !r.done) || null,
  };
}

/** Tab-separated rows for pasting straight into Google Sheets or Excel: Pro's Sinking Funds tab, cell A5. */
export const fundsTsv = (funds) => funds.map((f) => [f.name.replace(/\t/g, ' '), f.target, f.due].join('\t')).join('\n');
/** Starting balances as deposits dated today: the same tab, cell K5. */
export const depositsTsv = (funds, today) => funds.filter((f) => f.saved > 0).map((f) => [today, f.name.replace(/\t/g, ' '), f.saved].join('\t')).join('\n');

const csvCell = (s) => (/[",\n]/.test(String(s)) ? `"${String(s).replace(/"/g, '""')}"` : String(s));
export function plannerCsv(p, lang = 'en') {
  const head = lang === 'es' ? ['Fondo', 'Meta', 'Para cuándo', 'Ahorrado', 'Falta', 'Meses que quedan', 'Guardar al mes'] : ['Fund', 'Target', 'Needed by', 'Saved so far', 'Still to save', 'Months left', 'Save each month'];
  const rows = p.rows.map((r) => [r.name, r.target, r.due, r.saved, r.still, r.monthsLeft, r.monthly]);
  return `${[head, ...rows].map((r) => r.map(csvCell).join(',')).join('\r\n')}\r\n`;
}
