// "What's your money personality?" quiz. Pure data and scoring, no DOM.
// Five original types. Each answer adds a point to one type; the top score wins, the runner-up is shown too.
// Not a psychological test: a fun way into the free tools that fit how you handle money.

export const TYPES = {
  planner: {
    name: 'The Planner', emoji: '🗂️',
    blurb: 'You like to know where every dollar is going before the month starts. Spreadsheets don\'t scare you, and surprises do.',
    strength: 'You rarely get caught short, and your savings grow because you plan for them.',
    blindSpot: 'Plans can turn rigid. If one slip-up makes you drop the whole budget, build in a "no questions asked" fun line.',
    tools: [['Rate my budget', 'budget/rate.html'], ['Annual money checkup', 'budget/checkup.html'], ['Roth vs Traditional', 'money-calculators/roth-vs-traditional/']],
  },
  enjoyer: {
    name: 'The Enjoyer', emoji: '🎉',
    blurb: 'Money is for living. You\'re generous, you say yes to plans, and you\'d rather have the memory than the balance.',
    strength: 'You actually enjoy your money, and the people around you feel it.',
    blindSpot: 'Small yeses add up, and "buy now, pay later" makes them easy. Decide what matters most, then spend freely on that.',
    tools: [['Can I afford this?', 'budget/afford.html'], ['Holiday spending planner', 'budget/holiday.html'], ['The 20-Minute Budget', 'budget/']],
  },
  avoider: {
    name: 'The Avoider', emoji: '🙈',
    blurb: 'Money stuff feels like a chore, so it waits. Bills get paid, mostly, but you\'d rather not look at the balance.',
    strength: 'You don\'t obsess over money, and you\'re often happy with less.',
    blindSpot: 'Not looking costs money: late fees, forgotten subscriptions, interest. Ten minutes a week fixes most of it.',
    tools: [['Bill calendar', 'budget/bills.html'], ['Annual money checkup', 'budget/checkup.html'], ['Credit card minimum payment', 'money-calculators/credit-card-minimum/']],
  },
  worrier: {
    name: 'The Worrier', emoji: '😬',
    blurb: 'You check your balance a lot and still feel there\'s never enough. A surprise bill can ruin your week.',
    strength: 'You take money seriously and you\'re careful with it.',
    blindSpot: 'Worry isn\'t a plan. An emergency fund with a clear target and a debt plan with an end date turn the worry into numbers.',
    tools: [['Emergency fund calculator', 'money-calculators/emergency-fund/'], ['Debt payoff: avalanche vs snowball', 'money-calculators/debt-payoff/'], ['Scam checker', 'scam-checker/']],
  },
  builder: {
    name: 'The Builder', emoji: '🛠️',
    blurb: 'You think about money as something to grow. Side income, investing, raises: you like to make the pile bigger.',
    strength: 'You find ways to earn more, which beats cutting back every time.',
    blindSpot: 'Growth plans can skip the boring basics: taxes on side income, fees and a cushion for when a bet doesn\'t work.',
    tools: [['Side hustle profit calculator', 'freelance-invoices/side-hustle.html'], ['Tax refund estimator', 'money-calculators/tax-refund/'], ['401(k) fee checker', 'money-calculators/401k-fees/']],
  },
};
export const ORDER = ['planner', 'enjoyer', 'avoider', 'worrier', 'builder'];

// Each option: [text, type]. Options are shown in a shuffled-looking but fixed order per question.
export const QUESTIONS = [
  { q: 'Payday lands. What happens first?', o: [
    ['I move money to savings and bills before I touch it', 'planner'], ['Dinner out. I earned it', 'enjoyer'], ['Nothing special. I don\'t really check', 'avoider'],
    ['I check that it covers everything coming up', 'worrier'], ['Some goes to investing or my side project', 'builder']] },
  { q: 'Your bank app shows a notification. You…', o: [
    ['Read it later, maybe', 'avoider'], ['Open it right away, a little nervous', 'worrier'], ['Check it against my budget', 'planner'],
    ['See if it\'s a payment from a client', 'builder'], ['Hope it isn\'t a reminder about that order', 'enjoyer']] },
  { q: 'A friend suggests a weekend trip next month.', o: [
    ['I\'m in! I\'ll figure out the money', 'enjoyer'], ['I see if it fits the budget first', 'planner'], ['I want to, but I\'ll worry about the cost', 'worrier'],
    ['I could pick up extra work to pay for it', 'builder'], ['Sure, and I won\'t look at what it costs', 'avoider']] },
  { q: 'How do you feel about your credit card statement?', o: [
    ['I pay it in full every month, on a schedule', 'planner'], ['I\'d rather not open it', 'avoider'], ['It stresses me out even when it\'s fine', 'worrier'],
    ['It\'s higher than I\'d like, but life is short', 'enjoyer'], ['I use it for rewards and business costs', 'builder']] },
  { q: 'You get an unexpected $1,000. You…', o: [
    ['Put it toward a goal I already have', 'planner'], ['Treat myself and the people I love', 'enjoyer'], ['Leave it in checking and forget it', 'avoider'],
    ['Save every bit of it, just in case', 'worrier'], ['Invest it or put it into something that earns', 'builder']] },
  { q: 'Which sounds most like you?', o: [
    ['"I have a spreadsheet for that"', 'planner'], ['"You only live once"', 'enjoyer'], ['"I\'ll deal with it later"', 'avoider'],
    ['"What if something goes wrong?"', 'worrier'], ['"How could this make money?"', 'builder']] },
  { q: 'Tax season is coming. Your plan?', o: [
    ['Already sorted, documents in a folder', 'planner'], ['Wait for the refund and spend it', 'enjoyer'], ['File close to the deadline', 'avoider'],
    ['Dread it and double-check everything', 'worrier'], ['Track my deductions from side income', 'builder']] },
  { q: 'What would help you most right now?', o: [
    ['A cleaner system, with less to track', 'planner'], ['Spending on what I love without guilt', 'enjoyer'], ['Not having to think about it', 'avoider'],
    ['Feeling safe if something goes wrong', 'worrier'], ['More income', 'builder']] },
];

export function score(answers) {
  const s = Object.fromEntries(ORDER.map((t) => [t, 0]));
  let answered = 0;
  QUESTIONS.forEach((q, i) => {
    const a = answers[i];
    if (a === undefined || a === null || !q.o[a]) return;
    s[q.o[a][1]] += 1;
    answered += 1;
  });
  const ranked = [...ORDER].sort((a, b) => s[b] - s[a] || ORDER.indexOf(a) - ORDER.indexOf(b));
  const [top, second] = ranked;
  return {
    answered, total: QUESTIONS.length, complete: answered === QUESTIONS.length, scores: s,
    top, second: s[second] > 0 ? second : null,
    pct: answered ? Math.round((s[top] / answered) * 100) : 0,
  };
}

export const isType = (t) => Object.hasOwn(TYPES, t);
