// Annual money checkup: 20 questions, a score out of 100, scores by area, and the fixes that matter most,
// each linked to the free tool that helps. Pure functions, no DOM.

export const AREAS = { budget: 'Spending and bills', saving: 'Savings', debt: 'Debt', credit: 'Credit and net worth', retirement: 'Retirement', protection: 'Insurance and taxes', safety: 'Scam safety' };

const yn = (yes, partly, no) => [[yes, 2], [partly, 1], [no, 0]];

// Each: id, area, question, options [label, points 0-2], weight (how much a low score matters), fix, link.
export const QUESTIONS = [
  { id: 'track', area: 'budget', q: 'Do you know where your money went last month?', o: yn('Yes, to the dollar', 'Roughly', 'Not really'), w: 3, fix: 'Give every dollar a job for one month.', link: './', tool: '20-Minute Budget' },
  { id: 'surplus', area: 'budget', q: 'Do you spend less than you earn most months?', o: yn('Yes, every month', 'Some months', 'No, I fall short'), w: 3, fix: 'Score your budget and find the three moves that free up the most money.', link: 'rate.html', tool: 'Rate my budget' },
  { id: 'subs', area: 'budget', q: 'Have you checked your subscriptions in the last 6 months?', o: yn('Yes', 'Some of them', 'No'), w: 1, fix: 'Paste a bank statement and list every recurring charge.', link: 'subscriptions.html', tool: 'Subscription audit' },
  { id: 'bills', area: 'budget', q: 'Have you asked for a lower rate on internet, phone or insurance this year?', o: yn('Yes', 'Once or twice', 'Never'), w: 1, fix: 'Call with a script and track what each call saves.', link: 'bills.html', tool: 'Bill negotiation tracker' },
  { id: 'cushion', area: 'saving', q: 'How many months of essentials could your savings cover?', o: [['3 months or more', 2], ['1 to 3 months', 1], ['Less than 1 month', 0]], w: 3, fix: 'Set a target and a monthly amount to get to one month, then three.', link: '../money-calculators/emergency-fund/', tool: 'Emergency fund calculator' },
  { id: 'hysa', area: 'saving', q: 'Is your emergency money in a high-yield savings account?', o: yn('Yes', 'Part of it', 'No, it earns little or nothing'), w: 1, fix: 'See what a higher APY earns on what you already have.', link: '../money-calculators/savings-interest/', tool: 'Savings interest calculator' },
  { id: 'auto', area: 'saving', q: 'Does money move to savings automatically each payday?', o: yn('Yes', 'Sometimes I move it by hand', 'No'), w: 2, fix: 'Split your direct deposit so savings happen first.', link: 'first-paycheck.html#step-cushion', tool: 'First paycheck guide' },
  { id: 'cards', area: 'debt', q: 'Your credit cards each month:', o: [['Paid in full', 2], ['Carrying a balance that is shrinking', 1], ['Carrying a balance that is growing', 0]], w: 3, fix: 'Make a payoff plan: avalanche or snowball, with a debt-free date.', link: '../money-calculators/debt-payoff/', tool: 'Debt payoff calculator' },
  { id: 'deals', area: 'debt', q: 'Any 0% or buy now, pay later deals running?', o: [['None', 2], ['Yes, with a plan to clear them in time', 2], ['Yes, and I\'m not sure when they end', 0]], w: 2, fix: 'Find the monthly payment that clears each deal before interest hits.', link: 'deals.html', tool: '0% deal countdown' },
  { id: 'loans', area: 'debt', q: 'Student loans on the best repayment plan for you?', o: [['No student loans', 2], ['Yes, checked this year', 2], ['Not sure', 0]], w: 2, fix: 'Compare every plan under the 2026 rules, including RAP.', link: '../money-calculators/student-loans/', tool: 'Student loan chooser' },
  { id: 'medical', area: 'debt', q: 'Medical bills or collections you\'re unsure about?', o: [['None', 2], ['Yes, and I\'m handling them', 1], ['Yes, and I\'ve been ignoring them', 0]], w: 2, fix: 'Ask for an itemized bill and check for errors before you pay.', link: '../medical-bills/', tool: 'Medical bill helper' },
  { id: 'reports', area: 'credit', q: 'Checked all three credit reports this year?', o: yn('Yes', 'One of them', 'No'), w: 2, fix: 'Pull your free reports and track any disputes.', link: 'disputes.html', tool: 'Credit dispute tracker' },
  { id: 'networth', area: 'credit', q: 'Do you know your net worth?', o: yn('Yes, I track it', 'Roughly', 'No idea'), w: 1, fix: 'Add up what you own and owe, and save a yearly snapshot.', link: 'networth.html', tool: 'Net worth snapshot' },
  { id: 'match', area: 'retirement', q: 'Getting your full employer 401(k) match?', o: [['Yes, or no match is offered', 2], ['Some of it', 1], ['No', 0]], w: 3, fix: 'Find the contribution that captures the whole match.', link: 'first-paycheck.html#step-match', tool: 'First paycheck guide' },
  { id: 'rate', area: 'retirement', q: 'Saving 10% to 15% of pay for retirement (including any match)?', o: yn('Yes', '5% to 10%', 'Less than 5%'), w: 2, fix: 'See what Roth versus traditional means for your future tax bill.', link: '../money-calculators/roth-vs-traditional/', tool: 'Roth vs Traditional' },
  { id: 'fees', area: 'retirement', q: 'Do you know what your retirement funds charge in fees?', o: yn('Yes, and they\'re low', 'Roughly', 'No'), w: 1, fix: 'See what your fund fees cost you over the years.', link: '../money-calculators/401k-fees/', tool: '401(k) fee checker' },
  { id: 'health', area: 'protection', q: 'Health insurance for everyone in your household?', o: yn('Yes', 'Some of us', 'No'), w: 3, fix: 'Check Healthcare.gov or your state marketplace; a job change or move opens a special enrollment period.', link: 'https://www.healthcare.gov/', tool: 'HealthCare.gov' },
  { id: 'cover', area: 'protection', q: 'Reviewed your renter\'s, home and car insurance this year?', o: yn('Yes', 'Some of it', 'No'), w: 1, fix: 'Shop your rates and use a call script to ask for a better price.', link: 'bills.html', tool: 'Bill negotiation tracker' },
  { id: 'taxes', area: 'protection', q: 'Last year\'s tax refund or bill:', o: [['Within a few hundred dollars', 2], ['A big refund', 1], ['I owed a lot', 0]], w: 1, fix: 'Check your take-home pay and W-4 so each paycheck is closer to right.', link: '../money-calculators/take-home-pay/', tool: 'Paycheck calculator' },
  { id: 'scams', area: 'safety', q: 'Does your family have a scam plan (a safe word, and verify before paying)?', o: yn('Yes', 'We\'ve talked about it', 'No'), w: 2, fix: 'Set a family safe word and the call-back rule in 10 minutes.', link: '../scam-checker/family/', tool: 'Family scam safety plan' },
];

