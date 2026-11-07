// "Rate My Budget": a 0-100 budget health score with plain-English next moves.
// Benchmarks are common rules of thumb (20% saved, 3+ months of cushion, housing near 30% of take-home,
// debt payments under ~15%), shown as guides, not rules.

const clamp = (x, lo = 0, hi = 1) => Math.max(lo, Math.min(hi, x));
const r0 = (n) => Math.round(n);
const money = (n) => `$${Math.round(n).toLocaleString('en-US')}`;

export const FIELDS = ['income', 'housing', 'essentials', 'debtPayments', 'wants', 'saving', 'cushion', 'cardDebt', 'match'];

export function rateBudget(input) {
  const v = {};
  for (const k of FIELDS) {
    if (k === 'match') continue;
    const n = Number(input[k] ?? 0);
    if (!Number.isFinite(n) || n < 0) throw new RangeError(`${k} must be zero or more`);
    v[k] = n;
  }
  v.match = ['yes', 'no', 'na'].includes(input.match) ? input.match : 'na';
  if (v.income <= 0) throw new RangeError('Enter your monthly take-home pay');

  const spend = v.housing + v.essentials + v.debtPayments + v.wants + v.saving;
  const leftover = v.income - spend;
  const core = v.housing + v.essentials + v.debtPayments; // what a cushion has to cover
  const savingsRate = v.saving / v.income;
  const housingRatio = v.housing / v.income;
  const debtRatio = v.debtPayments / v.income;
  const cushionMonths = core > 0 ? v.cushion / core : v.cushion > 0 ? 12 : 0;

  const parts = [
    { id: 'saving', label: 'Saving rate', max: 25, score: 25 * clamp(savingsRate / 0.2), value: `${r0(savingsRate * 100)}% of pay`, guide: '20% or more' },
    { id: 'cushion', label: 'Emergency cushion', max: 20, score: 20 * clamp(cushionMonths / 3), value: `${cushionMonths.toFixed(1)} months`, guide: '3 to 6 months' },
    { id: 'housing', label: 'Housing cost', max: 15, score: 15 * clamp((0.5 - housingRatio) / 0.2), value: `${r0(housingRatio * 100)}% of pay`, guide: 'about 30% or less' },
    { id: 'debt', label: 'Debt payments', max: 15, score: 15 * clamp((0.36 - debtRatio) / 0.21) * (v.cardDebt > 0 ? 0.7 : 1), value: `${r0(debtRatio * 100)}% of pay${v.cardDebt > 0 ? `, ${money(v.cardDebt)} on cards` : ''}`, guide: 'under 15%, no card balance' },
    { id: 'plan', label: 'Every dollar planned', max: 15, score: leftover < 0 ? 0 : 15 * clamp(1 - Math.max(0, leftover / v.income - 0.05) / 0.15), value: leftover < 0 ? `${money(-leftover)} over` : `${money(leftover)} unplanned`, guide: 'within 5% of pay' },
    { id: 'match', label: 'Free employer money', max: 10, score: v.match === 'no' ? 0 : 10, value: v.match === 'yes' ? 'getting the full match' : v.match === 'no' ? 'missing some match' : 'no match offered', guide: 'take the full match' },
  ];
  for (const p of parts) p.score = Math.round(p.score * 10) / 10;
  const score = r0(parts.reduce((s, p) => s + p.score, 0));
  const grade = score >= 85 ? 'A' : score >= 70 ? 'B' : score >= 55 ? 'C' : score >= 40 ? 'D' : 'F';

  // Next moves, most urgent first. Each says exactly what to do, with a number in it.
  const moves = [];
  if (leftover < 0) moves.push({ id: 'overspend', weight: 100, text: `You're planning ${money(-leftover)} more than you take home each month. Trim wants first: that gap is going on a card or coming out of savings.` });
  if (v.match === 'no') moves.push({ id: 'match', weight: 90, text: 'Raise your 401(k) contribution to get the full employer match. It is an instant, guaranteed return on that money.' });
  if (cushionMonths < 1) moves.push({ id: 'starter', weight: 85, text: `Build a starter cushion of ${money(Math.min(1000, Math.max(core, 500)))} before anything else, so a surprise bill doesn't go on a card.` });
  if (v.cardDebt > 0) moves.push({ id: 'cards', weight: 80, text: `Attack the ${money(v.cardDebt)} on cards with every spare dollar, highest APR first. Card interest usually beats any return you'd get by investing instead.` });
  if (leftover > v.income * 0.05) moves.push({ id: 'assign', weight: 70, text: `${money(leftover)} a month has no job. Set up an automatic transfer on payday so it doesn't disappear.` });
  if (cushionMonths >= 1 && cushionMonths < 3) moves.push({ id: 'cushion', weight: 60, text: `Grow your cushion from ${cushionMonths.toFixed(1)} to 3 months (${money(core * 3)}). Keep it in an insured high-yield savings account.` });
  if (housingRatio > 0.35) moves.push({ id: 'housing', weight: 50, text: `Housing takes ${r0(housingRatio * 100)}% of your pay. At your next lease or renewal, look at a roommate, a cheaper unit, or negotiating the rent.` });
  if (savingsRate < 0.2 && leftover >= 0) {
    const target = Math.min(0.2, savingsRate + 0.05);
    moves.push({ id: 'saving', weight: 40, text: `Lift saving from ${r0(savingsRate * 100)}% to ${r0(target * 100)}% (${money(v.income * target)} a month). Raising it 1% every few months is easier than one big jump.` });
  }
  if (v.wants > v.income * 0.3) moves.push({ id: 'wants', weight: 30, text: `Wants are ${r0((v.wants / v.income) * 100)}% of pay. Pick the one or two you value least and cap them; keep the rest guilt-free.` });
  if (!moves.length) moves.push({ id: 'invest', weight: 10, text: 'Your basics are covered. Next: max out tax-advantaged accounts (401(k), IRA) and keep costs low with broad index funds.' });
  moves.sort((a, b) => b.weight - a.weight);

  return { score, grade, parts, moves: moves.slice(0, 3), leftover: r0(leftover), cushionMonths: Math.round(cushionMonths * 10) / 10, savingsRate };
}
