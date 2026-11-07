// Bill negotiation tracker: your bills, when each promo price ends, what you asked for on each
// call, and how much the calls saved. Do-it-yourself, so you keep 100% of the savings, and it
// never asks for logins. All data stays in this browser.
import { isDay, addDays, daysBetween, addMonths } from './dates.js';

export const REMIND_DAYS = 14;
export const SOON_DAYS = 30;

export const KINDS = {
  internet: 'Internet',
  phone: 'Phone',
  insurance: 'Car or home insurance',
  tv: 'TV or streaming',
  gym: 'Gym or membership',
  other: 'Other bill',
};

// What to say on the call. Plain and honest: nothing that needs you to invent a competing offer.
export const SCRIPTS = {
  internet: {
    who: 'Ask for the retention or loyalty team ("I\'m thinking about cancelling").',
    lines: [
      'I\'ve been a customer since [year] and my bill went from $[old] to $[new]. I\'d like to stay, but I need a lower price.',
      'New customers in my area get [plan] for $[price]. Can you match that, or what\'s the best you can do?',
      'If there\'s no promo, can you move me to a slower plan that still covers what I use?',
      'Can you take off the equipment fee if I use my own modem?',
    ],
    close: 'Before you hang up, ask for the new monthly price including taxes and fees, how long it lasts, and a confirmation number.',
  },
  phone: {
    who: 'Ask for the loyalty or retention department.',
    lines: [
      'I\'m paying $[old] a month for [n] lines. I\'m comparing prepaid plans that cost less. What can you do to keep me?',
      'Am I paying for anything I don\'t use, like device insurance, extra data, or a phone that\'s already paid off?',
      'Is there an autopay, employer, military, student or senior discount I could get?',
    ],
    close: 'Ask for the new price in writing (text or email) and the date it ends.',
  },
  insurance: {
    who: 'Call your agent or the company. Get one or two outside quotes first.',
    lines: [
      'My renewal went up to $[new]. I have a quote for similar coverage at $[quote]. Can you review my policy for discounts?',
      'Can you check bundling, paperless, autopay, safe driver, low mileage, home security and pay-in-full discounts?',
      'What would raising my deductible from $[a] to $[b] save? (Only worth it if you could pay that deductible from savings.)',
    ],
    close: 'Don\'t cancel the old policy until the new one is active, so you\'re never uninsured.',
  },
  tv: {
    who: 'Start cancelling online or tell the agent you want to cancel. Offers often show up at that step.',
    lines: [
      'I\'d like to cancel. Is there a cheaper plan or a discount before I go?',
      'Can I pause instead of cancelling, or switch to the plan with ads?',
    ],
    close: 'If you do cancel, write down the last day of service so you aren\'t billed again.',
  },
  gym: {
    who: 'Ask for the manager. Read your contract\'s cancellation rules first.',
    lines: [
      'I\'m paying $[old] a month. Is there an off-peak or yearly rate that costs less?',
      'Can you freeze my membership for [n] months instead of charging me?',
    ],
    close: 'Get any change or cancellation in writing, with the date.',
  },
  other: {
    who: 'Ask for the department that handles cancellations.',
    lines: [
      'I\'ve been a customer for [n] years and the price went up. What\'s the best rate you can offer to keep me?',
      'Is there a cheaper plan with only what I actually use?',
    ],
    close: 'Write down the new price, how long it lasts and a confirmation number.',
  },
};

export class LimitError extends Error {}

export const emptyBills = () => ({ bills: [], calls: [] });

export function loadBills(raw) {
  try {
    const d = JSON.parse(raw);
    if (d && Array.isArray(d.bills) && Array.isArray(d.calls)) return d;
  } catch { /* fall through */ }
  return emptyBills();
}

const newId = () => Math.random().toString(36).slice(2, 10);
const money = (v) => {
  if (v === '' || v == null) return NaN;
  const n = Math.round(Number(v) * 100) / 100;
  return Number.isFinite(n) && n >= 0 ? n : NaN;
};
const round = (n) => Math.round(n * 100) / 100;

export function addBill(data, { name, kind = 'other', monthly, promoEnd = '', notes = '' }, { max = Infinity } = {}) {
  name = String(name || '').trim();
  if (!name) throw new Error('Give the bill a name.');
  const m = money(monthly);
  if (Number.isNaN(m)) throw new Error('Enter what the bill costs a month.');
  if (promoEnd && !isDay(promoEnd)) throw new Error('That promo end date doesn\'t look right.');
  if (data.bills.length >= max) throw new LimitError(`The free plan tracks ${max} bills. Pro tracks every bill and adds calendar reminders.`);
  const bill = { id: newId(), name: name.slice(0, 60), kind: KINDS[kind] ? kind : 'other', monthly: m, promoEnd: promoEnd || '', notes: String(notes || '').slice(0, 500) };
  data.bills.push(bill);
  return bill;
}

export function removeBill(data, billId) {
  data.bills = data.bills.filter((b) => b.id !== billId);
  data.calls = data.calls.filter((c) => c.billId !== billId);
}

