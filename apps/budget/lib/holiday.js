// Holiday spending planner (holiday.html). Pure functions, no DOM. Saved in the browser only.
// A gift list with a budget per person, a total cap, and the true cost of buy now, pay later.
import { isDay, addDays, addMonths } from './dates.js';

const uid = () => Math.random().toString(36).slice(2, 10);
const cents = (n) => Math.round(Number(n) * 100) / 100;
const num = (v) => Number(String(v ?? '').replace(/[$,%\s]/g, ''));
const clean = (s, max = 60) => String(s ?? '').trim().slice(0, max);

export const PAY = { cash: 'Cash or debit', card: 'Credit card (paid in full)', carry: 'Credit card (carrying a balance)', bnpl: 'Buy now, pay later' };
export const BNPL_TYPES = { pay4: 'Pay in 4 (every 2 weeks)', monthly: 'Monthly plan' };
export const EXTRA_KINDS = { travel: 'Travel', food: 'Food and hosting', decor: 'Decorations', cards: 'Cards and postage', wrap: 'Wrapping', other: 'Other' };

export const emptyPlan = () => ({ version: 1, cap: 0, people: [], gifts: [], extras: [] });

export function loadPlan(json) {
  try {
    const p = typeof json === 'string' ? JSON.parse(json) : json;
    if (!p || !Array.isArray(p.people) || !Array.isArray(p.gifts)) return emptyPlan();
    return { version: 1, cap: Math.max(0, Number(p.cap) || 0), people: p.people, gifts: p.gifts.filter((g) => g && g.price >= 0), extras: Array.isArray(p.extras) ? p.extras : [] };
  } catch { return emptyPlan(); }
}

export function setCap(plan, value) {
  const v = num(value);
  plan.cap = Number.isFinite(v) && v > 0 ? cents(v) : 0;
  return plan.cap;
}

export function addPerson(plan, { name, budget }) {
  const n = clean(name, 40);
  if (!n) throw new Error('Add a name.');
  const b = num(budget);
  const person = { id: uid(), name: n, budget: Number.isFinite(b) && b > 0 ? cents(b) : 0 };
  plan.people.push(person);
  return person;
}

export function removePerson(plan, id) {
  plan.people = plan.people.filter((p) => p.id !== id);
  plan.gifts = plan.gifts.filter((g) => g.personId !== id);
}

export function addGift(plan, v) {
  if (!plan.people.some((p) => p.id === v.personId)) throw new Error('Pick who the gift is for.');
  const item = clean(v.item, 80);
  if (!item) throw new Error('Name the gift.');
  const price = num(v.price);
  if (!(price >= 0)) throw new Error('Enter the price.');
  const pay = PAY[v.pay] ? v.pay : 'cash';
  const gift = { id: uid(), personId: v.personId, item, price: cents(price), bought: Boolean(v.bought), pay };
  if (pay === 'bnpl') {
    const type = BNPL_TYPES[v.bnplType] ? v.bnplType : 'pay4';
    const apr = type === 'monthly' ? num(v.apr) : 0;
    const months = type === 'monthly' ? Math.round(num(v.months)) : 0;
    if (type === 'monthly' && !(months >= 2 && months <= 60)) throw new Error('Enter how many monthly payments (2 to 60).');
    if (type === 'monthly' && !(apr >= 0 && apr <= 36)) throw new Error('Enter the plan\'s APR (0% to 36%).');
    gift.bnpl = { type, apr: type === 'monthly' ? cents(apr) : 0, months, start: isDay(v.start) ? v.start : '' };
  }
  plan.gifts.push(gift);
  return gift;
}

export function toggleBought(plan, id) {
  const g = plan.gifts.find((x) => x.id === id);
  if (!g) throw new Error('Gift not found.');
  g.bought = !g.bought;
  return g.bought;
}

export function removeGift(plan, id) { plan.gifts = plan.gifts.filter((g) => g.id !== id); }

export function addExtra(plan, { kind, amount, name }) {
  const a = num(amount);
  if (!(a > 0)) throw new Error('Enter an amount.');
  const k = EXTRA_KINDS[kind] ? kind : 'other';
  const extra = { id: uid(), kind: k, name: clean(name, 60) || EXTRA_KINDS[k], amount: cents(a) };
  plan.extras.push(extra);
  return extra;
}

export function removeExtra(plan, id) { plan.extras = plan.extras.filter((e) => e.id !== id); }

/**
 * Payment schedule and true cost of a BNPL purchase.
 * pay4: 4 equal payments, the first today and then every 2 weeks, 0% APR when paid on time.
 * monthly: an amortized loan at the plan's APR. Late fees are not included (they vary by provider).
 */
