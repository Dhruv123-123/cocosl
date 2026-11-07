// The deduction finder: yes/no questions mapped to the Schedule C (and nearby) deductions they unlock.
// Pure data + functions, no DOM. Figures are 2026 federal; re-check every January with lib/tax.js.
import { federalTax } from './tax.js';

const IRS = 'irs.gov';
export const ITEMS = [
  { id: 'home-office', q: 'Do you use part of your home regularly and only for work?', name: 'Home office',
    rule: 'Simplified: $5 a square foot, up to 300 sq ft ($1,500). Or the regular method: the office share of rent or mortgage interest, utilities and insurance (Form 8829). The space must be used exclusively for business.', where: 'Schedule C, line 30', source: `${IRS}/businesses/small-businesses-self-employed/home-office-deduction` },
  { id: 'car', q: 'Do you drive to clients, job sites or business errands (not a commute to a regular workplace)?', name: 'Business mileage',
    rule: '72.5¢ a business mile for 2026, or the business share of actual car costs. Needs a log: date, miles, purpose. Parking and tolls on business trips are extra.', where: 'Schedule C, line 9', source: `${IRS}/tax-professionals/standard-mileage-rates` },
  { id: 'phone', q: 'Do you use your phone for work?', name: 'Phone (business share)',
    rule: 'The business-use percentage of your phone plan and the phone itself. Write down how you worked out the percentage.', where: 'Schedule C, line 25 or 27a', source: `${IRS}/publications/p334` },
  { id: 'internet', q: 'Do you use your home internet for work?', name: 'Internet (business share)',
    rule: 'The business-use share of your internet bill. Separate from the home office deduction, so you can take it even without a qualifying office.', where: 'Schedule C, line 25', source: `${IRS}/publications/p334` },
  { id: 'software', q: 'Do you pay for software, apps or online subscriptions you use for work?', name: 'Software and subscriptions',
    rule: 'Fully deductible when used for the business: design tools, accounting software, cloud storage, scheduling apps, stock assets.', where: 'Schedule C, line 18 or 27a', source: `${IRS}/publications/p334` },
  { id: 'equipment', q: 'Did you buy a computer, camera, tools or office furniture for work?', name: 'Equipment',
    rule: 'Items up to $2,500 each can usually be expensed in the year you start using them (de minimis election); bigger items through Section 179 or bonus depreciation. Business-use share only.', where: 'Schedule C, line 13 or 22', source: `${IRS}/publications/p946` },
  { id: 'fees', q: 'Do clients pay you through PayPal, Stripe, Upwork, Fiverr or another platform that takes a cut?', name: 'Payment and platform fees',
    rule: 'Processing fees and marketplace commissions are business expenses. A 1099-K shows the gross, so report the gross and deduct the fees.', where: 'Schedule C, line 10 or 27a', source: `${IRS}/businesses/understanding-your-form-1099-k` },
  { id: 'health', q: 'Do you pay for your own health insurance, and weren\'t eligible for an employer plan (yours or a spouse\'s)?', name: 'Self-employed health insurance',
    rule: 'Premiums for you, your spouse and dependents, up to your business profit. Lowers income tax, not self-employment tax.', where: 'Schedule 1 (Form 7206)', source: `${IRS}/forms-pubs/about-form-7206` },
  { id: 'retirement', q: 'Do you contribute to, or want to open, a SEP-IRA, Solo 401(k) or traditional IRA?', name: 'Retirement contributions',
    rule: 'A SEP-IRA allows roughly 20% of net self-employment earnings and can be opened and funded until your filing deadline. A traditional IRA can be funded until April 15. Lowers income tax.', where: 'Schedule 1', source: `${IRS}/retirement-plans/plan-sponsor/simplified-employee-pension-plan-sep` },
  { id: 'hsa', q: 'Do you have an HSA-eligible (high-deductible) health plan?', name: 'HSA contributions',
    rule: '2026 limits: $4,400 self-only, $8,750 family (+$1,000 at 55+). Contributions for 2026 can be made until April 15, 2027.', where: 'Schedule 1 (Form 8889)', source: `${IRS}/publications/p969` },
  { id: 'learning', q: 'Did you pay for courses, books or conferences that build skills for the work you already do?', name: 'Education and training',
    rule: 'Deductible if it maintains or improves skills for your current business. Not if it qualifies you for a new trade.', where: 'Schedule C, line 27a', source: `${IRS}/publications/p334` },
  { id: 'contractors', q: 'Did you pay other freelancers or contractors to help with client work?', name: 'Contract labor',
    rule: 'Deductible. If you paid one person $2,000 or more in 2026 for services, you may need to send them a 1099-NEC by February 1, 2027.', where: 'Schedule C, line 11', source: `${IRS}/forms-pubs/about-form-1099-nec` },
  { id: 'travel', q: 'Did you travel overnight away from home for business?', name: 'Business travel',
    rule: 'Flights, lodging and transport for the business part of the trip. Meals while traveling are 50% deductible. Keep the receipts and a note of the business purpose.', where: 'Schedule C, lines 24a and 24b', source: `${IRS}/publications/p463` },
  { id: 'prep', q: 'Did you pay for tax preparation, bookkeeping or a lawyer for the business?', name: 'Professional fees',
    rule: 'The business part (for example the Schedule C portion of a tax preparer\'s fee) is deductible on Schedule C.', where: 'Schedule C, line 17', source: `${IRS}/publications/p334` },
  { id: 'startup', q: 'Did you start freelancing this year and spend money before your first client?', name: 'Startup costs',
    rule: 'Up to $5,000 of startup costs can be deducted in the first year (less if they total over $50,000), the rest over 15 years.', where: 'Schedule C, line 27a', source: `${IRS}/publications/p334` },
  { id: 'insurance', q: 'Do you pay for business insurance, such as liability or errors and omissions?', name: 'Business insurance',
    rule: 'Premiums for business insurance are deductible. (Health insurance goes in its own deduction above.)', where: 'Schedule C, line 15', source: `${IRS}/publications/p334` },
  { id: 'coworking', q: 'Do you rent a desk, studio or coworking membership?', name: 'Rent for business space',
    rule: 'Deductible. Note that renting an outside space can make a home office harder to claim, because home has to be your main place of business.', where: 'Schedule C, line 20b', source: `${IRS}/publications/p334` },
  { id: 'marketing', q: 'Do you pay for a website, domain, ads or business cards?', name: 'Advertising and website',
    rule: 'Deductible: hosting, domains, portfolio sites, ads, printed materials.', where: 'Schedule C, line 8', source: `${IRS}/publications/p334` },
];

