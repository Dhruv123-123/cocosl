// Mileage math for gig drivers (Uber, Lyft, DoorDash, Uber Eats, Instacart...). Pure functions, no DOM.
// Uses the IRS standard mileage rate for business use of a car and the same federal model as lib/tax.js.
// 2026 has two business rates: 72.5 cents a mile for Jan 1 - Jun 30 (Notice 2026-10) and 76 cents for Jul 1 - Dec 31
// (Announcement 2026-11, a rare mid-year increase). Re-check every December at irs.gov/tax-professionals/standard-mileage-rates.
import { federalTax } from './tax.js';

export const RATE_JAN_JUN = 0.725;
export const RATE_JUL_DEC = 0.76;
export const MILEAGE_RATE = RATE_JUL_DEC; // the current rate, for "100 more miles" style estimates

// The 2026 deduction: miles before July at 72.5¢, miles from July 1 at 76¢. Without a split, half are assumed to be
// from July (the calculator says so and lets you enter your own).
export function mileageDeduction(miles, milesFromJuly = null) {
  const total = Math.max(0, Number.isFinite(+miles) ? +miles : 0);
  const h2 = milesFromJuly === null || milesFromJuly === '' || !Number.isFinite(+milesFromJuly)
    ? total / 2 : Math.min(total, Math.max(0, +milesFromJuly));
  return (total - h2) * RATE_JAN_JUN + h2 * RATE_JUL_DEC;
}

const n = (x) => (Number.isFinite(+x) ? Math.max(0, +x) : 0);

// What logging your miles is worth, and how much of each payout to keep for tax.
//   earnings      everything the apps paid you this year, tips included (tips are income)
//   miles         business miles you logged: online and driving to a pickup, on a delivery or trip,
//                 and between jobs. Not your commute to a regular workplace or personal errands.
//   appMiles      optional: the miles the app reports (often only on-trip miles), to show the gap
//   otherCosts    other business costs: the business share of your phone, bags, parking and tolls on jobs
//   deliveries    optional: trips or deliveries this year, for the per-delivery set-aside
export function mileagePlan({
  earnings = 0, miles = 0, milesFromJuly = null, appMiles = 0, otherCosts = 0, deliveries = 0,
  status = 'single', w2Wages = 0, stateRate = 0,
} = {}) {
  earnings = n(earnings); miles = n(miles); appMiles = n(appMiles); otherCosts = n(otherCosts);
  deliveries = Math.round(n(deliveries)); w2Wages = n(w2Wages);
  const state = Math.min(n(stateRate), 0.2);
  const deduction = mileageDeduction(miles, milesFromJuly);
  const blended = miles > 0 ? deduction / miles : MILEAGE_RATE;
  const profitNoMiles = Math.max(0, earnings - otherCosts);
  const profit = Math.max(0, earnings - otherCosts - deduction);
  const taxOn = (p) => federalTax({ profit: p, status, w2Wages }).freelanceShare + p * state;
  const taxNoMiles = taxOn(profitNoMiles);
  const tax = taxOn(profit);
  const fed = federalTax({ profit, status, w2Wages });
  // The deduction the app's own figure would give you, so the gap shows what an own log adds.
  const appTax = appMiles > 0 ? taxOn(Math.max(0, earnings - otherCosts - appMiles * blended)) : null;
  // Rough value of 100 more logged miles at your current tax rates.
  const per100 = Math.max(0, tax - taxOn(Math.max(0, profit - 100 * blended)));
  return {
    rate: blended, earnings, miles, deduction, otherCosts, profit, profitNoMiles,
    seTax: fed.seTax, federal: fed.freelanceShare, state: profit * state,
    tax, taxNoMiles, saving: Math.max(0, taxNoMiles - tax),
    appSaving: appTax === null ? null : Math.max(0, appTax - tax),
    per100,
    setAsideRate: earnings > 0 ? tax / earnings : 0,
    perDelivery: deliveries > 0 ? tax / deliveries : null,
    quarterly: tax / 4,
    owesEstimates: tax >= 1000 && w2Wages === 0,
  };
}
