// "S corp or not?": compares a sole proprietor (Schedule C) with the same business taxed as an S corp that
// pays the owner a salary. 2026 federal figures from lib/tax.js. Built for single owners below the QBI
// threshold and the Additional Medicare Tax threshold; above them it flags the result instead of guessing.
// Sources: IRS "S corporations" and "S corporation compensation and medical insurance issues" pages,
// Publication 15 (FICA rates), Form 940 (FUTA), SSA 2026 wage base, Rev. Proc. 2025-32.
import { TABLES, federalTax, incomeTax } from './tax.js';

const n = (x) => (Number.isFinite(+x) ? Math.max(0, +x) : 0);
export const FICA = { ss: 0.062, medicare: 0.0145 };          // each side: employee and employer
export const FUTA = 0.006 * 7000;                               // $42 a year after the full state credit
export const LIMITS = { single: 200000, mfj: 250000 };          // Additional Medicare Tax thresholds (wages + SE income)

export function payroll(salary) {
  const half = Math.min(salary, TABLES.ssWageBase) * FICA.ss + salary * FICA.medicare;
  return { employee: half, employer: half, futa: salary > 0 ? Math.min(salary, 7000) * 0.006 : 0 };
}

export function scorpCompare({ profit = 0, salary = 0, costs = 2500, status = 'single' } = {}) {
  profit = n(profit); costs = n(costs); status = status === 'mfj' ? 'mfj' : 'single';
  salary = Math.min(n(salary), profit);
  const sole = federalTax({ profit, status });
  const soleKeep = profit - sole.total;

  const p = payroll(salary);
  // Business income left after the salary, the employer's payroll taxes and the extra running costs.
  const k1 = Math.max(0, profit - salary - p.employer - p.futa - costs);
  const agi = salary + k1;
  const std = TABLES.standardDeduction[status];
  const preQbi = Math.max(0, agi - std);
  const qbi = Math.min(TABLES.qbiRate * k1, TABLES.qbiRate * preQbi);
  const taxable = Math.max(0, preQbi - qbi);
  const incTax = incomeTax(taxable, status);
  const scorpTax = incTax + p.employee + p.employer + p.futa;
  const scorpKeep = profit - scorpTax - costs;

  return {
    profit, salary, costs,
    sole: { seTax: sole.seTax, incomeTax: sole.incomeTax, total: sole.total, keep: soleKeep },
    scorp: { employee: p.employee, employer: p.employer, futa: p.futa, k1, qbi, incomeTax: incTax, total: scorpTax, keep: scorpKeep },
    saving: scorpKeep - soleKeep,
    salaryShare: profit > 0 ? salary / profit : 0,
    outOfRange: profit > LIMITS[status],
  };
}

// Lowest profit (in $5,000 steps) at which the S corp comes out ahead, keeping salary at the same share of
// profit. null if it never does up to the range this tool covers.
export function breakEven({ salaryShare = 0.5, costs = 2500, status = 'single' } = {}) {
  for (let profit = 20000; profit <= LIMITS[status === 'mfj' ? 'mfj' : 'single']; profit += 5000) {
    if (scorpCompare({ profit, salary: profit * salaryShare, costs, status }).saving > 0) return profit;
  }
  return null;
}
