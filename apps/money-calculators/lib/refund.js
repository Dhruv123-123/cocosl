// Federal tax refund estimator for tax year 2026 (the return filed in early 2027). Pure functions, no API calls.
// Standard deduction only (most filers); no itemizing, no EITC, no state tax. The page says so.
//
// Sources:
//   Brackets and standard deductions (single, joint, head of household), $1,650/$2,050 extra standard deduction
//   at 65+, child tax credit $2,200 with $1,700 refundable: Rev. Proc. 2025-32
//     https://www.irs.gov/pub/irs-drop/rp-25-32.pdf
//     https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2026-including-amendments-from-the-one-big-beautiful-bill
//   Child tax credit rules ($500 credit for other dependents; phase-out from $200,000, $400,000 joint, $50 per
//   $1,000; refundable part limited to 15% of earned income over $2,500):
//     https://www.irs.gov/credits-deductions/individuals/child-tax-credit
//   No tax on tips (up to $25,000), no tax on overtime (premium pay, up to $12,500 / $25,000 joint), the $6,000
//   senior deduction, their income thresholds, 2025-2028, not for married filing separately:
//     https://www.irs.gov/newsroom/working-families-tax-cuts-tax-deductions-for-working-americans-and-seniors
//   Phase-out rates are from the law itself (P.L. 119-21, secs. 70201, 70202, 70103), since the IRS pages give
//   only the thresholds: tips and overtime drop $100 for each $1,000 over; the senior deduction drops by 6% of
//   the income over. Recheck when the 2026 Schedule 1-A instructions come out.
import { STANDARD_DEDUCTION, BRACKETS } from './tax2026.js';

export const FILING = ['single', 'married', 'hoh'];
export const AGED_EXTRA = { single: 2050, hoh: 2050, married: 1650 };
export const CTC = { perChild: 2200, refundable: 1700, otherDependent: 500, phaseStart: { single: 200000, hoh: 200000, married: 400000 } };
export const TIPS = { max: 25000, phaseStart: { single: 150000, hoh: 150000, married: 300000 } };
export const OVERTIME = { max: { single: 12500, hoh: 12500, married: 25000 }, phaseStart: { single: 150000, hoh: 150000, married: 300000 } };
export const SENIOR = { perPerson: 6000, phaseStart: { single: 75000, hoh: 75000, married: 150000 }, rate: 0.06 };

const cents = (n) => Math.round(n * 100) / 100;
const num = (v, d = 0) => { const x = Number(v); return Number.isFinite(x) && x >= 0 ? x : d; };

export function incomeTax(taxable, filing) {
  let tax = 0;
  let lower = 0;
  for (const [upper, rate] of BRACKETS[filing]) {
    if (taxable <= lower) break;
    tax += (Math.min(taxable, upper) - lower) * rate;
    lower = upper;
  }
  return cents(tax);
}

const phaseTenPct = (amount, magi, start) => Math.max(0, amount - Math.ceil(Math.max(0, magi - start) / 1000) * 100);

export function estimateRefund(input) {
  const filing = FILING.includes(input.filing) ? input.filing : 'single';
  const wages = num(input.wages);
  const other = num(input.otherIncome);
  const withheld = num(input.withheld);
  const estimated = num(input.estimated);
  const kids = Math.min(20, Math.round(num(input.kids)));
  const otherDeps = Math.min(20, Math.round(num(input.otherDeps)));
  const seniors = Math.min(filing === 'married' ? 2 : 1, Math.round(num(input.seniors)));
  const agi = wages + other;
  const magi = agi;

  const standard = STANDARD_DEDUCTION[filing] + seniors * AGED_EXTRA[filing];
  const tipsDed = phaseTenPct(Math.min(num(input.tips), TIPS.max), magi, TIPS.phaseStart[filing]);
  const otDed = phaseTenPct(Math.min(num(input.overtime), OVERTIME.max[filing]), magi, OVERTIME.phaseStart[filing]);
  const seniorDed = seniors * Math.max(0, SENIOR.perPerson - SENIOR.rate * Math.max(0, magi - SENIOR.phaseStart[filing]));
  const taxable = Math.max(0, agi - standard - tipsDed - otDed - seniorDed);
  const tax = incomeTax(taxable, filing);

  // Child tax credit and credit for other dependents, phased out together.
  const fullCredit = kids * CTC.perChild + otherDeps * CTC.otherDependent;
  const credit = Math.max(0, fullCredit - Math.ceil(Math.max(0, magi - CTC.phaseStart[filing]) / 1000) * 50);
  const nonrefundable = Math.min(tax, credit);
  const childPart = Math.min(credit, kids * CTC.perChild);
  const unusedChild = Math.max(0, childPart - Math.min(tax, childPart));
  const refundableCredit = cents(Math.min(unusedChild, kids * CTC.refundable, 0.15 * Math.max(0, wages - 2500)));
  const owed = cents(tax - nonrefundable);
  const paid = cents(withheld + estimated);
  const refund = cents(paid + refundableCredit - owed);
  const marginal = (BRACKETS[filing].find(([upper]) => taxable <= upper) || [0, 0.37])[1];
  return {
    filing, agi: cents(agi), standard, tipsDed: cents(tipsDed), otDed: cents(otDed), seniorDed: cents(seniorDed), taxable: cents(taxable), tax,
    credit: cents(credit), nonrefundable: cents(nonrefundable), refundableCredit, owed, paid, refund,
    marginal, effective: agi ? owed / agi : 0,
    eitcMaybe: wages > 0 && agi < (kids ? 70000 : 27000), // rough flag only: the page points to the IRS EITC assistant
    bigRefund: refund > 1500, owesMuch: refund < -1000,
  };
}