// Everyone with self-employment income gets these, no question needed.
export const AUTOMATIC = [
  { name: 'Half of self-employment tax', rule: 'Half of your SE tax comes off your income for income-tax purposes. Software does it for you.', where: 'Schedule 1 (Schedule SE)' },
  { name: 'Qualified business income (QBI) deduction', rule: 'Generally 20% of business profit (capped at 20% of taxable income), below about $200,000 of taxable income single.', where: 'Form 1040 (Form 8995)' },
];

export function findDeductions(answers = {}) {
  return ITEMS.filter((it) => answers[it.id] === true);
}

// Rough federal saving per $100 of extra deduction at a given profit: income tax + SE tax effect.
// schedule: 'C' lowers profit (income tax + SE tax); '1' is an adjustment to income (income tax only).
export function savingPer100(profit = 0, status = 'single', schedule = 'C') {
  profit = Number.isFinite(+profit) ? Math.max(0, +profit) : 0;
  if (profit < 100) return 0;
  const base = federalTax({ profit, status }).total;
  return base - (schedule === '1' ? federalTax({ profit, status, aboveLine: 100 }) : federalTax({ profit: profit - 100, status })).total;
}

export const scheduleOf = (it) => (/^Schedule 1/.test(it.where) ? '1' : 'C');
