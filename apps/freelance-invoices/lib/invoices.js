// Freelancer invoice tracker and late-fee calculator (1099 Money). Pure functions, no DOM.
// Everything stays in the browser. General information, not legal or tax advice: a late fee is
// only collectable if the client agreed to it (contract or invoice terms) and is within state limits.
import { isDay, addDays, daysBetween } from './dates.js';

export const TERMS = { 0: 'Due on receipt', 7: 'Net 7', 15: 'Net 15', 30: 'Net 30', 45: 'Net 45', 60: 'Net 60' };
export const FEE_TYPES = { none: 'No late fee', percent: '% per month on the unpaid amount', flat: 'Flat fee, once' };

const uid = () => Math.random().toString(36).slice(2, 10);
const cents = (n) => Math.round(Number(n) * 100) / 100;
const clean = (s, max = 120) => String(s ?? '').trim().slice(0, max);
const num = (v) => { const n = Number(String(v ?? '').replace(/[$,\s]/g, '')); return Number.isFinite(n) ? n : NaN; };

export const emptyBook = () => ({ version: 1, invoices: [], me: { name: '', business: '', payHow: '' } });

export function loadBook(json) {
  try {
    const b = typeof json === 'string' ? JSON.parse(json) : json;
    if (!b || !Array.isArray(b.invoices)) return emptyBook();
    return { version: 1, invoices: b.invoices.filter((i) => i && isDay(i.issued) && isDay(i.due) && i.amount > 0), me: { ...emptyBook().me, ...(b.me || {}) } };
  } catch { return emptyBook(); }
}

/** Validate form values into an invoice. */
export function makeInvoice(v) {
  const client = clean(v.client, 80);
  if (!client) throw new Error('Add the client\'s name.');
  const amount = cents(num(v.amount));
  if (!(amount > 0)) throw new Error('Add the invoice amount.');
  if (!isDay(v.issued)) throw new Error('Add the invoice date.');
  const termDays = v.terms === 'custom' ? null : Number(v.terms ?? 30);
  const due = v.terms === 'custom' ? v.due : addDays(v.issued, Number.isFinite(termDays) ? termDays : 30);
  if (!isDay(due)) throw new Error('Add the due date.');
  if (due < v.issued) throw new Error('The due date can\'t be before the invoice date.');
  const feeType = FEE_TYPES[v.feeType] ? v.feeType : 'none';
  const feeRate = feeType === 'percent' ? num(v.feeRate) : 0;
  const feeFlat = feeType === 'flat' ? num(v.feeFlat) : 0;
  if (feeType === 'percent' && !(feeRate > 0 && feeRate <= 10)) throw new Error('Enter a monthly late fee between 0.1% and 10%.');
  if (feeType === 'flat' && !(feeFlat > 0)) throw new Error('Enter the flat late fee.');
  return {
    id: v.id || uid(),
    number: clean(v.number, 30),
    client,
    clientEmail: clean(v.clientEmail, 120),
    project: clean(v.project, 120),
    amount,
    issued: v.issued,
    terms: v.terms === 'custom' ? 'custom' : String(termDays),
    due,
    feeType,
    feeRate: feeType === 'percent' ? cents(feeRate) : 0,
    feeFlat: feeType === 'flat' ? cents(feeFlat) : 0,
    grace: Math.max(0, Math.min(60, Math.round(num(v.grace) || 0))),
    sent: isDay(v.sent) ? v.sent : '',
    payments: Array.isArray(v.payments) ? v.payments : [],
    writtenOff: Boolean(v.writtenOff),
    reminders: Array.isArray(v.reminders) ? v.reminders : [],
  };
}

export function addInvoice(book, values) {
  const inv = makeInvoice(values);
  book.invoices.push(inv);
  return inv;
}

const find = (book, id) => {
  const inv = book.invoices.find((i) => i.id === id);
  if (!inv) throw new Error('Invoice not found.');
  return inv;
};

export const paidSoFar = (inv) => cents((inv.payments || []).reduce((t, p) => t + p.amount, 0));
export const balance = (inv) => Math.max(0, cents(inv.amount - paidSoFar(inv)));

export function recordPayment(book, id, amount, date) {
  const inv = find(book, id);
  const a = cents(num(amount));
  if (!(a > 0)) throw new Error('Enter the amount paid.');
  if (!isDay(date)) throw new Error('Add the date it was paid.');
  inv.payments.push({ amount: a, date });
  return inv;
}

/** Mark paid in full: records the remaining balance (plus nothing for fees; add fees as a payment if paid). */
export function markPaid(book, id, date) {
  const inv = find(book, id);
  const left = balance(inv);
  if (left > 0) recordPayment(book, id, left, date);
  return inv;
}

