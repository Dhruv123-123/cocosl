// Side hustle profit: what a gig driver, reseller or Etsy seller really keeps per hour after platform fees,
// costs, driving and taxes. Pure functions, no DOM, no API calls. All figures are a week of work.
//
// Sources (check each January and July):
//   IRS business standard mileage rate: 72.5 cents Jan-Jun 2026, 76 cents from July 1, 2026
//     (Notice 2026-10, Announcement 2026-11): https://www.irs.gov/newsroom/irs-sets-2026-business-standard-mileage-rate-at-725-cents-per-mile-up-25-cents
//     and https://www.journalofaccountancy.com/news/2026/jul/irs-raises-standard-mileage-rates-for-remainder-of-2026/
//   Self-employment tax: 15.3% (12.4% Social Security up to the wage base, 2.9% Medicare) on 92.35% of net
//     profit, owed once net earnings reach $400: https://www.irs.gov/businesses/small-businesses-self-employed/self-employment-tax-social-security-and-medicare-taxes
//   2026 Social Security wage base $184,500: https://www.ssa.gov/oact/cola/cbb.html
//   Qualified business income deduction (20%), made permanent in 2025: https://www.irs.gov/newsroom/qualified-business-income-deduction
//   Etsy (US): $0.20 listing, 6.5% transaction fee on item + shipping, 3% + $0.25 payment processing:
//     https://www.etsy.com/legal/fees/ (checked against a July 2026 summary). eBay and Poshmark presets are
//     typical rates only; categories and promotions change them, so the page says to check.

export const MILEAGE_RATE = 0.76; // IRS business rate per mile from July 1, 2026
export const SS_WAGE_BASE = 184500;
export const SE_FACTOR = 0.9235;
export const QBI = 0.2;

export const KINDS = {
  driver: { label: 'Rideshare or delivery driver', feePct: 0, perOrder: 0, perListing: 0, gross: 600, hours: 25, miles: 400, orders: 0, listings: 0, goods: 0, shipping: 0, other: 15 },
  etsy: { label: 'Etsy seller', feePct: 9.5, perOrder: 0.25, perListing: 0.2, gross: 500, hours: 15, miles: 10, orders: 15, listings: 10, goods: 120, shipping: 70, other: 10 },
  ebay: { label: 'eBay reseller', feePct: 13.6, perOrder: 0.4, perListing: 0, gross: 500, hours: 15, miles: 40, orders: 12, listings: 0, goods: 160, shipping: 60, other: 5 },
  poshmark: { label: 'Poshmark reseller', feePct: 20, perOrder: 0, perListing: 0, gross: 400, hours: 12, miles: 30, orders: 10, listings: 0, goods: 120, shipping: 0, other: 5 },
  other: { label: 'Something else', feePct: 0, perOrder: 0, perListing: 0, gross: 400, hours: 10, miles: 0, orders: 0, listings: 0, goods: 0, shipping: 0, other: 0 },
};

export const BRACKETS = [0, 10, 12, 22, 24, 32, 35, 37];

const cents = (n) => Math.round(n * 100) / 100;
const num = (v, d = 0) => { const x = Number(String(v ?? '').replace(/[$,%\s]/g, '')); return Number.isFinite(x) && x >= 0 ? x : d; };

export function normalize(input = {}) {
  const kind = KINDS[input.kind] ? input.kind : 'driver';
  const p = KINDS[kind];
  const pick = (k, d = p[k]) => (input[k] === undefined || input[k] === '' ? d : num(input[k], d));
  return {
    kind,
    gross: pick('gross'), hours: pick('hours'), miles: pick('miles'), carCost: pick('carCost', MILEAGE_RATE),
    orders: Math.round(pick('orders')), listings: Math.round(pick('listings')), feePct: Math.min(pick('feePct'), 60), perOrder: pick('perOrder'), perListing: pick('perListing'),
    goods: pick('goods'), shipping: pick('shipping'), other: pick('other'),
    weeks: Math.max(1, Math.min(52, Math.round(pick('weeks', 48)))),
    bracket: input.bracket !== undefined && input.bracket !== '' && BRACKETS.includes(Number(input.bracket)) ? Number(input.bracket) : 12,
    stateRate: Math.min(pick('stateRate', 0), 15),
  };
}

/** Self-employment tax on a year's net profit. */
export function seTax(yearProfit, wageBase = SS_WAGE_BASE) {
  const base = Math.max(0, yearProfit) * SE_FACTOR;
  if (base < 400) return 0;
  return cents(Math.min(base, wageBase) * 0.124 + base * 0.029);
}

export function profit(raw) {
  const v = normalize(raw);
  const fees = cents(v.gross * (v.feePct / 100) + v.orders * v.perOrder + v.listings * v.perListing);
  const car = cents(v.miles * v.carCost); // what driving really costs you
  const mileageDeduction = cents(v.miles * MILEAGE_RATE); // what the IRS lets you deduct instead of car costs
  const costs = cents(v.goods + v.shipping + v.other);
  const cashProfit = cents(v.gross - fees - costs - car); // before tax
  const taxableWeek = Math.max(0, v.gross - fees - costs - mileageDeduction);
  const yearTaxable = taxableWeek * v.weeks;
  const se = seTax(yearTaxable);
  const incomeBase = Math.max(0, yearTaxable - se / 2) * (1 - QBI);
  const incomeTax = cents(incomeBase * (v.bracket / 100));
  const stateTax = cents(Math.max(0, yearTaxable - se / 2) * (v.stateRate / 100));
  const taxYear = cents(se + incomeTax + stateTax);
  const taxWeek = cents(taxYear / v.weeks);
  const keepWeek = cents(cashProfit - taxWeek);
  const hourly = v.hours ? cents(cashProfit / v.hours) : null;
  const hourlyAfterTax = v.hours ? cents(keepWeek / v.hours) : null;
  const tips = [];
  if (v.hours && hourlyAfterTax !== null && hourlyAfterTax < 7.25) tips.push(`After costs and taxes you keep ${hourlyAfterTax < 0 ? 'nothing' : `about $${hourlyAfterTax.toFixed(2)}`} an hour, under the federal minimum wage of $7.25.`);
  if (v.kind === 'driver' && v.miles && v.hours && v.miles / v.hours > 12) tips.push('Long miles per hour eat your profit. Turning down low-paying long trips often raises your real hourly rate.');
  if (v.miles) tips.push(`Log every business mile. At ${Math.round(MILEAGE_RATE * 1000) / 10} cents a mile, this week's ${v.miles} miles are a ${dollars(mileageDeduction)} tax deduction.`);
  if (taxWeek > 0) tips.push(`Set aside about ${dollars(taxWeek)} a week (${Math.round((taxWeek / Math.max(1, cashProfit)) * 100)}% of your profit) for taxes, and pay quarterly estimates if you'll owe $1,000 or more for the year.`);
  if (v.kind === 'etsy' && v.listings) tips.push('Listing fees renew every 4 months or when an item sells; renewing slow sellers adds up.');
  return {
    input: v, fees, car, mileageDeduction, costs, cashProfit, taxWeek, keepWeek, hourly, hourlyAfterTax,
    year: { gross: cents(v.gross * v.weeks), keep: cents(keepWeek * v.weeks), se, incomeTax, stateTax, tax: taxYear, taxable: cents(yearTaxable) },
    keepPerDollar: v.gross ? keepWeek / v.gross : 0,
    tips,
  };
}

function dollars(n) { return `$${n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`; }