/**
 * Log a call. When the price went down, the bill's price and promo end date are updated and
 * the call saved (old - new) x months. Leave the new price blank when nothing changed.
 */
export function logCall(data, billId, { date, outcome = '', newMonthly = '', months = 12 }) {
  const bill = data.bills.find((b) => b.id === billId);
  if (!bill) throw new Error('Pick a bill.');
  if (!isDay(date)) throw new Error('Enter the date of the call.');
  const n = newMonthly === '' || newMonthly == null ? bill.monthly : money(newMonthly);
  if (Number.isNaN(n)) throw new Error('Enter the new monthly price, or leave it blank if nothing changed.');
  const mo = Math.max(0, Math.min(60, Math.round(Number(months) || 0)));
  const call = { id: newId(), billId, date, outcome: String(outcome || '').slice(0, 300), oldMonthly: bill.monthly, newMonthly: n, months: n < bill.monthly ? mo : 0 };
  data.calls.push(call);
  if (n !== bill.monthly) {
    if (n < bill.monthly && mo) bill.promoEnd = addMonths(date, mo);
    bill.monthly = n;
  }
  return call;
}

export const callSavings = (c) => round(Math.max(0, c.oldMonthly - c.newMonthly) * c.months);

/** The part of a call's savings that lands in one calendar year (one month's saving per month from the call). */
export function savingsInYear(c, year) {
  const per = Math.max(0, c.oldMonthly - c.newMonthly);
  let total = 0;
  for (let i = 0; i < c.months; i++) if (addMonths(c.date, i).startsWith(`${year}-`)) total += per;
  return round(total);
}

export function billStatus(bill, today) {
  if (!bill.promoEnd) return { code: 'none', days: null };
  const days = daysBetween(today, bill.promoEnd);
  if (days < 0) return { code: 'ended', days };
  if (days <= SOON_DAYS) return { code: 'soon', days };
  return { code: 'ok', days };
}

export function summarizeBills(data, today) {
  const year = Number(today.slice(0, 4));
  const order = { ended: 0, soon: 1, ok: 2, none: 3 };
  const rows = data.bills
    .map((b) => ({ ...b, status: billStatus(b, today), calls: data.calls.filter((c) => c.billId === b.id).sort((x, y) => y.date.localeCompare(x.date)) }))
    .sort((a, b) => order[a.status.code] - order[b.status.code] || (a.promoEnd || '9').localeCompare(b.promoEnd || '9') || a.name.localeCompare(b.name));
  const monthly = round(data.bills.reduce((s, b) => s + b.monthly, 0));
  return {
    rows,
    monthly,
    yearly: round(monthly * 12),
    savedThisYear: round(data.calls.reduce((s, c) => s + savingsInYear(c, year), 0)),
    savedTotal: round(data.calls.reduce((s, c) => s + callSavings(c), 0)),
    calls: data.calls.length,
    needsCall: rows.filter((r) => r.status.code === 'ended' || r.status.code === 'soon').length,
  };
}

/** Calendar reminders REMIND_DAYS before each promo ends (today, if that day has passed). */
export function billReminders(data, today) {
  return data.bills.filter((b) => b.promoEnd && b.promoEnd >= today).map((b) => {
    const when = addDays(b.promoEnd, -REMIND_DAYS);
    return {
      uid: `bill-${b.id}-${b.promoEnd}`,
      date: when < today ? today : when,
      title: `Call about ${b.name}: promo price ends ${b.promoEnd}`,
      description: `Your ${KINDS[b.kind].toLowerCase()} price ($${b.monthly.toFixed(2)} a month) ends on ${b.promoEnd}. ${SCRIPTS[b.kind].who} The call script is in your bill tracker.`,
    };
  });
}

export function guessKind(name) {
  const n = String(name || '');
  if (/comcast|xfinity|spectrum|fios|cox|frontier|internet|fiber|broadband|starlink/i.test(n)) return 'internet';
  if (/t-mobile|tmobile|verizon|at&t|att\b|mint|visible|cricket|wireless|mobile/i.test(n)) return 'phone';
  if (/geico|progressive|state farm|allstate|insurance|lemonade|liberty mutual/i.test(n)) return 'insurance';
  if (/netflix|hulu|disney|\bmax\b|peacock|paramount|youtube|spotify|sling|directv/i.test(n)) return 'tv';
  if (/gym|fitness|planet|peloton|club|ymca/i.test(n)) return 'gym';
  return 'other';
}

/** Monthly charges found by the subscription finder (lib/recurring.js) that aren't tracked yet. */
export function billsFromRecurring(found, existing = []) {
  const have = new Set(existing.map((b) => b.name.toLowerCase()));
  return found
    .filter((r) => r.cadence === 'monthly' && !r.stale && !have.has(String(r.name).toLowerCase()))
    .map((r) => ({ name: r.name, kind: guessKind(r.name), monthly: r.amount }));
}
