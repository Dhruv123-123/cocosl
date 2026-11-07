// "What should I charge?" freelance rate calculator (rate.html). Pure functions, no DOM, no API calls.
// Works backwards from the take-home pay you want: add self-employment and income tax, health insurance,
// retirement savings, business costs and a cushion for slow months, then divide by the hours you can bill.
//
// Tax uses the same simple model as the side hustle and set-aside tools (lib/sidehustle.js):
//   self-employment tax 15.3% on 92.35% of profit (12.4% only up to the 2026 Social Security wage base of $184,500),
//   income tax at your bracket on profit after half of self-employment tax, health insurance (the self-employed
//   health insurance deduction), pre-tax retirement savings and the 20% qualified business income deduction,
//   and state tax at a flat rate on the same base without the QBI deduction. An estimate, not a tax return.
import { seTax, BRACKETS, QBI } from './sidehustle.js';

const cents = (n) => Math.round(n * 100) / 100;
const num = (v, d = 0) => { const x = Number(String(v ?? '').replace(/[$,%\s]/g, '')); return Number.isFinite(x) && x >= 0 ? x : d; };

export const DEFAULTS = { takeHome: 60000, costs: 300, health: 450, retire: 300, weeksOff: 6, hours: 40, billable: 60, buffer: 10, bracket: 22, stateRate: 5, current: '' };

export function normalize(input = {}) {
  const pick = (k) => (input[k] === undefined || input[k] === '' ? DEFAULTS[k] : num(input[k], DEFAULTS[k]));
  return {
    takeHome: Math.min(pick('takeHome'), 5e6),
    costs: Math.min(pick('costs'), 1e6), health: Math.min(pick('health'), 1e5), retire: Math.min(pick('retire'), 1e5), // a month
    weeksOff: Math.min(Math.round(pick('weeksOff')), 40), hours: Math.min(Math.max(pick('hours'), 1), 80),
    billable: Math.min(Math.max(pick('billable'), 5), 100), buffer: Math.min(pick('buffer'), 50),
    bracket: BRACKETS.includes(Number(input.bracket)) ? Number(input.bracket) : DEFAULTS.bracket,
    stateRate: Math.min(pick('stateRate'), 15),
    current: input.current === undefined || input.current === '' ? null : num(input.current, null),
  };
}

/** Taxes on a year's profit (after business costs), given yearly health insurance and pre-tax retirement savings. */
export function taxes(profit, { health = 0, retire = 0, bracket = 22, stateRate = 0 } = {}) {
  const se = seTax(profit);
  const base = Math.max(0, profit - se / 2 - health - retire);
  const income = cents(base * (1 - QBI) * (bracket / 100));
  const state = cents(base * (stateRate / 100));
  return { se, income, state, total: cents(se + income + state) };
}

/** What you keep from a year's profit after taxes, health insurance and retirement savings. */
export function keepFromProfit(profit, o) {
  return cents(profit - taxes(profit, o).total - o.health - o.retire);
}

/** The profit that leaves exactly `takeHome` (bisection: keep rises with profit). */
export function profitFor(takeHome, o) {
  let lo = 0; let hi = Math.max(1000, (takeHome + o.health + o.retire) * 3);
  while (keepFromProfit(hi, o) < takeHome) hi *= 2;
  for (let i = 0; i < 60; i += 1) { const mid = (lo + hi) / 2; if (keepFromProfit(mid, o) < takeHome) lo = mid; else hi = mid; }
  return cents(hi);
}

export function rateFor(raw) {
  const v = normalize(raw);
  const o = { health: v.health * 12, retire: v.retire * 12, bracket: v.bracket, stateRate: v.stateRate };
  const workWeeks = 52 - v.weeksOff;
  const billableHours = Math.round(workWeeks * v.hours * (v.billable / 100));
  const profit = profitFor(v.takeHome, o);
  const tax = taxes(profit, o);
  const costsYear = cents(v.costs * 12);
  const beforeCushion = profit + costsYear;
  const revenue = cents(beforeCushion / (1 - v.buffer / 100));
  const hourly = billableHours ? cents(revenue / billableHours) : null;
  const quote = hourly === null ? null : Math.ceil(hourly / 5) * 5;
  const out = {
    input: v, workWeeks, billableHours, profit, tax, costsYear, revenue, hourly, quote,
    cushion: cents(revenue - beforeCushion),
    day: quote === null ? null : quote * 8,
    week: quote === null ? null : Math.round(quote * v.hours * (v.billable / 100)),
    monthRevenue: cents(revenue / 12),
    perDollar: revenue ? cents(v.takeHome / revenue) : 0,
    current: null,
  };
  if (v.current !== null && billableHours) {
    const rev = v.current * billableHours * (1 - v.buffer / 100);
    const p = Math.max(0, rev - costsYear);
    const keep = keepFromProfit(p, o);
    out.current = { rate: v.current, keep, gap: cents(keep - v.takeHome), raiseTo: quote };
  }
  return out;
}
