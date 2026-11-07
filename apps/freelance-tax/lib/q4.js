// The January 15 payment (the 4th estimated payment for the tax year), worked out. Pure functions.
// Uses quarterlyPlan from lib/tax.js, so it agrees with the main calculator's Q4 view.
import { quarterlyPlan, dueDates, TAX_YEAR } from './tax.js';

export const Q4_DUE = dueDates(TAX_YEAR)[3].date;              // Jan 15 of the next year
export const FILE_BY = new Date(Date.UTC(TAX_YEAR + 1, 1, 1)); // Feb 1, 2027 (Jan 31 is a Sunday)

const n = (x) => (Number.isFinite(+x) ? Math.max(0, +x) : 0);

export function q4Plan(v = {}) {
  const p = quarterlyPlan({ ...v, nextQuarter: 4 });
  const paid = n(v.paidSoFar), withheld = n(v.withholding);
  // What should have been paid by Sep 15 (75% of the year's requirement), and how far behind that is.
  const dueBySep = p.needFromEstimates * 0.75;
  const behind = Math.max(0, dueBySep - paid);
  return {
    ...p,
    jan15: p.thisPayment,                                  // brings the year to 100% of the requirement
    q4Share: Math.max(0, p.thisPayment - behind),          // the part that is Q4's own quarter
    behind,                                                // catch-up for earlier quarters (penalty already running)
    fileEarlyInstead: Math.max(0, p.total - withheld - paid), // file and pay everything by Feb 1 instead of Jan 15
    afterJan15: Math.max(0, p.total - withheld - Math.max(paid, p.needFromEstimates)), // still due in April
  };
}
