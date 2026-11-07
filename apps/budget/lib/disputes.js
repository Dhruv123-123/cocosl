// Credit report dispute tracker (disputes.html). Tracking only: dates, the reply clock and what
// the bureau said. It writes no letters and is not a credit repair service. Everything here is free.
//
// Timing under the Fair Credit Reporting Act (general information, not legal advice):
// - A credit bureau generally has 30 days from receiving a dispute to investigate (FCRA 611(a)(1)).
// - 45 days if you dispute after getting your free annual report, or up to 15 extra days if you
//   send more information during the 30 days (611(a)(1)(B), 612(a)).
// - It must send the results within 5 business days of finishing (611(a)(6)).
// - A dispute sent straight to the lender or collector that reported the item (the "furnisher")
//   generally runs on the same 30 days (623(a)(8)).
import { isDay, addDays, daysBetween } from './dates.js';

export const TARGETS = {
  equifax: { name: 'Equifax', url: 'https://www.equifax.com/personal/credit-report-services/credit-dispute/' },
  experian: { name: 'Experian', url: 'https://www.experian.com/disputes/main.html' },
  transunion: { name: 'TransUnion', url: 'https://www.transunion.com/credit-disputes/dispute-your-credit' },
  furnisher: { name: 'The lender or collector directly', url: '' },
};

export const REASONS = {
  'not-mine': "Not my account",
  'identity-theft': 'Opened by an identity thief',
  'wrong-late': 'Shows late, but I paid on time',
  'wrong-balance': 'Wrong balance or credit limit',
  'wrong-status': 'Wrong status (open/closed, paid, charged off)',
  duplicate: 'Listed twice',
  'too-old': 'Older than the 7-year limit',
  'wrong-personal': 'Wrong name, address or other personal info',
  other: 'Something else',
};

export const METHODS = { online: 'Online', mail: 'Mail', phone: 'Phone' };

export const OUTCOMES = {
  deleted: 'Removed',
  corrected: 'Corrected',
  verified: 'Verified as accurate (no change)',
  frivolous: 'Rejected as "frivolous" or not investigated',
};

export const MAIL_DAYS = 5; // assumed delivery time when you mailed it and have no delivery date
export const NOTICE_DAYS = 7; // 5 business days to send results, as calendar days

const uid = () => Math.random().toString(36).slice(2, 10);
const clean = (s, max = 120) => String(s ?? '').trim().slice(0, max);

export const emptyDisputes = () => ({ version: 1, disputes: [] });

export function loadDisputes(json) {
  try {
    const d = typeof json === 'string' ? JSON.parse(json) : json;
    if (!d || !Array.isArray(d.disputes)) return emptyDisputes();
    return { version: 1, disputes: d.disputes.filter((x) => x && TARGETS[x.target] && isDay(x.sent)) };
  } catch { return emptyDisputes(); }
}

/** Validate form values into a dispute. Throws with a message a person can act on. */
export function makeDispute(v) {
  const target = TARGETS[v.target] ? v.target : '';
  if (!target) throw new Error('Pick who you sent the dispute to.');
  const item = clean(v.item, 80);
  if (!item) throw new Error('Name the item you disputed, for example the account name on your report.');
  if (!isDay(v.sent)) throw new Error('Add the date you sent the dispute.');
  const received = isDay(v.received) ? v.received : '';
  if (received && received < v.sent) throw new Error("The date they received it can't be before you sent it.");
  return {
    id: v.id || uid(),
    target,
    furnisher: clean(v.furnisher, 80),
    item,
    reason: REASONS[v.reason] ? v.reason : 'other',
    method: METHODS[v.method] ? v.method : 'online',
    sent: v.sent,
    received,
    extended: v.extended === true || v.extended === 'on',
    confirmation: clean(v.confirmation, 60),
    outcome: OUTCOMES[v.outcome] ? v.outcome : '',
    outcomeDate: isDay(v.outcomeDate) ? v.outcomeDate : '',
    checkedReport: isDay(v.checkedReport) ? v.checkedReport : '',
    notes: clean(v.notes, 500),
  };
}

export function addDispute(data, values) {
  const d = makeDispute(values);
  data.disputes.push(d);
  return d;
}

export function removeDispute(data, id) {
  data.disputes = data.disputes.filter((d) => d.id !== id);
}

export function setOutcome(data, id, outcome, date) {
  const d = data.disputes.find((x) => x.id === id);
  if (!d) throw new Error('Dispute not found.');
  if (outcome && !OUTCOMES[outcome]) throw new Error('Unknown outcome.');
  if (outcome && !isDay(date)) throw new Error('Add the date of their reply.');
  d.outcome = outcome || '';
  d.outcomeDate = outcome ? date : '';
  return d;
}

