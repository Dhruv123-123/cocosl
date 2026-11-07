// Read transactions from text pasted out of a bank statement or online banking page, so the
// subscription audit works without a CSV download. Runs in the browser; nothing is uploaded.
// Handles: CSV with a header row, tab-separated rows copied from a web table or spreadsheet,
// and plain statement lines such as "10/03  NETFLIX.COM 866-579-7172  15.49  1,234.56".
import { importBankCsv } from './budget.js';

const MONTHS = { jan: 1, feb: 2, mar: 3, apr: 4, may: 5, jun: 6, jul: 7, aug: 8, sep: 9, sept: 9, oct: 10, nov: 11, dec: 12 };
const FULL = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december'];
/** 'Oct', 'Sept' or 'October' -> 10; anything else -> 0. */
const monthNum = (w) => { const x = String(w).toLowerCase(); return x.length > 3 && !FULL.some((f) => f.startsWith(x)) ? 0 : (MONTHS[x.slice(0, 4)] || MONTHS[x.slice(0, 3)] || 0); };
const pad = (n) => String(n).padStart(2, '0');
const MONEY = /^(?:[-+]?\(?-?\$?\d{1,3}(?:,\d{3})*(?:\.\d{2})\)?-?|[-+]?\(?-?\$?\d+\.\d{2}\)?-?)(?:\s?(?:CR|DR))?$/i;
const INCOME = /\b(payroll|direct dep(osit)?|deposit|refund|interest (paid|earned)|transfer from|zelle from|reversal|cashback|cash back|salary|paycheck)\b/i;

function fullDate(y, m, d, today) {
  if (!(m >= 1 && m <= 12 && d >= 1 && d <= 31)) return '';
  let year = y;
  if (year === null) {
    year = Number(today.slice(0, 4));
    if (`${year}-${pad(m)}-${pad(d)}` > today) year -= 1; // "Dec 28" read in January is last year
  } else if (year < 100) year += 2000;
  const s = `${year}-${pad(m)}-${pad(d)}`;
  return Number.isNaN(Date.parse(`${s}T00:00:00Z`)) ? '' : s;
}

/** A date at the start of the text. Returns { date, rest } or null. */
export function leadingDate(text, today) {
  const t = text.trim();
  let m = /^(\d{4})-(\d{1,2})-(\d{1,2})\b\s*(.*)$/.exec(t);
  if (m) return { date: fullDate(+m[1], +m[2], +m[3], today), rest: m[4] };
  m = /^(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?\b\s*(.*)$/.exec(t);
  if (m) return { date: fullDate(m[3] ? +m[3] : null, +m[1], +m[2], today), rest: m[4] };
  m = /^([A-Za-z]{3,9})\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?(?:\s+(\d{4}))?\b\s*(.*)$/.exec(t);
  if (m && monthNum(m[1])) return { date: fullDate(m[3] ? +m[3] : null, monthNum(m[1]), +m[2], today), rest: m[4] };
  m = /^(\d{1,2})\s+([A-Za-z]{3,9})\.?,?(?:\s+(\d{4}))?\b\s*(.*)$/.exec(t);
  if (m && monthNum(m[2])) return { date: fullDate(m[3] ? +m[3] : null, monthNum(m[2]), +m[1], today), rest: m[4] };
  return null;
}

export function moneyValue(token) {
  const s = token.trim();
  const credit = /CR$/i.test(s) || /^\+/.test(s);
  const neg = /^\(|^-|-\)?$|\)$/.test(s.replace(/\s?(CR|DR)$/i, ''));
  const n = Number(s.replace(/\s?(CR|DR)$/i, '').replace(/[^0-9.]/g, ''));
  return { value: neg ? -n : n, credit };
}

/** One plain statement line: { date, amount (as printed), credit, note } or null. */
export function parseLine(line, today) {
  const lead = leadingDate(line, today);
  if (!lead || !lead.date) return null;
  let rest = lead.rest;
  const second = leadingDate(rest, today); // many statements show transaction and posting dates
  if (second && second.date) rest = second.rest;
  const tokens = rest.trim().split(/\s+/);
  // Glue "15.49 CR" into one token.
  for (let i = tokens.length - 1; i > 0; i--) if (/^(CR|DR)$/i.test(tokens[i])) { tokens[i - 1] += ` ${tokens[i]}`; tokens.splice(i, 1); }
  const trailing = [];
  while (tokens.length && MONEY.test(tokens.at(-1))) trailing.unshift(tokens.pop());
  if (!trailing.length || !tokens.length) return null;
  // With an amount and a running balance at the end, the first trailing number is the amount.
  const { value, credit } = moneyValue(trailing[0]);
  if (!Number.isFinite(value) || value === 0) return null;
  const note = tokens.join(' ').replace(/\s{2,}/g, ' ').trim().slice(0, 120);
  return { date: lead.date, amount: value, credit, note };
}

const looksDelimited = (first) => /date/i.test(first) && /(amount|debit|withdrawal|description|payee)/i.test(first) && /[,\t;]/.test(first);

/**
 * Parse pasted text. Returns { transactions: [{date, amount (spending positive), note}], skipped, format, error? }.
 */
export function parseStatement(text, { today = new Date().toISOString().slice(0, 10) } = {}) {
  const lines = String(text || '').replace(/\r/g, '').split('\n').map((l) => l.trim()).filter(Boolean);
  if (!lines.length) return { transactions: [], skipped: 0, format: 'text', error: 'Paste some transactions first' };
  const headerAt = lines.findIndex((l) => looksDelimited(l));
  if (headerAt >= 0 && headerAt < 5) {
    const delim = lines[headerAt].includes('\t') ? '\t' : lines[headerAt].split(';').length > lines[headerAt].split(',').length ? ';' : ',';
    const csv = delim === ','
      ? lines.slice(headerAt).join('\n')
      : lines.slice(headerAt).map((l) => l.split(delim).map((c) => `"${c.trim().replace(/"/g, '""')}"`).join(',')).join('\n');
    return { ...importBankCsv(csv), format: delim === '\t' ? 'table' : 'csv' };
  }
  const parsed = [];
  let skipped = 0;
  for (const l of lines) {
    const p = parseLine(l, today);
    if (p) parsed.push(p); else if (/\d/.test(l)) skipped++;
  }
  if (!parsed.length) return { transactions: [], skipped, format: 'text', error: "Couldn't find any lines that start with a date and end with an amount" };
  // If most amounts are printed negative, negative means spending (like most online banking).
  const negativeIsSpending = parsed.filter((p) => p.amount < 0).length > parsed.length / 2;
  const transactions = parsed.map((p) => {
    let amount = negativeIsSpending ? -p.amount : Math.abs(p.amount) * (p.amount < 0 ? -1 : 1);
    if (p.credit || (!negativeIsSpending && INCOME.test(p.note))) amount = -Math.abs(amount);
    return { date: p.date, amount: Math.round(amount * 100) / 100, note: p.note };
  });
  return { transactions, skipped, format: 'text' };
}
