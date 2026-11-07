// 0% and deferred-interest countdown. For each deal (a 0% balance transfer, a "no interest if
// paid in full" store card, a 0% purchase card or a pay-over-time plan) it works out the monthly
// payment that clears it in time, what's left at the end if you keep paying what you pay now,
// and what that would cost.
//
// The big trap is deferred interest: if any of the balance is left when the promo ends, the
// lender charges the interest for the WHOLE promo period, back to the purchase date. A true 0%
// offer only charges interest on what's left, from then on.
import { isDay, addDays, daysBetween, monthsBetween } from './dates.js';

export const KINDS = {
  deferred: 'Deferred interest ("no interest if paid in full")',
  zero: 'True 0% APR (balance transfer or 0% card)',
  bnpl: 'Pay-over-time plan with fixed payments',
};
export const REMIND_BEFORE = [60, 30, 7];

export class LimitError extends Error {}

const round = (n) => Math.round(n * 100) / 100;
const ceilCents = (n) => Math.ceil(Math.round(n * 1000) / 10) / 100;
const num = (v) => { const n = Number(v); return v === '' || v == null || !Number.isFinite(n) || n < 0 ? NaN : n; };
const newId = () => Math.random().toString(36).slice(2, 10);

export const emptyDeals = () => ({ deals: [] });
export function loadDeals(raw) {
  try { const d = JSON.parse(raw); if (d && Array.isArray(d.deals)) return d; } catch { /* fall through */ }
  return emptyDeals();
}

/** Check a form's values. Returns a clean deal or throws an Error with a message for the person. */
export function makeDeal({ name, kind = 'deferred', balance, purchase = '', apr, start = '', end, payment = '' }) {
  name = String(name || '').trim() || 'My deal';
  if (!KINDS[kind]) kind = 'deferred';
  const bal = num(balance);
  if (Number.isNaN(bal)) throw new Error('Enter the balance you still owe.');
  if (!isDay(end)) throw new Error('Enter the date the promo ends (it\'s on your statement).');
  const rate = kind === 'bnpl' && (apr === '' || apr == null) ? 0 : num(apr);
  if (Number.isNaN(rate) || rate > 99) throw new Error('Enter the APR that applies after the promo (on your statement, often 25% to 30%).');
  let orig = purchase === '' || purchase == null ? bal : num(purchase);
  if (Number.isNaN(orig)) throw new Error('The original amount doesn\'t look right.');
  orig = Math.max(orig, bal);
  if (start && !isDay(start)) throw new Error('The start date doesn\'t look right.');
  if (start && start >= end) throw new Error('The start date must be before the end date.');
  const pay = payment === '' || payment == null ? 0 : num(payment);
  if (Number.isNaN(pay)) throw new Error('The monthly payment doesn\'t look right.');
  return { name: name.slice(0, 60), kind, balance: round(bal), purchase: round(orig), apr: rate, start: start || '', end, payment: round(pay) };
}

export function addDeal(data, values, { max = Infinity } = {}) {
  const deal = makeDeal(values);
  if (data.deals.length >= max) throw new LimitError(`The free plan saves ${max} deal. Pro saves every deal and adds calendar reminders.`);
  const saved = { id: newId(), ...deal };
  data.deals.push(saved);
  return saved;
}

export function removeDeal(data, id) { data.deals = data.deals.filter((d) => d.id !== id); }

/** Payments left: one per month from now until the end date (at least 1 while it's still running). */
export function paymentsLeft(today, end) {
  if (end < today) return 0;
  return Math.max(1, monthsBetween(today, end));
}

/**
 * Rough deferred-interest charge if the deal isn't cleared: interest at the APR on each month's
 * balance from the start date to the end date. Past months assume the balance fell evenly from
 * the original amount to today's balance; future months assume `payment` a month.
 * It's an estimate: lenders use the average daily balance, so the real figure differs a little.
 */
export function deferredInterest(deal, today, payment = deal.payment) {
  const start = deal.start || today;
  const past = Math.max(0, monthsBetween(start, today));
  const ahead = paymentsLeft(today, deal.end);
  const monthly = deal.apr / 100 / 12;
  let interest = 0;
  for (let i = 0; i < past; i++) {
    const bal = deal.purchase - ((deal.purchase - deal.balance) * i) / Math.max(1, past);
    interest += bal * monthly;
  }
  let bal = deal.balance;
  for (let i = 0; i < ahead; i++) { interest += bal * monthly; bal = Math.max(0, bal - payment); }
  return round(interest);
}

export function analyzeDeal(deal, today) {
  const left = paymentsLeft(today, deal.end);
  const days = daysBetween(today, deal.end);
  const ended = days < 0;
  const toClear = left ? ceilCents(deal.balance / left) : deal.balance;
  // Pay it off a month early: statements and payments take time to post.
  const safe = left > 1 ? ceilCents(deal.balance / (left - 1)) : toClear;
  const leftover = round(Math.max(0, deal.balance - deal.payment * left));
  const onTrack = deal.balance === 0 || leftover === 0;
  let cost = 0;
  let costNote = '';
  if (deal.balance > 0 && !onTrack) {
    if (deal.kind === 'deferred') {
      cost = deferredInterest(deal, today);
      costNote = `If $${leftover.toFixed(2)} is still owed when the promo ends, expect roughly $${cost.toFixed(2)} of back-dated interest added at once.`;
    } else if (deal.kind === 'zero') {
      cost = round(leftover * deal.apr / 100 / 12);
      costNote = `$${leftover.toFixed(2)} would be left, and it starts costing about $${cost.toFixed(2)} a month in interest.`;
    } else {
      costNote = `$${leftover.toFixed(2)} would be left. Check the plan's terms for late fees.`;
    }
  }
  const worstCase = deal.kind === 'deferred' && deal.balance > 0 ? deferredInterest(deal, today, 0) : 0;
  let status = 'ok';
  if (deal.balance === 0) status = 'paid';
  else if (ended) status = 'ended';
  else if (!onTrack) status = 'behind';
  else if (days <= 60) status = 'soon';
  return { ...deal, days, paymentsLeft: left, toClear, safe, leftover, onTrack, cost, costNote, worstCase, status };
}

export function summarizeDeals(data, today) {
  const rows = data.deals.map((d) => analyzeDeal(d, today)).sort((a, b) => a.end.localeCompare(b.end));
  return {
    rows,
    owed: round(rows.reduce((s, r) => s + r.balance, 0)),
    atRisk: round(rows.filter((r) => r.status === 'behind' || r.status === 'ended').reduce((s, r) => s + r.cost, 0)),
    behind: rows.filter((r) => r.status === 'behind').length,
    neededMonthly: round(rows.filter((r) => r.paymentsLeft > 0).reduce((s, r) => s + r.safe, 0)),
  };
}

/** Calendar reminders 60, 30 and 7 days before each promo ends (only the ones still ahead). */
export function dealReminders(data, today) {
  const out = [];
  for (const d of data.deals) {
    if (d.balance <= 0 || d.end < today) continue;
    for (const before of REMIND_BEFORE) {
      const date = addDays(d.end, -before);
      if (date < today) continue;
      out.push({
        uid: `deal-${d.id}-${before}`,
        date,
        title: `${d.name}: 0% ends in ${before} days (${d.end})`,
        description: d.kind === 'deferred'
          ? `Deferred interest: pay the full balance before ${d.end} or interest is charged back to the purchase date. Check your current balance and pay it off.`
          : `Your promo rate ends on ${d.end}. Check the balance and pay off what you can before then.`,
      });
    }
  }
  return out.sort((a, b) => a.date.localeCompare(b.date));
}
