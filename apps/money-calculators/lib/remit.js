// Remittance cost: what sending money abroad really costs, from the numbers the person types in
// (amount, fee, the provider's rate or its markup, and the market rate). No provider data.
//
// Two costs hide in a transfer: the fee you see, and the exchange-rate markup you don't (the provider
// gives you fewer pesos per dollar than the market rate and keeps the difference).
// Since January 1, 2026 a 1% federal excise tax also applies to transfers paid with cash, a money order or a
// cashier's check (Internal Revenue Code section 4475); transfers paid from a bank account or with a US debit or
// credit card are exempt. The sender pays it and the provider collects it.

const r2 = (n) => Math.round((n + Number.EPSILON) * 100) / 100;
const r4 = (n) => Math.round(n * 10000) / 10000;
export const CASH_TAX = 0.01;

function num(v, label, { max = Infinity } = {}) {
  const n = Number(v);
  if (!Number.isFinite(n) || n < 0 || n > max) throw new Error(label);
  return n;
}

/**
 * amount: dollars you want to send. fee: flat fee ($). feePct: percentage fee (% of amount).
 * midRate: market rate, units of the other currency per dollar (0 = unknown). quotedRate: the provider's rate (0 = use markupPct).
 * markupPct: how far below the market rate the provider's rate is (%). feeMode: 'top' (paid on top) or 'inside' (taken from the amount).
 * pay: 'bank' (bank account or card, no tax) or 'cash' (cash, money order or cashier's check: 1% tax). perYear: transfers a year.
 * Messages are passed in so the Spanish page shows Spanish errors.
 */
export function remittanceCost(v, msg = {}) {
  const m = { amount: 'Enter the amount to send.', fee: 'Enter the fee (0 if none).', rate: 'Enter rates as numbers, like 18.45.', markup: 'Use a markup between 0% and 50%.', perYear: 'Use 0 to 52 transfers a year.', ...msg };
  const amount = num(v.amount, m.amount, { max: 1e7 });
  if (!amount) throw new Error(m.amount);
  const fee = num(v.fee ?? 0, m.fee, { max: 1e6 });
  const feePct = num(v.feePct ?? 0, m.fee, { max: 50 });
  const midRate = num(v.midRate ?? 0, m.rate, { max: 1e6 });
  const quotedRate = num(v.quotedRate ?? 0, m.rate, { max: 1e6 });
  let markupPct = num(v.markupPct ?? 0, m.markup, { max: 50 });
  const perYear = Math.round(num(v.perYear ?? 12, m.perYear, { max: 52 }));
  const inside = v.feeMode === 'inside';
  const cash = v.pay === 'cash';

  // A quoted rate wins over a typed markup when both rates are known.
  let rateFrom = 'markup';
  if (quotedRate > 0 && midRate > 0) { markupPct = Math.max(0, (1 - quotedRate / midRate) * 100); rateFrom = 'quoted'; }
  const fees = r2(fee + amount * feePct / 100);
  const converted = inside ? Math.max(0, r2(amount - fees)) : amount;       // dollars that get exchanged
  const tax = cash ? r2(amount * CASH_TAX) : 0;                           // on the amount transferred
  const paid = r2((inside ? amount : amount + fees) + tax);              // what leaves your pocket
  const markupCost = r2(converted * markupPct / 100);                     // dollars lost in the rate
  const totalCost = r2(fees + markupCost + tax);
  const effRate = midRate > 0 ? (rateFrom === 'quoted' ? quotedRate : midRate * (1 - markupPct / 100)) : 0;
  const arrives = effRate ? r2(converted * effRate) : null;               // in the other currency
  const arrivesUsd = r2(converted - markupCost);                          // what arrives, valued at the market rate
  // If every dollar you paid arrived at the market rate, with no fee, markup or tax.
  const ideal = midRate > 0 ? r2(paid * midRate) : null;
  return {
    amount, fees, converted, tax, paid, markupPct: r4(markupPct), markupCost, totalCost,
    costPct: paid ? r4(totalCost / paid * 100) : 0,
    midRate, effRate: r4(effRate), arrives, arrivesUsd, ideal, lost: ideal !== null && arrives !== null ? r2(ideal - arrives) : null,
    perYear, yearCost: r2(totalCost * perYear), rateFrom, inside, cash,
    // The UN target for remittance costs is 3% (Sustainable Development Goal 10.c).
    overTarget: paid ? totalCost / paid > 0.03 : false,
  };
}
