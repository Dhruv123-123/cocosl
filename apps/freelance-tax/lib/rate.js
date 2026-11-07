// Freelance rate calculator: work backwards from the take-home you want to the hourly rate you need.
// Same method as the Rate Calculator sheet in the $29 Rate & Contract Kit (launch/1099-money/products/
// build_kit.py), so the free page and the paid kit agree: $55,000 take-home → about $84,000 profit → $75/hour.
import { federalTax } from './tax.js';

const n = (x) => (Number.isFinite(+x) ? Math.max(0, +x) : 0);
export const MAX_PROFIT = 400000;

// Tax (federal + flat state) on a given profit.
const taxOn = (profit, status, stateRate) => federalTax({ profit, status }).total + profit * stateRate;

export function ratePlan({
  takeHome = 0, health = 0, retirement = 0, costs = 0, status = 'single', stateRate = 0,
  weeks = 48, hoursPerWeek = 25, dayHours = 6,
} = {}) {
  takeHome = n(takeHome); health = n(health); retirement = n(retirement); costs = n(costs);
  stateRate = Math.min(n(stateRate), 0.2); weeks = Math.min(n(weeks), 52); hoursPerWeek = Math.min(n(hoursPerWeek), 80);
  dayHours = n(dayHours) || 6; status = status === 'mfj' ? 'mfj' : 'single';
  const afterTax = takeHome + health + retirement;
  // Smallest profit, in $1,000 steps (as the kit's lookup table), that leaves `afterTax` once tax is paid.
  let profit = 0;
  while (profit < MAX_PROFIT && profit - taxOn(profit, status, stateRate) < afterTax) profit += 1000;
  const tooHigh = profit >= MAX_PROFIT && profit - taxOn(profit, status, stateRate) < afterTax;
  const fed = federalTax({ profit, status }).total;
  const state = profit * stateRate;
  const revenue = profit + costs;
  const hours = weeks * hoursPerWeek;
  const hourly = hours > 0 ? revenue / hours : 0;
  return {
    afterTax, profit, federal: fed, state, leftAfterTax: profit - fed - state, revenue, hours,
    hourly, day: hourly * dayHours, monthly: revenue / 12, weekly: weeks > 0 ? revenue / weeks : 0,
    setAside: profit > 0 ? (fed + state) / profit : 0, tooHigh,
    // The same take-home as a salary would need roughly this much less revenue: the "freelance premium".
    premium: takeHome > 0 ? revenue / takeHome : 0,
  };
}
