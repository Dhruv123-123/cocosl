import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as Bills from '../lib/bills.js';
import * as Deals from '../lib/promos.js';
import { buildIcs } from '../lib/ics.js';
import { monthsBetween, addMonths, addDays, daysBetween } from '../lib/dates.js';
import { PLANS } from '../lib/plans.js';

test('date helpers', () => {
  assert.equal(monthsBetween('2026-11-07', '2027-01-15'), 2);
  assert.equal(monthsBetween('2026-11-20', '2027-01-15'), 1);
  assert.equal(addMonths('2026-01-31', 1), '2026-02-28');
  assert.equal(addDays('2026-12-30', 3), '2027-01-02');
  assert.equal(daysBetween('2026-11-07', '2026-12-07'), 30);
});

test('bills: add, log calls, savings this year and overall', () => {
  const d = Bills.emptyBills();
  const net = Bills.addBill(d, { name: 'Internet', kind: 'internet', monthly: '80', promoEnd: '2026-11-20' });
  Bills.addBill(d, { name: 'Phone', kind: 'phone', monthly: 65 });
  assert.throws(() => Bills.addBill(d, { name: '', monthly: 5 }), /name/);
  assert.throws(() => Bills.addBill(d, { name: 'X', monthly: '' }), /costs a month/);
  assert.throws(() => Bills.addBill(d, { name: 'X', monthly: 5 }, { max: 2 }), Bills.LimitError);

  // Call on Nov 10: $80 -> $55 for 12 months
  const call = Bills.logCall(d, net.id, { date: '2026-11-10', outcome: 'Retention: $25 off for 12 months', newMonthly: '55', months: 12 });
  assert.equal(Bills.callSavings(call), 300);
  assert.equal(Bills.savingsInYear(call, 2026), 50); // Nov and Dec
  assert.equal(Bills.savingsInYear(call, 2027), 250);
  assert.equal(net.monthly, 55);
  assert.equal(net.promoEnd, '2027-11-10');

  // A call that changed nothing saves nothing and keeps the price
  const nothing = Bills.logCall(d, net.id, { date: '2026-11-12', outcome: 'No offers', newMonthly: '' });
  assert.equal(Bills.callSavings(nothing), 0);
  assert.equal(net.monthly, 55);

  const s = Bills.summarizeBills(d, '2026-12-01');
  assert.equal(s.monthly, 120);
  assert.equal(s.yearly, 1440);
  assert.equal(s.savedThisYear, 50);
  assert.equal(s.savedTotal, 300);
  assert.equal(s.calls, 2);
  assert.equal(s.rows[0].name, 'Internet'); // has a promo date, so it sorts before the phone
  assert.equal(s.rows[0].calls[0].outcome, 'No offers'); // newest call first

  Bills.removeBill(d, net.id);
  assert.equal(d.calls.length, 0);
  assert.deepEqual(Bills.loadBills('nope'), Bills.emptyBills());
  assert.equal(Bills.loadBills(JSON.stringify(d)).bills.length, 1);
});

test('bills: status and reminders two weeks before a promo ends', () => {
  const d = Bills.emptyBills();
  Bills.addBill(d, { name: 'Car insurance', kind: 'insurance', monthly: 140, promoEnd: '2027-03-01' });
  Bills.addBill(d, { name: 'Gym', kind: 'gym', monthly: 40, promoEnd: '2026-11-15' });
  Bills.addBill(d, { name: 'Old promo', kind: 'tv', monthly: 20, promoEnd: '2026-10-01' });
  const s = Bills.summarizeBills(d, '2026-11-07');
  assert.deepEqual(s.rows.map((r) => r.status.code), ['ended', 'soon', 'ok']);
  assert.equal(s.needsCall, 2);
  const r = Bills.billReminders(d, '2026-11-07');
  assert.equal(r.length, 2); // the ended promo gets no reminder
  assert.equal(r.find((x) => x.title.includes('Car insurance')).date, '2027-02-15');
  assert.equal(r.find((x) => x.title.includes('Gym')).date, '2026-11-07'); // less than 2 weeks left: remind today
  for (const k of Object.keys(Bills.KINDS)) assert.ok(Bills.SCRIPTS[k].lines.length >= 2, k);
});

test('bills: prefill from the subscription finder', () => {
  const found = [
    { name: 'Comcast Xfinity', cadence: 'monthly', amount: 89.99 },
    { name: 'Netflix', cadence: 'monthly', amount: 15.49 },
    { name: 'Amazon Prime', cadence: 'yearly', amount: 139 },
    { name: 'Old Gym', cadence: 'monthly', amount: 30, stale: true },
  ];
  const out = Bills.billsFromRecurring(found, [{ name: 'netflix' }]);
  assert.deepEqual(out, [{ name: 'Comcast Xfinity', kind: 'internet', monthly: 89.99 }]);
  assert.equal(Bills.guessKind('T-Mobile'), 'phone');
  assert.equal(Bills.guessKind('GEICO Auto'), 'insurance');
});