export function bnplCost(price, bnpl, start) {
  const day = isDay(bnpl?.start) ? bnpl.start : start;
  if (!bnpl || bnpl.type === 'pay4') {
    const each = Math.floor((price / 4) * 100) / 100;
    const payments = [0, 14, 28, 42].map((d, i) => ({ date: addDays(day, d), amount: i === 3 ? cents(price - each * 3) : each }));
    return { type: 'pay4', payments, interest: 0, total: cents(price), last: payments.at(-1).date, each };
  }
  const r = bnpl.apr / 100 / 12;
  const n = bnpl.months;
  const each = r === 0 ? cents(price / n) : cents((price * r) / (1 - (1 + r) ** -n));
  // Payments start a month after purchase; the last one absorbs rounding.
  const payments = Array.from({ length: n }, (_, i) => ({ date: addMonths(day, i + 1), amount: each }));
  let bal = price;
  let interest = 0;
  for (let i = 0; i < n; i++) { const int = bal * r; interest += int; bal = bal + int - each; }
  payments[n - 1].amount = cents(each + bal);
  interest = cents(interest);
  return { type: 'monthly', payments, interest, total: cents(price + interest), last: payments.at(-1).date, each };
}

/** Everything the page shows. today: 'YYYY-MM-DD'. */
export function summary(plan, today) {
  const people = plan.people.map((p) => {
    const gifts = plan.gifts.filter((g) => g.personId === p.id);
    const planned = cents(gifts.reduce((t, g) => t + g.price, 0));
    const bought = cents(gifts.filter((g) => g.bought).reduce((t, g) => t + g.price, 0));
    return { ...p, gifts: gifts.length, planned, bought, over: p.budget > 0 && planned > p.budget ? cents(planned - p.budget) : 0, left: p.budget > 0 ? cents(Math.max(0, p.budget - planned)) : null };
  });
  const giftsPlanned = cents(people.reduce((t, p) => t + p.planned, 0));
  // Budget for people with no gifts picked yet still counts toward the total.
  const reserved = cents(people.reduce((t, p) => t + (p.left || 0), 0));
  const extras = cents(plan.extras.reduce((t, e) => t + e.amount, 0));
  const bnplGifts = plan.gifts.filter((g) => g.pay === 'bnpl');
  const plans = bnplGifts.map((g) => ({ gift: g, ...bnplCost(g.price, g.bnpl, today) }));
  const interest = cents(plans.reduce((t, p) => t + p.interest, 0));
  const carry = cents(plan.gifts.filter((g) => g.pay === 'carry').reduce((t, g) => t + g.price, 0));
  const expected = cents(giftsPlanned + reserved + extras + interest);
  const spent = cents(plan.gifts.filter((g) => g.bought).reduce((t, g) => t + g.price, 0) + extras);
  const byMonth = {};
  for (const p of plans) for (const pay of p.payments) { const m = pay.date.slice(0, 7); byMonth[m] = cents((byMonth[m] || 0) + pay.amount); }
  return {
    people, giftsPlanned, reserved, extras, expected, spent, cap: plan.cap,
    overCap: plan.cap > 0 && expected > plan.cap ? cents(expected - plan.cap) : 0,
    capLeft: plan.cap > 0 ? cents(Math.max(0, plan.cap - expected)) : null,
    pct: plan.cap > 0 ? Math.min(100, Math.round((expected / plan.cap) * 100)) : null,
    bnpl: { count: plans.length, plans, interest, byMonth, total: cents(plans.reduce((t, p) => t + p.total, 0)), lastDate: plans.map((p) => p.last).sort().at(-1) || '' },
    carry,
  };
}

const monthName = (ym) => new Date(`${ym}-15T12:00:00Z`).toLocaleDateString('en-US', { month: 'long', year: 'numeric', timeZone: 'UTC' });

/** Plain-language warnings about the cap and BNPL. */
export function warnings(plan, today) {
  const s = summary(plan, today);
  const out = [];
  if (s.overCap) out.push({ level: 'high', text: `Your plan is $${s.overCap.toFixed(2)} over your cap. Trim a gift or two, or lower some per-person budgets.` });
  for (const p of s.people) if (p.over) out.push({ level: 'medium', text: `${p.name}'s gifts are $${p.over.toFixed(2)} over their budget.` });
  if (s.bnpl.count) {
    const months = Object.keys(s.bnpl.byMonth).filter((m) => m > today.slice(0, 7)).sort();
    if (months.length) out.push({ level: 'medium', text: `Buy now, pay later: you'll still be paying for these gifts in ${monthName(months.at(-1))}, with ${months.map((m) => `$${s.bnpl.byMonth[m].toFixed(2)} in ${monthName(m).split(' ')[0]}`).join(', ')}.` });
    if (s.bnpl.interest > 0) out.push({ level: 'high', text: `The monthly plans add $${s.bnpl.interest.toFixed(2)} in interest, so those gifts really cost $${s.bnpl.plans.filter((p) => p.type === 'monthly').reduce((t, p) => t + p.total, 0).toFixed(2)}.` });
    if (s.bnpl.count >= 3) out.push({ level: 'high', text: `You have ${s.bnpl.count} buy now, pay later plans. Several plans at once are easy to lose track of, and a missed payment usually means a late fee and can mean a hit to your credit.` });
    out.push({ level: 'info', text: 'Pay-in-4 is interest-free only if every payment goes through on time. Late fees and rules vary by provider: read the terms, and use autopay from an account that will have the money.' });
  }
  if (s.carry > 0) out.push({ level: 'medium', text: `$${s.carry.toFixed(2)} goes on a card you're carrying a balance on. At 22% APR, paying it off over a year adds about $${(s.carry * 0.12).toFixed(2)} in interest.` });
  return out;
}
