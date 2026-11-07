// 1099 Money app (freelance-invoices/app/): quarterly estimated tax, mileage log and deduction checklist.
// Pure functions, no DOM, no network. Not tax advice: these are planning estimates.
//
// Estimated tax: the IRS wants at least the smaller of 90% of this year's tax or 100% of last year's
// (110% if last year's AGI was over $150,000), paid in four installments (Form 1040-ES, Publication 505).
// Dates and SE tax come from setaside.js and sidehustle.js so every 1099 tool uses the same numbers.
// Mileage: IRS business standard mileage rate by date driven. 2027's rate is announced in late 2026;
// until then 2027 trips use the latest 2026 rate and are marked provisional. Update RATES when it's out.
// Rates confirmed against irs.gov on 2026-11-07: 72.5 cents through Jun 30, 2026 (Notice 2026-10), 76 cents from
// Jul 1, 2026 (Announcement 2026-11).
import { QUARTERS } from './setaside.js';
import { seTax, QBI } from './sidehustle.js';

const cents = (n) => Math.round((n + Number.EPSILON) * 100) / 100;
const num = (v, d = 0) => { const x = Number(String(v ?? '').replace(/[$,%\s]/g, '')); return Number.isFinite(x) && x >= 0 ? x : d; };
export const BRACKETS = [10, 12, 22, 24, 32, 35, 37];
export const YEARS = Object.keys(QUARTERS).map(Number);
// Social Security wage base by year (SSA): $184,500 for 2026, $192,300 for 2027 (confirmed 2026-11-07).
export const WAGE_BASE = { 2026: 184500, 2027: 192300 };

// ---------- Quarterly estimated tax ----------
/**
 * input: { year, profit (expected net self-employment profit for the year), bracket, stateRate,
 *          withheld (tax already withheld from a W-2 job this year), lastYearTax, highIncome, paid: [q1..q4] }
 */
export function estimate(input, today) {
  const year = YEARS.includes(Number(input.year)) ? Number(input.year) : YEARS[0];
  const profit = num(input.profit);
  const bracket = BRACKETS.includes(Number(input.bracket)) ? Number(input.bracket) : 12;
  const stateRate = Math.min(15, num(input.stateRate));
  const se = seTax(profit, WAGE_BASE[year]);
  const afterHalfSe = Math.max(0, profit - se / 2);
  const income = cents(afterHalfSe * (1 - QBI) * (bracket / 100));
  const state = cents(afterHalfSe * (stateRate / 100));
  const federal = cents(se + income);
  const withheld = num(input.withheld);
  const ninety = cents(Math.max(0, federal * 0.9 - withheld));
  const last = num(input.lastYearTax);
  const safe = last ? cents(Math.max(0, last * (input.highIncome ? 1.1 : 1) - withheld)) : null;
  const required = safe === null ? ninety : Math.min(ninety, safe);
  const method = safe !== null && safe < ninety ? 'safe' : 'ninety';
  const paid = [0, 1, 2, 3].map((i) => num(input.paid?.[i]));
  const paidTotal = cents(paid.reduce((a, b) => a + b, 0));
  const even = cents(required / 4);
  const qs = QUARTERS[year].map((p, i) => ({ ...p, even, paid: paid[i], past: p.due < today }));
  const open = qs.filter((q) => !q.past);
  const left = cents(Math.max(0, required - paidTotal));
  for (const q of qs) q.suggested = q.past ? 0 : cents(left / Math.max(1, open.length));
  // keep the cents exact on the last open quarter
  if (open.length) open[open.length - 1].suggested = cents(left - open.slice(0, -1).reduce((t, q) => t + q.suggested, 0));
  const next = open[0] || null;
  return {
    year, profit, se, income, federal, state, withheld, ninety, safe, required, method, paidTotal, left,
    owesNothing: federal - withheld < 1000, // under $1,000 owed: no estimated payments needed
    quarters: qs, next, stateQuarter: cents(state / 4),
  };
}

// ---------- Mileage log ----------
export const RATES = [
  { from: '2026-01-01', rate: 0.725, note: 'IRS rate Jan 1 to Jun 30, 2026' },
  { from: '2026-07-01', rate: 0.76, note: 'IRS rate from Jul 1, 2026' },
];
export const PROVISIONAL_FROM = '2027-01-01'; // no announced rate yet for dates from here on
export function rateFor(date) {
  let r = null;
  for (const x of RATES) if (date >= x.from) r = x;
  return { rate: r ? r.rate : RATES[0].rate, provisional: date >= PROVISIONAL_FROM };
}

const isDay = (s) => typeof s === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(s) && !Number.isNaN(Date.parse(`${s}T00:00:00Z`)) && new Date(`${s}T00:00:00Z`).toISOString().slice(0, 10) === s;
export function normalizeTrip(t) {
  const miles = Math.round(num(t?.miles, NaN) * 10) / 10;
  if (!isDay(t?.date)) return { error: 'date' };
  if (!(miles > 0) || miles > 2000) return { error: 'miles' };
  const purpose = String(t?.purpose || '').trim().slice(0, 120);
  if (!purpose) return { error: 'purpose' };
  return { id: String(t.id || Math.random().toString(36).slice(2, 10)), date: t.date, miles, purpose, from: String(t?.from || '').trim().slice(0, 80), to: String(t?.to || '').trim().slice(0, 80) };
}