const STORE_CARD = { name: 'Furniture store card', kind: 'deferred', balance: '400', purchase: '1200', apr: '29.99', start: '2026-01-15', end: '2027-01-15', payment: '100' };

test('deals: deferred interest behind schedule', () => {
  const deal = Deals.makeDeal(STORE_CARD);
  const a = Deals.analyzeDeal(deal, '2026-11-07');
  assert.equal(a.paymentsLeft, 2);
  assert.equal(a.toClear, 200);
  assert.equal(a.safe, 400); // pay it off a month early
  assert.equal(a.leftover, 200);
  assert.equal(a.status, 'behind');
  assert.ok(a.cost > 150 && a.cost < 300, `back-dated interest ${a.cost}`);
  assert.ok(a.worstCase >= a.cost);
  assert.match(a.costNote, /back-dated interest/);

  const fine = Deals.analyzeDeal(Deals.makeDeal({ ...STORE_CARD, payment: '200' }), '2026-11-07');
  assert.equal(fine.onTrack, true);
  assert.equal(fine.cost, 0);
  assert.equal(fine.status, 'ok');
});

test('deals: true 0% only charges interest on what is left', () => {
  const a = Deals.analyzeDeal(Deals.makeDeal({ name: 'Balance transfer', kind: 'zero', balance: '3000', apr: '24', end: '2027-05-07', payment: '400' }), '2026-11-07');
  assert.equal(a.paymentsLeft, 6);
  assert.equal(a.toClear, 500);
  assert.equal(a.leftover, 600);
  assert.equal(a.cost, 12); // 600 x 24% / 12
  assert.match(a.costNote, /a month in interest/);
  assert.equal(Deals.analyzeDeal(Deals.makeDeal({ name: 'x', kind: 'zero', balance: '100', apr: '20', end: '2026-10-01' }), '2026-11-07').status, 'ended');
  assert.equal(Deals.analyzeDeal(Deals.makeDeal({ name: 'x', kind: 'zero', balance: '0', apr: '20', end: '2027-10-01' }), '2026-11-07').status, 'paid');
});

test('deals: validation, limits, summary and reminders', () => {
  assert.throws(() => Deals.makeDeal({ ...STORE_CARD, balance: '' }), /balance/);
  assert.throws(() => Deals.makeDeal({ ...STORE_CARD, end: '' }), /promo ends/);
  assert.throws(() => Deals.makeDeal({ ...STORE_CARD, apr: '' }), /APR/);
  assert.throws(() => Deals.makeDeal({ ...STORE_CARD, start: '2027-02-01' }), /before the end/);
  assert.equal(Deals.makeDeal({ name: 'Klarna', kind: 'bnpl', balance: '120', end: '2026-12-20' }).apr, 0);

  const data = Deals.emptyDeals();
  Deals.addDeal(data, STORE_CARD, { max: 1 });
  assert.throws(() => Deals.addDeal(data, STORE_CARD, { max: 1 }), Deals.LimitError);
  Deals.addDeal(data, { name: 'Balance transfer', kind: 'zero', balance: '3000', apr: '24', end: '2027-05-07', payment: '500' });
  const s = Deals.summarizeDeals(data, '2026-11-07');
  assert.equal(s.owed, 3400);
  assert.equal(s.behind, 1);
  assert.equal(s.rows[0].name, 'Furniture store card'); // soonest end first
  assert.equal(s.neededMonthly, 400 + 600);

  const r = Deals.dealReminders(data, '2026-11-07');
  assert.deepEqual(r.filter((x) => x.uid.includes(data.deals[0].id)).map((x) => x.date), ['2026-11-16', '2026-12-16', '2027-01-08']);
  assert.match(r[0].description, /back to the purchase date/);
  Deals.removeDeal(data, data.deals[0].id);
  assert.equal(data.deals.length, 1);
  assert.equal(Deals.loadDeals('{"deals":[1]}').deals.length, 1);
});

test('calendar file', () => {
  const ics = buildIcs([{ uid: 'bill-1', date: '2027-02-15', title: 'Call about Car insurance, promo ends', description: 'Line one\nLine two; with a comma, and more text that goes on long enough to need folding past seventy five characters' }], { stamp: new Date('2026-11-07T12:00:00Z') });
  assert.match(ics, /^BEGIN:VCALENDAR\r\n/);
  assert.match(ics, /DTSTART;VALUE=DATE:20270215\r\nDTEND;VALUE=DATE:20270216/);
  assert.match(ics, /SUMMARY:Call about Car insurance\\, promo ends/);
  assert.match(ics, /DTSTAMP:20261107T120000Z/);
  assert.ok(ics.split('\r\n').every((l) => l.length <= 75), 'lines are folded');
  assert.match(ics, /END:VCALENDAR\r\n$/);
});

test('free plan limits for the new tools', () => {
  assert.equal(PLANS.free.bills, 3);
  assert.equal(PLANS.free.deals, 1);
  assert.equal(PLANS.free.reminders, false);
  assert.equal(PLANS.pro.reminders, true);
});
