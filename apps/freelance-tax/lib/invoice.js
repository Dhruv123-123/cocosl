// Free invoice template: due dates from payment terms, line-item totals, invoice numbering and a
// completeness check against the invoice checklist used in the 1099 Money content (launch/1099-money).
// Pure functions; the page (invoice-template/app.js) renders and prints.

export const TERMS = {
  receipt: { label: 'Due on receipt', days: 0 },
  net7: { label: 'Net 7', days: 7 },
  net15: { label: 'Net 15', days: 15 },
  net30: { label: 'Net 30', days: 30 },
};

const num = (x) => {
  const v = parseFloat(String(x ?? '').replace(/[$,%\s]/g, ''));
  return Number.isFinite(v) ? v : 0;
};
const cents = (x) => Math.round(x * 100) / 100;

// Due date as YYYY-MM-DD, counted in calendar days from the invoice date. '' if the date is missing.
export function dueDate(issued, terms = 'net15') {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(issued || '')) return '';
  const d = new Date(issued + 'T12:00:00Z');
  d.setUTCDate(d.getUTCDate() + (TERMS[terms] ? TERMS[terms].days : 15));
  return d.toISOString().slice(0, 10);
}

// "2027-06-30" → "June 30, 2027": a written date is harder to misread than a term.
export function longDate(iso) {
  if (!iso) return '';
  return new Date(iso + 'T12:00:00Z').toLocaleDateString('en-US', { timeZone: 'UTC', month: 'long', day: 'numeric', year: 'numeric' });
}

export function totals(items = [], { taxRate = 0, deposit = 0 } = {}) {
  const lines = items
    .map((it) => ({ desc: String(it.desc || '').trim(), qty: Math.max(0, num(it.qty)), rate: Math.max(0, num(it.rate)) }))
    .filter((it) => it.desc || it.qty * it.rate > 0)
    .map((it) => ({ ...it, amount: cents(it.qty * it.rate) }));
  const subtotal = cents(lines.reduce((s, l) => s + l.amount, 0));
  const tax = cents(subtotal * Math.min(Math.max(num(taxRate), 0), 25) / 100);
  const paid = cents(Math.min(Math.max(num(deposit), 0), subtotal + tax));
  return { lines, subtotal, tax, deposit: paid, due: cents(subtotal + tax - paid) };
}

// Next invoice number: keeps any prefix and zero padding. "2026-014" → "2026-015", "INV9" → "INV10".
export function nextNumber(prev = '') {
  const m = String(prev).match(/^(.*?)(\d+)$/);
  if (!m) return prev ? `${prev}-2` : '001';
  const n = String(Number(m[2]) + 1).padStart(m[2].length, '0');
  return m[1] + n;
}

export function lateFeeLine(percentPerMonth, due) {
  const p = num(percentPerMonth);
  if (p <= 0 || !due) return '';
  return `A late fee of ${p}% per month applies to any balance unpaid after ${longDate(due)}, as agreed.`;
}

// The checklist: what's missing before this invoice is ready to send.
export function missing(inv = {}) {
  const t = totals(inv.items, inv);
  const out = [];
  if (!String(inv.fromName || '').trim()) out.push('Your name or business name');
  if (!String(inv.fromEmail || '').trim()) out.push('Your email, so they can reply');
  if (!String(inv.toName || '').trim()) out.push("The client's name or company");
  if (!String(inv.number || '').trim()) out.push('An invoice number');
  if (!inv.issued) out.push('The invoice date');
  if (!t.lines.length || t.lines.some((l) => !l.desc)) out.push('A description for every line');
  if (t.subtotal <= 0) out.push('At least one amount');
  if (!String(inv.payHow || '').trim()) out.push('How to pay you (a payment link or bank details)');
  return out;
}
