// Bill-due calendar: when each bill is due, month by month, and which ones are paid.
// Pure functions on YYYY-MM-DD strings; the page (bill-calendar/) keeps the data in localStorage.
import { isDay, addDays, addMonths, daysBetween } from './dates.js';

export const FREQS = ['monthly', 'weekly', 'biweekly', 'quarterly', 'yearly', 'once'];
const r2 = (n) => Math.round(n * 100) / 100;
// A real calendar day (Date.parse accepts Feb 30).
const realDay = (d) => isDay(d) && new Date(`${d}T00:00:00Z`).toISOString().slice(0, 10) === d;
const uid = () => Math.random().toString(36).slice(2, 10);

/** Clean a bill from the form or from storage. Returns null when it can't be used. */
export function normalizeBill(b) {
  const name = String(b?.name || '').trim().slice(0, 60);
  const amount = Number(String(b?.amount ?? '').replace(/[$,\s]/g, ''));
  if (!name || !realDay(b?.start) || !Number.isFinite(amount) || amount < 0) return null;
  return {
    id: b.id || uid(), name, amount: r2(amount), start: b.start,
    freq: FREQS.includes(b.freq) ? b.freq : 'monthly', autopay: !!b.autopay,
    until: realDay(b.until) ? b.until : '',
  };
}

export function loadState(json) {
  try {
    const s = typeof json === 'string' ? JSON.parse(json) : json;
    const bills = (Array.isArray(s?.bills) ? s.bills : []).map(normalizeBill).filter(Boolean);
    const ids = new Set(bills.map((b) => b.id));
    const paid = {};
    for (const [k, v] of Object.entries(s?.paid || {})) if (v && ids.has(k.split('|')[0]) && isDay(k.split('|')[1])) paid[k] = true;
    return { bills, paid };
  } catch { return { bills: [], paid: {} }; }
}

/** Due dates of one bill between from and to (inclusive). Monthly bills on the 29th-31st fall on the last day of shorter months. */
export function occurrences(bill, from, to) {
  const out = [];
  const end = bill.until && bill.until < to ? bill.until : to;
  if (bill.start > end) return out;
  if (bill.freq === 'once') return bill.start >= from ? [bill.start] : [];
  if (bill.freq === 'weekly' || bill.freq === 'biweekly') {
    const step = bill.freq === 'weekly' ? 7 : 14;
    let d = bill.start;
    if (d < from) d = addDays(d, Math.ceil(daysBetween(d, from) / step) * step);
    for (; d <= end; d = addDays(d, step)) out.push(d);
    return out;
  }
  const step = { monthly: 1, quarterly: 3, yearly: 12 }[bill.freq];
  const [fy, fm] = from.split('-').map(Number); const [sy, sm] = bill.start.split('-').map(Number);
  let n = Math.max(0, Math.floor(((fy - sy) * 12 + (fm - sm)) / step) - 1);
  for (let d = addMonths(bill.start, n * step); d <= end; d = addMonths(bill.start, ++n * step)) if (d >= from) out.push(d);
  return out;
}

const monthBounds = (ym) => { const first = `${ym}-01`; return [first, addDays(addMonths(first, 1), -1)]; };
export const shiftMonth = (ym, n) => addMonths(`${ym}-01`, n).slice(0, 7);
export const key = (billId, date) => `${billId}|${date}`;

/** Every due item between two days, sorted by date then name. */
export function dueBetween(state, from, to, today) {
  const items = [];
  for (const b of state.bills) for (const date of occurrences(b, from, to)) {
    const k = key(b.id, date);
    const paid = !!state.paid[k];
    items.push({ key: k, date, bill: b, amount: b.amount, paid, overdue: !paid && !b.autopay && date < today });
  }
  return items.sort((a, b) => a.date.localeCompare(b.date) || a.bill.name.localeCompare(b.bill.name));
}

/** The month: items, a Sunday-first grid of weeks, and totals. */
export function monthView(state, ym, today) {
  const [first, last] = monthBounds(ym);
  const items = dueBetween(state, first, last, today);
  const byDay = {};
  for (const it of items) (byDay[it.date] ||= []).push(it);
  const lead = new Date(`${first}T12:00:00Z`).getUTCDay();
  const weeks = []; let week = Array(lead).fill(null);
  for (let d = first; d <= last; d = addDays(d, 1)) {
    week.push({ date: d, items: byDay[d] || [], today: d === today });
    if (week.length === 7) { weeks.push(week); week = []; }
  }
  if (week.length) weeks.push([...week, ...Array(7 - week.length).fill(null)]);
  const sum = (xs) => r2(xs.reduce((s, x) => s + x.amount, 0));
  return {
    ym, items, weeks,
    total: sum(items), paid: sum(items.filter((i) => i.paid)), left: sum(items.filter((i) => !i.paid)),
    overdue: items.filter((i) => i.overdue).length, autopay: sum(items.filter((i) => i.bill.autopay)),
  };
}