export function markSent(book, id, date) {
  const inv = find(book, id);
  if (!isDay(date)) throw new Error('Add the date you sent it.');
  inv.sent = date;
  return inv;
}

export function logReminder(book, id, stage, date) {
  const inv = find(book, id);
  inv.reminders.push({ stage, date });
  return inv;
}

export function removeInvoice(book, id) {
  book.invoices = book.invoices.filter((i) => i.id !== id);
}

/**
 * The late fee owed on `today`, per the terms on the invoice.
 * percent: rate% of the unpaid balance for each month (or part month) past due after the grace days.
 * flat: charged once when the invoice is past due after the grace days.
 */
export function lateFee(inv, today) {
  const late = daysBetween(inv.due, today) - (inv.grace || 0);
  const owed = balance(inv);
  if (inv.feeType === 'none' || late <= 0 || owed <= 0 || inv.writtenOff) return { fee: 0, months: 0, apr: 0 };
  if (inv.feeType === 'flat') return { fee: inv.feeFlat, months: 0, apr: 0 };
  const months = Math.ceil(late / 30);
  return { fee: cents(owed * (inv.feeRate / 100) * months), months, apr: cents(inv.feeRate * 12) };
}

/**
 * state: paid | written-off | draft (not sent yet) | sent (not due) | due-soon (3 days or less)
 *        | due-today | overdue; plus partly paid.
 */
export function status(inv, today) {
  const owed = balance(inv);
  const paidDate = (inv.payments || []).map((p) => p.date).sort().at(-1) || '';
  if (owed <= 0) return { state: 'paid', paidDate, daysToPay: paidDate ? daysBetween(inv.issued, paidDate) : null, owed: 0, fee: 0, total: 0, daysLate: 0, partly: false };
  if (inv.writtenOff) return { state: 'written-off', owed, fee: 0, total: owed, daysLate: 0, partly: paidSoFar(inv) > 0 };
  const daysLate = daysBetween(inv.due, today);
  const { fee, months, apr } = lateFee(inv, today);
  let state = 'sent';
  if (!inv.sent) state = 'draft';
  else if (daysLate > 0) state = 'overdue';
  else if (daysLate === 0) state = 'due-today';
  else if (daysLate >= -3) state = 'due-soon';
  return { state, owed, fee, months, apr, total: cents(owed + fee), daysLate: Math.max(0, daysLate), daysLeft: Math.max(0, -daysLate), partly: paidSoFar(inv) > 0 };
}

export const STAGES = {
  before: 'Friendly heads-up (before it\'s due)',
  due: 'Due today',
  late: 'Gentle nudge (a few days late)',
  firm: 'Firm follow-up (2+ weeks late)',
  final: 'Final notice (30+ days late)',
};

/** Which reminder fits today. '' when none is needed (draft, paid, or too early). */
export function suggestedStage(inv, today) {
  const s = status(inv, today);
  if (s.state === 'due-soon') return 'before';
  if (s.state === 'due-today') return 'due';
  if (s.state !== 'overdue') return '';
  if (s.daysLate >= 30) return 'final';
  if (s.daysLate >= 14) return 'firm';
  return 'late';
}

