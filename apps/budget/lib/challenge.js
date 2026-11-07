// 52-week savings challenge. Pure functions, no DOM.
// Classic: save $1 in week 1, $2 in week 2 ... $52 in week 52 = $1,378. Every plan can be scaled to a goal.
import { addDays, daysBetween, isDay } from './dates.js';

export const WEEKS = 52;
export const CLASSIC_TOTAL = (WEEKS * (WEEKS + 1)) / 2; // 1,378
export const PLANS = ['classic', 'reverse', 'even', 'holiday'];
// classic: rising amounts. reverse: biggest weeks first, while motivation is high. even: the same every week.
// holiday: rising, but the last six weeks (often December) stay at the week-46 amount; the goal is spread over the rest.

const cents = (n) => Math.round(n * 100) / 100;

function shape(plan) {
  if (plan === 'reverse') return Array.from({ length: WEEKS }, (_, i) => WEEKS - i);
  if (plan === 'even') return Array(WEEKS).fill(1);
  if (plan === 'holiday') return Array.from({ length: WEEKS }, (_, i) => Math.min(i + 1, 46));
  return Array.from({ length: WEEKS }, (_, i) => i + 1);
}

/** amounts for each week so they add up to the goal exactly (the last biggest week absorbs rounding). */
export function amounts({ plan = 'classic', goal = CLASSIC_TOTAL, round = 'cents' } = {}) {
  const g = Math.max(0, Number(goal) || 0);
  const s = shape(PLANS.includes(plan) ? plan : 'classic');
  const total = s.reduce((t, x) => t + x, 0);
  const unit = round === 'dollars' ? (x) => Math.round(x) : cents;
  const out = s.map((x) => unit((x / total) * g));
  const diff = cents(g - out.reduce((t, x) => t + x, 0));
  // Put the rounding difference on the last of the biggest weeks so no week goes negative.
  const big = out.lastIndexOf(Math.max(...out));
  out[big] = cents(out[big] + diff);
  return out;
}

export function schedule({ plan = 'classic', goal = CLASSIC_TOTAL, start, round = 'cents' } = {}) {
  const a = amounts({ plan, goal, round });
  const s = isDay(start) ? start : null;
  let run = 0;
  return a.map((amount, i) => { run = cents(run + amount); return { week: i + 1, date: s ? addDays(s, i * 7) : null, amount, total: run }; });
}

/** done: { [week]: true }. Returns totals, how far ahead or behind the calendar, and the next week to fill. */
export function progress(rows, done = {}, today) {
  const saved = cents(rows.filter((r) => done[r.week]).reduce((t, r) => t + r.amount, 0));
  const goal = rows.length ? rows.at(-1).total : 0;
  const count = rows.filter((r) => done[r.week]).length;
  let dueWeek = null;
  let expected = null;
  if (rows[0]?.date && isDay(today)) {
    const elapsed = daysBetween(rows[0].date, today);
    dueWeek = elapsed < 0 ? 0 : Math.min(WEEKS, Math.floor(elapsed / 7) + 1);
    expected = cents(rows.filter((r) => r.week <= dueWeek).reduce((t, r) => t + r.amount, 0));
  }
  const next = rows.find((r) => !done[r.week]) || null;
  // Streak: consecutive weeks done, counting back from the latest week that's due (or the last week ticked).
  // The week in progress doesn't break a streak until it's over.
  const from = dueWeek === null ? Math.max(0, ...rows.filter((r) => done[r.week]).map((r) => r.week)) : done[dueWeek] ? dueWeek : dueWeek - 1;
  let streak = 0;
  for (let w = from; w >= 1 && done[w]; w--) streak++;
  return {
    saved, goal, left: cents(goal - saved), count, pct: goal ? Math.round((saved / goal) * 100) : 0,
    dueWeek, expected, gap: expected === null ? null : cents(saved - expected), next, streak, finished: count === rows.length && rows.length > 0,
  };
}

/** Catch up: if behind, how much a week for the rest of the year clears the gap. */
export function catchUp(rows, done, today) {
  const p = progress(rows, done, today);
  if (p.gap === null || p.gap >= 0) return null;
  const weeksLeft = Math.max(1, WEEKS - p.dueWeek + 1);
  return { behind: -p.gap, extraPerWeek: cents(-p.gap / weeksLeft), weeksLeft };
}

/** Pick a start date: the coming Monday (or today if it's Monday). */
export function nextMonday(today) {
  const d = new Date(`${today}T12:00:00Z`).getUTCDay();
  return addDays(today, (8 - d) % 7);
}
