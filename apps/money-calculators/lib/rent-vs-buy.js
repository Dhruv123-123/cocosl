// Rent vs buy: compares what you'd have after N years if you buy, versus renting and investing the difference.
// Pure functions, no DOM, no API calls. Every rate is an input the person can change.
//
// Method (the usual "invest the difference" comparison):
//   Buyer pays the down payment and closing costs up front, then each month the mortgage (principal and
//   interest), property tax, home insurance, HOA and upkeep.
//   Renter invests the same up-front cash instead, pays rent and renter's insurance, and each month whoever
//   pays less invests the difference at the investment return.
//   After N years: buyer has the home's value minus the loan left and selling costs, plus their investments;
//   renter has their investments.
// Not included: mortgage interest and property tax deductions (most people take the standard deduction),
// PMI, taxes on investment gains or on the home sale (most sellers owe none under the $250k/$500k exclusion).

const cents = (n) => Math.round(n * 100) / 100;
const num = (v, d = 0) => { const x = Number(v); return Number.isFinite(x) && x >= 0 ? x : d; };

export function mortgagePayment(loan, apr, years) {
  const r = apr / 100 / 12;
  const n = years * 12;
  if (!(loan > 0)) return 0;
  return r === 0 ? loan / n : (loan * r) / (1 - (1 + r) ** -n);
}

export function rentVsBuy(input) {
  const price = num(input.price);
  if (!price) throw new RangeError('Enter the home price');
  const downPct = Math.min(num(input.downPct, 20), 100);
  const rate = Math.min(num(input.mortgageRate, 6.5), 20);
  const termYears = Math.max(1, Math.min(40, Math.round(num(input.termYears, 30))));
  const taxPct = num(input.propertyTaxPct, 1.1);
  const insurance = num(input.insurance, 1800); // home insurance a year
  const hoa = num(input.hoa); // a month
  const upkeepPct = num(input.maintenancePct, 1); // of home value a year
  const closingPct = num(input.closingPct, 3);
  const sellingPct = num(input.sellingPct, 6);
  const appreciation = Math.min(num(input.appreciation, 3), 20);
  const rent0 = num(input.rent);
  const rentGrowth = Math.min(num(input.rentGrowth, 3), 20);
  const rentersIns = num(input.rentersInsurance, 15); // a month
  const ret = Math.min(num(input.investReturn, 6), 20);
  const years = Math.max(1, Math.min(40, Math.round(num(input.years, 7))));

  const down = price * (downPct / 100);
  const loan = price - down;
  const closing = price * (closingPct / 100);
  const pmt = mortgagePayment(loan, rate, termYears);
  const r = rate / 100 / 12;
  const g = (1 + ret / 100) ** (1 / 12) - 1;

  let balance = loan;
  let value = price;
  let rent = rent0;
  let buyerInv = 0;
  let renterInv = down + closing;
  const yearly = [];
  let firstMonth = null;
  let breakEven = null;
  // Run to at least 30 years so the break-even year shows even when you plan to stay less.
  const horizon = Math.max(years, 30);
  for (let m = 0; m < horizon * 12; m++) {
    if (m && m % 12 === 0) rent *= 1 + rentGrowth / 100;
    const interest = balance * r;
    const mortgage = balance > 0.005 ? Math.min(pmt, balance + interest) : 0;
    balance = Math.max(0, balance + interest - mortgage);
    const own = mortgage + (value * (taxPct / 100)) / 12 + insurance / 12 + hoa + (value * (upkeepPct / 100)) / 12;
    const renting = rent + rentersIns;
    if (!firstMonth) firstMonth = { own: cents(own), rent: cents(renting), mortgage: cents(mortgage), interest: cents(interest) };
    buyerInv *= 1 + g;
    renterInv *= 1 + g;
    if (own > renting) renterInv += own - renting; else buyerInv += renting - own;
    value *= (1 + appreciation / 100) ** (1 / 12);
    if ((m + 1) % 12 === 0) {
      const buyer = value * (1 - sellingPct / 100) - balance + buyerInv;
      const y = (m + 1) / 12;
      yearly.push({ year: y, buyer: cents(buyer), renter: cents(renterInv), homeValue: cents(value), loanLeft: cents(balance) });
      if (breakEven === null && buyer >= renterInv) breakEven = y;
    }
  }
  const end = yearly[years - 1];
  const diff = cents(end.buyer - end.renter);
  return {
    years, upfront: cents(down + closing), down: cents(down), closing: cents(closing), loan: cents(loan), payment: cents(pmt),
    firstMonth, yearly: yearly.slice(0, years), buyer: end.buyer, renter: end.renter, diff, winner: Math.abs(diff) < 1 ? 'tie' : diff > 0 ? 'buy' : 'rent',
    breakEven, pmiLikely: downPct < 20,
  };
}