/**
 * The reply clock for one dispute on `today`.
 * state: 'waiting' | 'due-soon' (5 days or less) | 'late' (past the deadline, results may still be in the post)
 *        | 'overdue' (past the deadline plus time to send results) | 'answered'
 */
export function clock(d, today) {
  const start = d.received || (d.method === 'mail' ? addDays(d.sent, MAIL_DAYS) : d.sent);
  const days = d.extended ? 45 : 30;
  const due = addDays(start, days);
  const noticeBy = addDays(due, NOTICE_DAYS);
  const left = daysBetween(today, due);
  let state = 'waiting';
  if (d.outcome) state = 'answered';
  else if (today > noticeBy) state = 'overdue';
  else if (left < 0) state = 'late';
  else if (left <= 5) state = 'due-soon';
  const elapsed = Math.max(0, daysBetween(start, today));
  return { start, estimatedStart: !d.received, days, due, noticeBy, left, state, pct: Math.min(100, Math.round((elapsed / days) * 100)) };
}

/** What to do next, in plain words. */
export function nextSteps(d, today) {
  const c = clock(d, today);
  const who = TARGETS[d.target].name;
  if (c.state === 'overdue') return [
    `${who} has had more than ${c.days} days plus time to send the results. Check your credit report to see whether the item changed.`,
    'If you have heard nothing, you can submit a complaint to the CFPB at consumerfinance.gov/complaint. It is free and companies must respond.',
    'Keep your confirmation number, the date you sent it and proof of delivery.',
  ];
  if (c.state === 'late') return [
    `The ${c.days}-day investigation period has passed. Results should arrive within about 5 business days.`,
    'Check your credit report now: corrections often show up there before the letter arrives.',
  ];
  if (!d.outcome) return [
    `Wait for ${who}'s results by ${c.noticeBy}. ${c.estimatedStart ? 'Add the date they received it, if you know it, for an exact clock.' : ''}`.trim(),
    'If you find more proof (statements, payment confirmations), you can send it, but it can extend their deadline by up to 15 days.',
  ];
  switch (d.outcome) {
    case 'deleted': return [
      'Check your report in about a week to confirm it is gone at every bureau that listed it.',
      'If a removed item comes back, the bureau must tell you within 5 business days. Mark it here and dispute again.',
    ];
    case 'corrected': return [
      'Check the corrected details on your report. If anything is still wrong, start a new dispute for that part.',
      'Corrections at one bureau don\'t always reach the others: check all three.',
    ];
    case 'verified': return [
      'You can ask the bureau how it verified the item, including the business it contacted. It must answer within 15 days of your request.',
      'You can dispute directly with the lender or collector, sending copies of your proof.',
      'You can add a statement of up to 100 words to your file explaining your side.',
      'If you think the investigation was not real, submit a complaint to the CFPB at consumerfinance.gov/complaint.',
    ];
    case 'frivolous': return [
      'A bureau that calls a dispute frivolous must tell you why and what information it needs.',
      'Send that information in a new dispute, with copies (never originals) of your proof.',
    ];
    default: return [];
  }
}

const ORDER = { overdue: 0, late: 1, 'due-soon': 2, waiting: 3, answered: 4 };

/** Disputes sorted most urgent first, with their clocks. */
export function board(data, today) {
  return data.disputes
    .map((d) => ({ ...d, clock: clock(d, today) }))
    .sort((a, b) => ORDER[a.clock.state] - ORDER[b.clock.state] || a.clock.due.localeCompare(b.clock.due));
}

export function summary(data, today) {
  const rows = board(data, today);
  const open = rows.filter((r) => r.clock.state !== 'answered');
  return {
    total: rows.length,
    open: open.length,
    overdue: rows.filter((r) => r.clock.state === 'overdue' || r.clock.state === 'late').length,
    removedOrFixed: rows.filter((r) => r.outcome === 'deleted' || r.outcome === 'corrected').length,
    nextDue: open.filter((r) => r.clock.left >= 0).map((r) => r.clock.due).sort()[0] || '',
  };
}

/** Calendar reminders: the reply deadline and a report check a week after it. */
export function reminderEvents(data, today) {
  const out = [];
  for (const r of board(data, today)) {
    if (r.clock.state === 'answered') continue;
    const who = TARGETS[r.target].name;
    out.push({ uid: `dispute-${r.id}-due`, date: r.clock.due, title: `Credit dispute deadline: ${who} (${r.item})`, description: `${who} should finish investigating your dispute about ${r.item} today. Results are due within about 5 business days.` });
    out.push({ uid: `dispute-${r.id}-check`, date: r.clock.noticeBy, title: `Check your credit report: ${r.item}`, description: `No reply about ${r.item} yet? Check your report and consider a CFPB complaint at consumerfinance.gov/complaint.` });
  }
  return out.filter((e) => e.date >= today);
}
