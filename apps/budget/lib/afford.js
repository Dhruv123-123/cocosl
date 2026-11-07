// "Can I afford this?" for a big purchase (a car, a phone, anything): paying cash vs a loan vs buy now, pay later.
// Pure functions, no DOM. Used by afford.html / afford.js.
import { bnplCost } from './holiday.js';

const cents = (n) => Math.round(n * 100) / 100;
const usd = (x) => `$${cents(x).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
const n = (v, d = 0) => { const x = Number(String(v ?? '').replace(/[$,%\s]/g, '')); return Number.isFinite(x) && x >= 0 ? x : d; };

export const KINDS = { car: 'A car', phone: 'A phone', other: 'Something else' };
export const BNPL_TYPES = { pay4: 'Pay in 4 (every 2 weeks, no interest)', monthly: 'Monthly plan (Affirm-style)' };

// Starting numbers for each kind of purchase; the person changes them.
export const PRESETS = {
  car: { price: 28000, salesTax: 7, fees: 600, down: 3000, tradeIn: 0, extraMonthly: 250, loanApr: 7.5, loanMonths: 60, bnplType: 'monthly', bnplApr: 15.99, bnplMonths: 36 },
  phone: { price: 1099, salesTax: 7, fees: 0, down: 0, tradeIn: 0, extraMonthly: 0, loanApr: 0, loanMonths: 36, bnplType: 'pay4', bnplApr: 0, bnplMonths: 12 },
  other: { price: 1500, salesTax: 7, fees: 0, down: 0, tradeIn: 0, extraMonthly: 0, loanApr: 21.99, loanMonths: 12, bnplType: 'pay4', bnplApr: 0, bnplMonths: 12 },
};

/** Fixed monthly payment for a loan: amount at apr % over months. */
export function loanPayment(amount, apr, months) {
  if (!(amount > 0) || !(months > 0)) return 0;
  const r = apr / 100 / 12;
  return r === 0 ? amount / months : (amount * r) / (1 - (1 + r) ** -months);
}

export function normalize(input = {}) {
  const kind = KINDS[input.kind] ? input.kind : 'car';
  const p = PRESETS[kind];
  const pick = (k) => (input[k] === undefined || input[k] === '' ? p[k] : n(input[k], p[k]));
  return {
    kind,
    price: pick('price'), salesTax: Math.min(pick('salesTax'), 20), fees: pick('fees'), down: pick('down'), tradeIn: pick('tradeIn'),
    extraMonthly: pick('extraMonthly'),
    loanApr: Math.min(pick('loanApr'), 60), loanMonths: Math.max(1, Math.min(96, Math.round(pick('loanMonths')))),
    bnplType: BNPL_TYPES[input.bnplType] ? input.bnplType : p.bnplType,
    bnplApr: Math.min(pick('bnplApr'), 60), bnplMonths: Math.max(2, Math.min(60, Math.round(pick('bnplMonths')))),
    savings: n(input.savings), keepSaved: n(input.keepSaved),
    takeHome: n(input.takeHome), bills: n(input.bills),
  };
}

// How a new monthly cost compares to what's left after bills.
function fit(monthly, leftover) {
  if (monthly <= 0) return 'yes';
  if (leftover <= 0) return 'no';
  const share = monthly / leftover;
  return share <= 0.5 ? 'yes' : share <= 0.8 ? 'tight' : 'no';
}
const worst = (...v) => (v.includes('no') ? 'no' : v.includes('tight') ? 'tight' : 'yes');

/**
 * Compare the three ways to pay. today: 'YYYY-MM-DD' (for the BNPL schedule).
 * Returns { input, upfront, leftover, options: [{ key, cashNow, monthly, months, interest, total, verdict, reasons }], best, saveMonths, tips }.
 */
export function compare(raw, today) {
  const v = normalize(raw);
  const taxBase = Math.max(0, v.price - v.tradeIn); // most states tax the price after a trade-in
  const upfront = cents(taxBase * (1 + v.salesTax / 100) + v.fees);
  const leftover = cents(v.takeHome - v.bills);
  const spare = Math.max(0, v.savings - v.keepSaved); // savings you can spend without going under your floor
  const financed = cents(Math.max(0, upfront - v.down));
  const downOk = v.down <= spare;
  const options = [];

  // Cash
  {
    const reasons = [];
    let verdict = upfront <= spare ? 'yes' : upfront <= v.savings ? 'tight' : 'no';
    if (verdict === 'tight') reasons.push(`Paying cash leaves ${usd(v.savings - upfront)} in savings, under the ${usd(v.keepSaved)} you want to keep.`);
    if (verdict === 'no') reasons.push(`You'd need ${usd(upfront - spare)} more saved to pay cash and keep your cushion.`);
    const f = fit(v.extraMonthly, leftover);
    if (v.extraMonthly > 0 && f !== 'yes') reasons.push('The running costs alone are a big share of what you have left each month.');
    verdict = worst(verdict, f);
    options.push({ key: 'cash', cashNow: upfront, monthly: v.extraMonthly, months: 0, interest: 0, total: upfront, verdict, reasons });
  }

  // Loan
  {
    const pay = loanPayment(financed, v.loanApr, v.loanMonths);
    const total = cents(v.down + pay * v.loanMonths);
    const interest = cents(Math.max(0, total - v.down - financed));
    const monthly = cents(pay + v.extraMonthly);
    const reasons = [];
    let verdict = fit(monthly, leftover);
    if (verdict !== 'yes') reasons.push(`${usd(monthly)} a month would be ${verdict === 'no' ? 'more than you can spare from' : 'most of'} what's left after your bills (${usd(leftover)}).`);
    if (!downOk) { verdict = worst(verdict, 'tight'); reasons.push('The down payment would dip into the savings you want to keep.'); }
    if (v.kind === 'car') {
      if (v.loanMonths > 72) reasons.push('Loans over 6 years often leave you owing more than the car is worth for years.');
      else if (v.loanMonths > 48) reasons.push('The 20/4/10 rule of thumb suggests a loan of 4 years or less.');
      if (v.down < 0.2 * v.price) reasons.push('Putting less than 20% down makes it more likely you owe more than the car is worth at first.');
      if (v.takeHome > 0 && monthly / v.takeHome > 0.15) verdict = worst(verdict, 'tight');
      if (v.takeHome > 0 && monthly / v.takeHome > 0.15) reasons.push(`All-in car costs would be ${Math.round((monthly / v.takeHome) * 100)}% of your take-home pay; under about 15% is a common guide.`);
    }
    if (v.kind === 'phone' && v.loanApr > 0) reasons.push('Carriers and phone makers often offer 0% installment plans. Check those before paying interest on a phone.');
    options.push({ key: 'loan', cashNow: cents(v.down), monthly, payment: cents(pay), months: v.loanMonths, interest, total, verdict, reasons });
  }

  // Buy now, pay later
  {
    const c = bnplCost(financed, v.bnplType === 'pay4' ? { type: 'pay4' } : { type: 'monthly', apr: v.bnplApr, months: v.bnplMonths }, today);
    const pay4 = v.bnplType === 'pay4';
    // Pay in 4 lands two payments in most months: half the amount a month for two months.
    const monthly = cents((pay4 ? financed / 2 : c.each) + v.extraMonthly);
    const reasons = [];
    let verdict = fit(monthly, leftover);
    if (pay4 && financed > 1000) reasons.push('Pay-in-4 plans for large amounts are often declined or split; check the limit first.');
    if (pay4) reasons.push(`Four payments of about ${usd(financed / 4)} over 6 weeks, interest-free only if every payment goes through on time.`);
    else if (v.bnplApr > 0) reasons.push(`The plan adds ${usd(c.interest)} in interest.`);
    if (verdict !== 'yes') reasons.push(`About ${usd(monthly)} a month while you pay it off is ${verdict === 'no' ? 'more than' : 'most of'} what's left after bills.`);
    if (!downOk) verdict = worst(verdict, 'tight');
    options.push({ key: 'bnpl', cashNow: cents(v.down), monthly, payment: c.each, months: pay4 ? 2 : v.bnplMonths, interest: c.interest, total: cents(v.down + c.total), verdict, reasons, last: c.last });
  }

  // Best: the cheapest option that fits; cash wins ties.
  const fits = options.filter((o) => o.verdict === 'yes');
  const best = fits.length ? fits.reduce((a, b) => (b.total < a.total - 0.005 ? b : a)).key : null;

  // If nothing fits, how long saving what's left each month would take to pay cash.
  const gap = cents(Math.max(0, upfront - spare));
  const saveMonths = gap > 0 && leftover > 0 ? Math.ceil(gap / leftover) : gap > 0 ? null : 0;

  const tips = [];
  if (v.takeHome <= 0) tips.push('Add your monthly take-home pay and bills to see whether the payments fit.');
  if (best === null && saveMonths) tips.push(`Saving everything left after bills, you could pay cash in about ${saveMonths} month${saveMonths === 1 ? '' : 's'}.`);
  if (v.kind === 'car') tips.push('Get a loan quote from a credit union before the dealer, and compare on the total cost, not the monthly payment.');
  if (v.kind === 'phone') tips.push("Check your carrier's 0% device plan and trade-in credit, and whether the deal locks you into a pricier plan.");
  return { input: v, upfront, financed, leftover, options, best, saveMonths, tips };
}