export function mileageSummary(trips, year) {
  const rows = trips.filter((t) => !year || t.date.startsWith(String(year))).sort((a, b) => a.date.localeCompare(b.date) || a.id.localeCompare(b.id))
    .map((t) => { const r = rateFor(t.date); return { ...t, rate: r.rate, provisional: r.provisional, deduction: cents(t.miles * r.rate) }; });
  const miles = Math.round(rows.reduce((s, r) => s + r.miles, 0) * 10) / 10;
  const deduction = cents(rows.reduce((s, r) => s + r.deduction, 0));
  const byMonth = {};
  for (const r of rows) { const m = r.date.slice(0, 7); byMonth[m] = byMonth[m] || { miles: 0, deduction: 0 }; byMonth[m].miles = Math.round((byMonth[m].miles + r.miles) * 10) / 10; byMonth[m].deduction = cents(byMonth[m].deduction + r.deduction); }
  return { rows, miles, deduction, byMonth, provisional: rows.some((r) => r.provisional) };
}

const csvCell = (s) => (/[",\n\r]/.test(String(s)) ? `"${String(s).replace(/"/g, '""')}"` : String(s));
/** The columns the IRS expects a mileage log to show: date, miles, where and the business purpose. */
export function mileageCsv(sum) {
  const lines = [['Date', 'Business purpose', 'From', 'To', 'Miles', 'IRS rate', 'Deduction']];
  for (const r of sum.rows) lines.push([r.date, r.purpose, r.from, r.to, r.miles, r.rate.toFixed(3), r.deduction.toFixed(2)]);
  lines.push(['Total', '', '', '', sum.miles, '', sum.deduction.toFixed(2)]);
  return `${lines.map((l) => l.map(csvCell).join(',')).join('\r\n')}\r\n`;
}

// ---------- Deduction checklist ----------
// Common write-offs for 1099 workers (Schedule C). who: everyone | drivers | home | sellers | creators.
export const DEDUCTIONS = [
  { id: 'mileage', who: 'drivers', t: 'Business miles', d: 'Standard mileage rate, or actual car costs, for business driving. Commuting to a regular workplace doesn\'t count. Keep a log.' },
  { id: 'phone', who: 'everyone', t: 'Phone and internet', d: 'The business share of your phone and internet bills.' },
  { id: 'home', who: 'home', t: 'Home office', d: 'A space used only and regularly for work. The simplified method is $5 a square foot, up to 300 square feet.' },
  { id: 'se-half', who: 'everyone', t: 'Half of self-employment tax', d: 'Taken on your 1040 automatically when you file Schedule SE. Nothing to track, but it\'s why the calculator lowers your income tax.' },
  { id: 'health', who: 'everyone', t: 'Health insurance premiums', d: 'Self-employed health insurance for you and your family, if you weren\'t eligible for an employer plan.' },
  { id: 'retire', who: 'everyone', t: 'Retirement contributions', d: 'A SEP IRA or Solo 401(k) can shelter a big share of profit. Contributions lower income tax, not SE tax.' },
  { id: 'software', who: 'everyone', t: 'Software and subscriptions', d: 'Tools you use for the work: accounting, design, scheduling, cloud storage.' },
  { id: 'equipment', who: 'everyone', t: 'Equipment', d: 'Laptops, cameras, tools and furniture used for the business. Often deductible in full the year you buy them.' },
  { id: 'supplies', who: 'everyone', t: 'Supplies', d: 'Things used up in the work: printer ink, packaging, cleaning supplies for a rental, phone mounts.' },
  { id: 'fees', who: 'everyone', t: 'Platform and payment fees', d: 'Etsy, eBay, Upwork, Stripe and PayPal fees. Check that your 1099-K gross isn\'t already net of them.' },
  { id: 'cogs', who: 'sellers', t: 'Cost of goods sold', d: 'What you paid for inventory you sold, plus shipping to you.' },
  { id: 'shipping', who: 'sellers', t: 'Shipping and postage', d: 'Labels, boxes and postage you paid to send orders.' },
  { id: 'advertising', who: 'everyone', t: 'Advertising and marketing', d: 'Ads, promoted listings, business cards and your website.' },
  { id: 'pro', who: 'everyone', t: 'Professional services', d: 'Tax preparer, bookkeeper and legal fees for the business.' },
  { id: 'education', who: 'everyone', t: 'Training and courses', d: 'Learning that maintains or improves skills for the work you already do.' },
  { id: 'licenses', who: 'everyone', t: 'Licenses, permits and dues', d: 'Business licenses, professional memberships and union dues for your trade.' },
  { id: 'travel', who: 'everyone', t: 'Business travel', d: 'Flights, hotels and half of meals while traveling overnight for work.' },
  { id: 'meals', who: 'everyone', t: 'Business meals (50%)', d: 'Half of meals with clients or while traveling, with a note of who and why.' },
  { id: 'bank', who: 'everyone', t: 'Bank fees and interest', d: 'Fees on a business account and interest on business credit cards or loans.' },
  { id: 'gear', who: 'creators', t: 'Content gear and props', d: 'Lights, mics, props and backdrops used to make paid content.' },
  { id: 'driver-extras', who: 'drivers', t: 'Tolls, parking and car extras', d: 'Business tolls and parking are deductible even with the standard mileage rate. So are phone mounts, chargers and water for riders.' },
];
export const WHO = { everyone: 'Everyone', drivers: 'Drivers', home: 'Work from home', sellers: 'Sellers', creators: 'Creators' };
export const deductionsFor = (who) => DEDUCTIONS.filter((d) => !who || who === 'all' || d.who === 'everyone' || d.who === who);
