// Federal student loan repayment plans, as of November 2026. Pure functions, no DOM, no API calls.
// Rules are copied in by hand from Federal Student Aid. Check them every July (plan changes start July 1).
//
// Sources:
//   Repayment plan comparison (Federal Student Aid, Edfinancial servicer site on studentaid.gov):
//     https://edfinancial.studentaid.gov/income-driven-repaymentinformation-center/repayment-plan-comparison
//   Repayment Assistance Plan (RAP): AGI table, $50 per dependent, $10 minimum, interest subsidy,
//     $50 matching principal payment, forgiveness after 360 qualifying payments:
//     https://edfinancial.studentaid.gov/income-driven-repaymentinformation-center/rap
//   Income-Based Repayment (IBR): 10% or 15% of income above 150% of the poverty guideline, never more
//     than the 10-year Standard payment, forgiveness after 20 or 25 years:
//     https://edfinancial.studentaid.gov/income-driven-repaymentinformation-center/ibr
//   SAVE ended March 2026; PAYE and ICR end no later than July 1, 2028; loans from July 1, 2026 get
//     Tiered Standard or RAP: https://studentaid.gov/articles/save/
//   Tiered Standard terms by balance (10/15/20/25 years): Massachusetts Student Loan Ombudsman summary of
//     the 2025 law (H.R. 1, sec. 82001): https://www.mass.gov/info-details/the-new-tiered-standard-plan
//   2026 HHS poverty guidelines: https://aspe.hhs.gov/sites/default/files/documents/b1bfa16b20ae9b89d525bc35de7c1643/detailed-guidelines-2026.pdf
//
// Simplifications (shown on the page): one combined balance at one rate; income grows by a fixed % a year;
// the poverty guideline stays at its 2026 level; Graduated is modeled as payments rising 15% every 2 years
// (servicers set the real schedule); IBR unpaid interest is added to the balance; PAYE and ICR (closing by
// July 2028) and PSLF are not modeled. Forgiven balances may be taxable.

export const POVERTY_2026 = { contiguous: [15960, 5680], alaska: [19950, 7100], hawaii: [18360, 6530] };
export const RAP_MIN = 10;
export const RAP_PER_DEPENDENT = 50;
export const EXTENDED_MIN_BALANCE = 30000;

const cents = (n) => Math.round(n * 100) / 100;
const num = (v, d = 0) => { const x = Number(v); return Number.isFinite(x) && x >= 0 ? x : d; };

export function povertyLine(householdSize, region = 'contiguous') {
  const [first, extra] = POVERTY_2026[region] || POVERTY_2026.contiguous;
  return first + extra * (Math.max(1, Math.round(householdSize)) - 1);
}

/** RAP yearly base payment from AGI: $120 up to $10,000, then 1% of all AGI per $10,000 band, up to 10%. */
export function rapBase(agi) {
  if (agi <= 10000) return 120;
  const pct = Math.min(10, Math.ceil(agi / 10000) - 1);
  return agi * (pct / 100);
}

export function rapMonthly(agi, dependents = 0) {
  return cents(Math.max(RAP_MIN, rapBase(agi) / 12 - RAP_PER_DEPENDENT * dependents));
}

export function ibrMonthly(agi, householdSize, { newBorrower = true, region = 'contiguous', cap = Infinity } = {}) {
  const discretionary = Math.max(0, agi - 1.5 * povertyLine(householdSize, region));
  return cents(Math.min(cap, (discretionary * (newBorrower ? 0.10 : 0.15)) / 12));
}

export function amortized(balance, apr, months) {
  const r = apr / 100 / 12;
  return r === 0 ? balance / months : (balance * r) / (1 - (1 + r) ** -months);
}

/** Tiered Standard term in years, from the total principal when repayment starts. */
export function tieredYears(balance) {
  return balance < 25000 ? 10 : balance < 50000 ? 15 : balance < 100000 ? 20 : 25;
}

