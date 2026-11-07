// US federal payroll and income tax figures for tax year 2026. Update every October.
// Sources:
//   IRS release on 2026 inflation adjustments (Rev. Proc. 2025-32):
//     https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2026-including-amendments-from-the-one-big-beautiful-bill
//   SSA 2026 contribution and benefit base ($184,500): https://www.ssa.gov/oact/cola/cbb.html
//   Additional Medicare Tax thresholds (not indexed): https://www.irs.gov/taxtopics/tc560
export const TAX_YEAR = 2026;

export const STANDARD_DEDUCTION = { single: 16100, married: 32200 };

// [upper bound of the bracket, rate]
export const BRACKETS = {
  single: [[12400, 0.10], [50400, 0.12], [105700, 0.22], [201775, 0.24], [256225, 0.32], [640600, 0.35], [Infinity, 0.37]],
  married: [[24800, 0.10], [100800, 0.12], [211400, 0.22], [403550, 0.24], [512450, 0.32], [768700, 0.35], [Infinity, 0.37]],
};

export const SOCIAL_SECURITY = { rate: 0.062, wageBase: 184500 };
export const MEDICARE = { rate: 0.0145, additionalRate: 0.009, additionalThreshold: { single: 200000, married: 250000 } };

// States with no tax on wages (as of 2026).
export const NO_WAGE_TAX_STATES = ['Alaska', 'Florida', 'Nevada', 'New Hampshire', 'South Dakota', 'Tennessee', 'Texas', 'Washington', 'Wyoming'];