const money = (n) => `$${Number(n).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
const pretty = (d) => new Date(`${d}T12:00:00Z`).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric', timeZone: 'UTC' });

/** A polite reminder email: { subject, body }. me = { name, business, payHow }. */
export function reminderEmail(inv, stage, today, me = {}) {
  const s = status(inv, today);
  const ref = inv.number ? `invoice ${inv.number}` : `my invoice from ${pretty(inv.issued)}`;
  const Ref = ref[0].toUpperCase() + ref.slice(1);
  const what = inv.project ? ` for ${inv.project}` : '';
  const sign = [me.name, me.business].map((x) => clean(x, 80)).filter(Boolean).join('\n') || '[Your name]';
  const pay = clean(me.payHow, 300);
  const payLine = pay ? `\n\nYou can pay here: ${pay}` : '';
  const amountLine = s.fee > 0
    ? `The balance is ${money(s.owed)}, plus a late fee of ${money(s.fee)} under the payment terms on the invoice, for a total of ${money(s.total)}.`
    : `The balance is ${money(s.owed)}.`;
  const hi = `Hi ${inv.client.split(' ')[0]},`;
  const bodies = {
    before: [`Subject: ${Ref} is due ${pretty(inv.due)}`, hi, `A quick heads-up that ${ref}${what} (${money(s.owed)}) is due on ${pretty(inv.due)}.${payLine}`, 'Thanks so much, and let me know if you need another copy or anything else to process it.'],
    due: [`Subject: ${Ref} is due today`, hi, `Just a friendly reminder that ${ref}${what} is due today. ${amountLine}${payLine}`, 'If it\'s already on its way, thank you, and please ignore this.'],
    late: [`Subject: Following up on ${ref}`, hi, `I wanted to follow up on ${ref}${what}, which was due on ${pretty(inv.due)}. ${amountLine}${payLine}`, 'It may just have slipped through the cracks. Could you let me know when I can expect payment? If there\'s a problem with the invoice, I\'m happy to sort it out.'],
    firm: [`Subject: ${Ref} is now ${s.daysLate} days overdue`, hi, `${Ref}${what} was due on ${pretty(inv.due)} and is now ${s.daysLate} days overdue. ${amountLine}${payLine}`, 'Please arrange payment by the end of this week, or reply with a date I can expect it. If you need to split it into two payments, tell me and we can agree a plan.'],
    final: [`Subject: Final notice: ${ref}, ${s.daysLate} days overdue`, hi, `This is a final reminder about ${ref}${what}, due ${pretty(inv.due)} and now ${s.daysLate} days overdue. ${amountLine}${payLine}`, 'I value working with you, but I need to resolve this. If payment or a payment plan isn\'t agreed within 10 days, I\'ll pause any ongoing work and look at my next options for collecting it.'],
  };
  const parts = bodies[stage] || bodies.late;
  return { subject: parts[0].replace(/^Subject: /, ''), body: [parts[1], '', parts[2], '', parts[3], '', 'Thanks,', sign].join('\n') };
}

export function mailto(inv, email) {
  return `mailto:${encodeURIComponent(inv.clientEmail || '')}?subject=${encodeURIComponent(email.subject)}&body=${encodeURIComponent(email.body)}`;
}

const ORDER = { overdue: 0, 'due-today': 1, 'due-soon': 2, sent: 3, draft: 4, 'written-off': 5, paid: 6 };

export function board(book, today) {
  return book.invoices
    .map((inv) => ({ ...inv, status: status(inv, today) }))
    .sort((a, b) => ORDER[a.status.state] - ORDER[b.status.state] || a.due.localeCompare(b.due));
}

export function summary(book, today) {
  const rows = board(book, today);
  const year = today.slice(0, 4);
  const paid = rows.filter((r) => r.status.state === 'paid');
  const times = paid.map((r) => r.status.daysToPay).filter((d) => d !== null);
  const open = rows.filter((r) => !['paid', 'written-off'].includes(r.status.state));
  return {
    outstanding: cents(open.reduce((t, r) => t + r.status.owed, 0)),
    overdue: cents(rows.filter((r) => r.status.state === 'overdue').reduce((t, r) => t + r.status.owed, 0)),
    overdueCount: rows.filter((r) => r.status.state === 'overdue').length,
    fees: cents(open.reduce((t, r) => t + (r.status.fee || 0), 0)),
    paidThisYear: cents(rows.reduce((t, r) => t + (r.payments || []).filter((p) => p.date.startsWith(year)).reduce((a, p) => a + p.amount, 0), 0)),
    avgDaysToPay: times.length ? Math.round(times.reduce((a, b) => a + b, 0) / times.length) : null,
  };
}

/** Calendar reminders for unpaid invoices: 3 days before, due date, and 7 days late. */
export function reminderEvents(book, today) {
  const out = [];
  for (const r of board(book, today)) {
    if (['paid', 'written-off', 'draft'].includes(r.status.state)) continue;
    const label = `${r.client}${r.number ? ` #${r.number}` : ''}`;
    out.push({ uid: `inv-${r.id}-before`, date: addDays(r.due, -3), title: `Invoice due in 3 days: ${label}`, description: `Send a friendly heads-up to ${r.client}.` });
    out.push({ uid: `inv-${r.id}-due`, date: r.due, title: `Invoice due today: ${label}`, description: `Check whether ${r.client} has paid.` });
    out.push({ uid: `inv-${r.id}-late`, date: addDays(r.due, 7), title: `Follow up if unpaid: ${label}`, description: 'Open the invoice tracker for a ready-to-send follow-up email.' });
  }
  return out.filter((e) => e.date >= today);
}

export function toCsv(book, today) {
  const q = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;
  const head = ['Invoice', 'Client', 'Project', 'Amount', 'Issued', 'Due', 'Status', 'Paid', 'Balance', 'Late fee', 'Days late'];
  const rows = board(book, today).map((r) => [r.number, r.client, r.project, r.amount, r.issued, r.due, r.status.state, paidSoFar(r), r.status.owed, r.status.fee || 0, r.status.daysLate || 0]);
  return [head, ...rows].map((r) => r.map(q).join(',')).join('\r\n') + '\r\n';
}
