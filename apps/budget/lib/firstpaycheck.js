// "First paycheck" guide for new grads: W-4 choices, the 401(k) match, an emergency fund, a budget.
// Pure functions, no DOM, no API calls.
//
// Sources:
//   2026 401(k) employee limit $24,500: https://www.irs.gov/newsroom/401k-limit-increases-to-24500-for-2026-ira-limit-increases-to-7500
//   Form W-4 and the Tax Withholding Estimator: https://www.irs.gov/forms-pubs/about-form-w-4 and https://www.irs.gov/individuals/tax-withholding-estimator
//   Child tax credit, $2,200 per qualifying child for 2026 (Rev. Proc. 2025-32): https://www.irs.gov/credits-deductions/individuals/child-tax-credit

export const LIMIT_401K_2026 = 24500;
export const CHILD_CREDIT_2026 = 2200;
export const OTHER_DEPENDENT_CREDIT = 500;
export const W4_ESTIMATOR = 'https://www.irs.gov/individuals/tax-withholding-estimator';

export const STEPS = [
  { id: 'w4', title: 'Fill in your W-4' },
  { id: 'match', title: 'Get the full 401(k) match' },
  { id: 'cushion', title: 'Start an emergency fund' },
  { id: 'budget', title: 'Pick a way to budget' },
  { id: 'extras', title: 'The other first-job forms' },
];

// Things to do at a first job, beyond the four big steps. Each links to a tool or an explainer.
export const EXTRAS = [
  { id: 'health', text: 'Choose a health plan within your enrollment window (often 30 days). With a high-deductible plan, open the HSA too.' },
  { id: 'direct', text: 'Set up direct deposit, and split it so part goes straight to savings.' },
  { id: 'loans', text: 'Student loans? Your first payment usually comes 6 months after you graduate. Pick a plan before then.', link: '../money-calculators/student-loans/', label: 'Student loan chooser' },
  { id: 'card', text: 'Put every credit card on autopay for the full statement balance.' },
  { id: 'renters', text: "Get renter's insurance if you rent. It's often $15 to $20 a month." },
  { id: 'beneficiary', text: 'Name a beneficiary on your 401(k) and any life insurance through work.' },
];

const cents = (n) => Math.round(n * 100) / 100;
const num = (v, d = 0) => { const x = Number(String(v ?? '').replace(/[$,%\s]/g, '')); return Number.isFinite(x) && x >= 0 ? x : d; };

/**
 * What to put on the W-4, in plain words. answers: { jobs: 'one'|'two', married: 'no'|'yes'|'spouse-works',
 * kids (under 17), otherDeps, side: 'yes'|'no', sideIncome (yearly, $), bracket (%) }.
 */
export function w4Advice(answers = {}) {
  const kids = Math.round(num(answers.kids));
  const others = Math.round(num(answers.otherDeps));
  const married = answers.married === 'yes' || answers.married === 'spouse-works';
  const steps = [];
  steps.push({ step: 'Step 1', text: `Your name, address and Social Security number. Filing status: ${married ? '"Married filing jointly"' : '"Single or Married filing separately"'}${!married && kids ? ' (or "Head of household" if you pay more than half the cost of keeping up a home for your child)' : ''}.` });
  if (answers.jobs === 'two' || answers.married === 'spouse-works') {
    steps.push({ step: 'Step 2', text: 'You have more than one job, or your spouse works too. The most accurate choice is the IRS Tax Withholding Estimator. If the two jobs pay about the same, ticking the Step 2(c) box on both W-4s works well.', link: W4_ESTIMATOR });
  } else {
    steps.push({ step: 'Step 2', text: 'Skip it: you have one job and no working spouse.' });
  }
  const credit = kids * CHILD_CREDIT_2026 + others * OTHER_DEPENDENT_CREDIT;
  steps.push(credit
    ? { step: 'Step 3', text: `Enter ${dollars(credit)} (${kids ? `${kids} × ${dollars(CHILD_CREDIT_2026)} for children under 17` : ''}${kids && others ? ' plus ' : ''}${others ? `${others} × ${dollars(OTHER_DEPENDENT_CREDIT)} for other dependents` : ''}). Income limits apply.` }
    : { step: 'Step 3', text: 'Skip it: no dependents.' });
  const side = answers.side === 'yes' ? num(answers.sideIncome) : 0;
  if (side > 0) {
    const bracket = num(answers.bracket, 12);
    // Rough: income tax at your bracket plus self-employment tax (15.3% of 92.35%), spread over a year of paychecks.
    const extraYear = side * (bracket / 100 + 0.9235 * 0.153);
    steps.push({ step: 'Step 4(c)', text: `Side income of about ${dollars(side)} a year: ask for about ${dollars(extraYear / 26)} extra per paycheck (every two weeks), or pay quarterly estimated tax instead.`, extraYear: cents(extraYear) });
  } else {
    steps.push({ step: 'Step 4', text: 'Skip it unless you have other income, big deductions or want extra withheld.' });
  }
  steps.push({ step: 'Step 5', text: 'Sign and date it. Check your first two paychecks, and use the IRS estimator again if your pay or life changes.' });
  return { steps, simple: answers.jobs !== 'two' && answers.married !== 'spouse-works' && !credit && !side };
}

/**
 * The 401(k) contribution that gets the whole employer match.
 * matchPct: employer match rate (e.g. 50 for "50 cents per dollar"); upToPct: on contributions up to this % of salary.
 */
export function matchPlan({ salary, matchPct = 100, upToPct = 4, payPeriods = 26 } = {}) {
  const s = num(salary);
  const rate = num(matchPct, 100) / 100;
  const upTo = Math.min(num(upToPct, 4), 100) / 100;
  const periods = Math.max(1, Math.round(num(payPeriods, 26)));
  const youYear = Math.min(s * upTo, LIMIT_401K_2026);
  const employerYear = youYear * rate;
  return {
    contributePct: Math.round(upTo * 1000) / 10,
    youYear: cents(youYear), youPerPaycheck: cents(youYear / periods),
    freeMoneyYear: cents(employerYear), freeMoneyPerPaycheck: cents(employerYear / periods),
    instantReturn: rate, // e.g. 0.5 = a 50% return on every dollar you put in up to the cap
    capped: s * upTo > LIMIT_401K_2026,
  };
}

/** Emergency fund milestones from monthly essentials. */
export function cushionTargets(essentials) {
  const e = num(essentials);
  return [
    { key: 'starter', label: 'Starter fund', amount: Math.max(1000, cents(e * 0.5)) },
    { key: 'one', label: 'One month of essentials', amount: cents(e) },
    { key: 'three', label: 'Three months', amount: cents(e * 3) },
  ];
}

/** 50/30/20 split of monthly take-home pay, and pay-yourself-first. */
export function budgetSplits(takeHomeMonthly, savePct = 20) {
  const t = num(takeHomeMonthly);
  return {
    fiftyThirtyTwenty: { needs: cents(t * 0.5), wants: cents(t * 0.3), savings: cents(t * 0.2) },
    payYourselfFirst: { save: cents((t * num(savePct, 20)) / 100), spend: cents(t - (t * num(savePct, 20)) / 100) },
  };
}

function dollars(n) { return `$${Math.round(n).toLocaleString('en-US')}`; }