// Month-by-month run. payFor(month, balance, agi) returns the scheduled payment.
// rule: 'normal' (unpaid interest is added) or 'rap' (unpaid interest waived, $50 principal match).
function simulate({ balance, apr, months, payFor, rule = 'normal', agi, growth = 0 }) {
  const r = apr / 100 / 12;
  let bal = balance;
  let paid = 0;
  let first = null;
  let last = 0;
  let income = agi;
  let m = 0;
  for (; m < months && bal > 0.005; m++) {
    if (m && m % 12 === 0) income *= 1 + growth / 100;
    const interest = bal * r;
    let pay = Math.min(payFor(m, bal, income), bal + interest);
    if (first === null) first = cents(pay);
    last = pay;
    paid += pay;
    if (rule === 'rap') {
      const toPrincipal = Math.max(0, pay - interest);
      const match = Math.max(0, Math.min(pay, 50) - toPrincipal);
      bal = Math.max(0, bal - toPrincipal - match);
    } else {
      bal = bal + interest - pay;
    }
  }
  const forgiven = bal > 0.005 ? cents(bal) : 0;
  return { first: first ?? 0, last: cents(last), months: m, paid: cents(paid), forgiven };
}

/**
 * Compare the plans a borrower can use.
 * input: { balance, rate (%), agi, household (people), dependents, region, cohort: 'before2026'|'after2026',
 *          newBorrower2014: 'yes'|'no', growth (% a year) }
 */
export function comparePlans(input) {
  const balance = num(input.balance);
  const apr = Math.min(num(input.rate), 20);
  const agi = num(input.agi);
  const household = Math.max(1, Math.round(num(input.household, 1)));
  const dependents = Math.min(household - 1, Math.round(num(input.dependents)));
  const region = POVERTY_2026[input.region] ? input.region : 'contiguous';
  const growth = Math.min(num(input.growth), 15);
  const after = input.cohort === 'after2026';
  const newBorrower = input.newBorrower2014 !== 'no';
  if (!balance) throw new RangeError('Enter your loan balance');
  const ten = amortized(balance, apr, 120);
  const plans = [];
  const add = (key, years, opts) => plans.push({ key, years, ...simulate({ balance, apr, agi, growth, ...opts }), ...(opts.extra || {}) });

  if (after) {
    const y = tieredYears(balance);
    const pay = Math.max(50, amortized(balance, apr, y * 12));
    add('tiered', y, { months: y * 12, payFor: () => pay });
  } else {
    add('standard', 10, { months: 120, payFor: () => Math.max(50, ten) });
    // Graduated: 5 steps of 2 years, each 15% higher; the first payment is set so it pays off in 10 years.
    const g = 1.15;
    let pv = 0;
    const r = apr / 100 / 12;
    for (let k = 0; k < 5; k++) for (let j = 0; j < 24; j++) pv += g ** k / (1 + r) ** (k * 24 + j + 1);
    const p0 = balance / pv;
    add('graduated', 10, { months: 120, payFor: (m) => p0 * g ** Math.floor(m / 24) });
    if (balance > EXTENDED_MIN_BALANCE) {
      const ext = amortized(balance, apr, 300);
      add('extended', 25, { months: 300, payFor: () => ext });
    }
    const ibrYears = newBorrower ? 20 : 25;
    add('ibr', ibrYears, { months: ibrYears * 12, payFor: (m, b, income) => ibrMonthly(income, household, { newBorrower, region, cap: ten }) });
  }
  add('rap', 30, { months: 360, rule: 'rap', payFor: (m, b, income) => rapMonthly(income, dependents) });

  const paidOff = plans.filter((p) => !p.forgiven);
  const cheapest = plans.reduce((a, b) => (b.paid < a.paid ? b : a));
  const lowestPayment = plans.reduce((a, b) => (b.first < a.first ? b : a));
  const fastest = (paidOff.length ? paidOff : plans).reduce((a, b) => (b.months < a.months ? b : a));
  return {
    plans, cheapest: cheapest.key, lowestPayment: lowestPayment.key, fastest: fastest.key,
    tenYear: cents(ten), poverty: povertyLine(household, region), cohort: after ? 'after2026' : 'before2026',
  };
}