export const MAX = QUESTIONS.length * 2;

export function grade(score) {
  return score >= 90 ? 'A' : score >= 80 ? 'B' : score >= 65 ? 'C' : score >= 50 ? 'D' : 'F';
}

/** answers: { [id]: optionIndex }. Unanswered questions are left out of the score. */
export function report(answers = {}) {
  const answered = QUESTIONS.filter((q) => Number.isInteger(answers[q.id]) && q.o[answers[q.id]]);
  const points = answered.reduce((t, q) => t + q.o[answers[q.id]][1], 0);
  const possible = answered.length * 2;
  const score = possible ? Math.round((points / possible) * 100) : 0;
  const areas = Object.entries(AREAS).map(([key, label]) => {
    const qs = answered.filter((q) => q.area === key);
    const p = qs.reduce((t, q) => t + q.o[answers[q.id]][1], 0);
    return { key, label, answered: qs.length, score: qs.length ? Math.round((p / (qs.length * 2)) * 100) : null };
  });
  // Fixes: anything short of full marks, biggest gap times weight first.
  const fixes = answered
    .map((q) => ({ q, gap: 2 - q.o[answers[q.id]][1] }))
    .filter((x) => x.gap > 0)
    .sort((a, b) => b.gap * b.q.w - a.gap * a.q.w || QUESTIONS.indexOf(a.q) - QUESTIONS.indexOf(b.q))
    .map(({ q, gap }) => ({ id: q.id, area: AREAS[q.area], fix: q.fix, link: q.link, tool: q.tool, urgent: gap === 2 && q.w >= 3 }));
  const strengths = answered.filter((q) => q.o[answers[q.id]][1] === 2).map((q) => q.id);
  return { score, grade: grade(score), answered: answered.length, total: QUESTIONS.length, complete: answered.length === QUESTIONS.length, areas, fixes, strengths };
}