export function upcoming(state, today, days = 14) {
  return dueBetween(state, today, addDays(today, days - 1), today).filter((i) => !i.paid);
}

/** Overdue items in the last 60 days, so a bill from last month that slipped still shows. */
export function overdue(state, today) {
  return dueBetween(state, addDays(today, -60), addDays(today, -1), today).filter((i) => i.overdue);
}

export function togglePaid(state, k, on = !state.paid[k]) {
  const paid = { ...state.paid };
  if (on) paid[k] = true; else delete paid[k];
  return { ...state, paid };
}

export function removeBill(state, id) {
  const paid = Object.fromEntries(Object.entries(state.paid).filter(([k]) => !k.startsWith(`${id}|`)));
  return { bills: state.bills.filter((b) => b.id !== id), paid };
}

/** Rough monthly cost of a bill, for the bills list. */
export const perMonth = (b) => r2(b.amount * ({ monthly: 1, weekly: 52 / 12, biweekly: 26 / 12, quarterly: 1 / 3, yearly: 1 / 12, once: 0 }[b.freq]));

// ---------- Calendar file ----------
const esc = (s) => String(s ?? '').replace(/\\/g, '\\\\').replace(/;/g, '\\;').replace(/,/g, '\\,').replace(/\r?\n/g, '\\n');
const fold = (line) => { const out = []; let s = line; while (s.length > 74) { out.push(s.slice(0, 74)); s = ` ${s.slice(74)}`; } out.push(s); return out.join('\r\n'); };
const compact = (d) => d.replace(/-/g, '');

/** Alarm at 9am, `daysBefore` days before an all-day event. */
export const trigger = (daysBefore) => (daysBefore > 0 ? `-PT${daysBefore * 24 - 9}H` : 'PT9H');

/**
 * One repeating event per bill (RRULE), so the calendar keeps reminding without re-exporting.
 * Monthly or quarterly bills on the 29th-31st become "last day of the month" when on the 31st, and explicit dates
 * for the next 24 months on the 29th or 30th (calendars skip months without that day otherwise).
 */
export function billsIcs(state, { daysBefore = 2, title = (b) => `${b.name} due`, describe = (b) => '', calName = 'Bills', stamp = new Date(), money = (n) => `$${n}` } = {}) {
  const dtstamp = stamp.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, '');
  const lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Money Made Simple//Bill calendar//EN', 'CALSCALE:GREGORIAN', `X-WR-CALNAME:${esc(calName)}`];
  const event = (uidPart, b, date, rrule) => {
    lines.push('BEGIN:VEVENT', `UID:${esc(uidPart)}@moneymadesimple-bills`, `DTSTAMP:${dtstamp}`, `DTSTART;VALUE=DATE:${compact(date)}`, `DTEND;VALUE=DATE:${compact(addDays(date, 1))}`);
    if (rrule) lines.push(`RRULE:${rrule}`);
    lines.push(`SUMMARY:${esc(`${title(b)} (${money(b.amount)})`)}`, `DESCRIPTION:${esc(describe(b))}`, 'TRANSP:TRANSPARENT',
      'BEGIN:VALARM', 'ACTION:DISPLAY', `DESCRIPTION:${esc(title(b))}`, `TRIGGER:${trigger(daysBefore)}`, 'END:VALARM', 'END:VEVENT');
  };
  for (const b of state.bills) {
    const until = b.until ? `;UNTIL=${compact(b.until)}` : '';
    const day = Number(b.start.slice(8));
    if (b.freq === 'once') event(b.id, b, b.start, '');
    else if (b.freq === 'weekly' || b.freq === 'biweekly') event(b.id, b, b.start, `FREQ=WEEKLY;INTERVAL=${b.freq === 'weekly' ? 1 : 2}${until}`);
    else if (b.freq === 'yearly') event(b.id, b, b.start, `FREQ=YEARLY${until}`);
    else {
      const interval = b.freq === 'quarterly' ? 3 : 1;
      if (day <= 28) event(b.id, b, b.start, `FREQ=MONTHLY;INTERVAL=${interval}${until}`);
      else if (day === 31) event(b.id, b, b.start, `FREQ=MONTHLY;INTERVAL=${interval};BYMONTHDAY=-1${until}`);
      else occurrences(b, b.start, addMonths(b.start, 24)).forEach((d) => event(`${b.id}-${d}`, b, d, ''));
    }
  }
  lines.push('END:VCALENDAR');
  return lines.map(fold).join('\r\n') + '\r\n';
}
