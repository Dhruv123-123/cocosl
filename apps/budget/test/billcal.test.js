import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import * as B from '../lib/billcal.js';

const bill = (o) => B.normalizeBill({ name: 'X', amount: 10, start: '2026-01-15', freq: 'monthly', ...o });

test('normalizeBill rejects bad input and cleans amounts', () => {
  assert.equal(B.normalizeBill({ name: '', amount: 5, start: '2026-01-01' }), null);
  assert.equal(B.normalizeBill({ name: 'Rent', amount: 'abc', start: '2026-01-01' }), null);
  assert.equal(B.normalizeBill({ name: 'Rent', amount: 5, start: '2026-02-30' }), null);
  const b = B.normalizeBill({ name: ' Rent ', amount: '$1,450.005', start: '2026-01-01', freq: 'nope' });
  assert.equal(b.name, 'Rent'); assert.equal(b.amount, 1450.01); assert.equal(b.freq, 'monthly');
});

test('occurrences for each repeat', () => {
  assert.deepEqual(B.occurrences(bill({}), '2026-03-01', '2026-05-31'), ['2026-03-15', '2026-04-15', '2026-05-15']);
  assert.deepEqual(B.occurrences(bill({ start: '2026-01-31' }), '2026-02-01', '2026-04-30'), ['2026-02-28', '2026-03-31', '2026-04-30'], '31st falls on the last day');
  assert.deepEqual(B.occurrences(bill({ start: '2026-01-02', freq: 'weekly' }), '2026-01-10', '2026-01-31'), ['2026-01-16', '2026-01-23', '2026-01-30']);
  assert.deepEqual(B.occurrences(bill({ start: '2026-01-02', freq: 'biweekly' }), '2026-01-10', '2026-02-28'), ['2026-01-16', '2026-01-30', '2026-02-13', '2026-02-27']);
  assert.deepEqual(B.occurrences(bill({ freq: 'quarterly' }), '2026-01-01', '2026-12-31'), ['2026-01-15', '2026-04-15', '2026-07-15', '2026-10-15']);
  assert.deepEqual(B.occurrences(bill({ start: '2025-03-01', freq: 'yearly' }), '2026-01-01', '2027-12-31'), ['2026-03-01', '2027-03-01']);
  assert.deepEqual(B.occurrences(bill({ freq: 'once' }), '2026-01-01', '2026-01-31'), ['2026-01-15']);
  assert.deepEqual(B.occurrences(bill({ freq: 'once' }), '2026-02-01', '2026-02-28'), []);
  assert.deepEqual(B.occurrences(bill({}), '2025-01-01', '2026-01-31'), ['2026-01-15'], 'nothing before the first due date');
  assert.deepEqual(B.occurrences(bill({ until: '2026-02-20' }), '2026-01-01', '2026-06-30'), ['2026-01-15', '2026-02-15']);
});

test('monthView: grid starts on Sunday, totals, paid and overdue', () => {
  let st = { bills: [bill({ id: 'rent', name: 'Rent', amount: 1450, start: '2026-11-01' }), bill({ id: 'ph', name: 'Phone', amount: 85, start: '2026-11-20', autopay: true }), bill({ id: 'gym', name: 'Gym', amount: 25, start: '2026-11-05' })], paid: {} };
  st = B.togglePaid(st, 'rent|2026-11-01');
  const v = B.monthView(st, '2026-11', '2026-11-07');
  assert.equal(v.weeks[0][0].date, '2026-11-01', 'Nov 1 2026 is a Sunday');
  assert.equal(v.weeks.at(-1).length, 7);
  assert.equal(v.total, 1560); assert.equal(v.paid, 1450); assert.equal(v.left, 110); assert.equal(v.autopay, 85);
  assert.equal(v.overdue, 1, 'gym on the 5th, not paid, not autopay');
  const dec = B.monthView(st, '2026-12', '2026-11-07');
  assert.equal(dec.weeks[0].filter((c) => c === null).length, 2, 'Dec 1 2026 is a Tuesday');
  assert.deepEqual(B.upcoming(st, '2026-11-07', 14).map((i) => i.bill.name), ['Phone']);
  assert.deepEqual(B.overdue(st, '2026-11-07').map((i) => i.key), ['gym|2026-11-05']);
});

test('remove bill drops its paid marks; loadState drops junk', () => {
  let st = { bills: [bill({ id: 'a' }), bill({ id: 'b' })], paid: { 'a|2026-01-15': true, 'b|2026-01-15': true } };
  st = B.removeBill(st, 'a');
  assert.deepEqual(Object.keys(st.paid), ['b|2026-01-15']);
  const loaded = B.loadState(JSON.stringify({ bills: [...st.bills, { name: '' }], paid: { ...st.paid, 'zzz|2026-01-01': true, 'b|bad': true } }));
  assert.equal(loaded.bills.length, 1);
  assert.deepEqual(Object.keys(loaded.paid), ['b|2026-01-15']);
  assert.deepEqual(B.loadState('not json'), { bills: [], paid: {} });
});

test('shiftMonth and perMonth', () => {
  assert.equal(B.shiftMonth('2026-12', 1), '2027-01');
  assert.equal(B.shiftMonth('2026-01', -1), '2025-12');
  assert.equal(B.perMonth(bill({ amount: 100, freq: 'weekly' })), 433.33);
  assert.equal(B.perMonth(bill({ amount: 600, freq: 'yearly' })), 50);
});

test('calendar file: repeating events, end-of-month rule, alarms, escaping', () => {
  const st = { bills: [
    bill({ id: 'r', name: 'Rent, apt; #2', amount: 1450, start: '2026-11-01' }),
    bill({ id: 'c', name: 'Card', amount: 40, start: '2026-11-30' }),
    bill({ id: 'l', name: 'Loan', amount: 200, start: '2026-10-31' }),
    bill({ id: 'w', name: 'Daycare', amount: 300, start: '2026-11-06', freq: 'biweekly' }),
    bill({ id: 'y', name: 'Car tag', amount: 90, start: '2027-03-10', freq: 'yearly' }),
  ], paid: {} };
  const ics = B.billsIcs(st, { daysBefore: 2, stamp: new Date('2026-11-07T00:00:00Z') });
  assert.match(ics, /^BEGIN:VCALENDAR\r\n/);
  assert.match(ics, /UID:r@moneymadesimple-bills\r\nDTSTAMP:20261107T000000Z\r\nDTSTART;VALUE=DATE:20261101\r\nDTEND;VALUE=DATE:20261102\r\nRRULE:FREQ=MONTHLY;INTERVAL=1\r\n/);
  assert.match(ics, /SUMMARY:Rent\\, apt\\; #2 due \(\$1450\)/);
  assert.match(ics, /RRULE:FREQ=MONTHLY;INTERVAL=1;BYMONTHDAY=-1/, '31st becomes last day of month');
  assert.equal((ics.match(/UID:c-/g) || []).length, 25, '30th: explicit dates for 24 months');
  assert.match(ics, /RRULE:FREQ=WEEKLY;INTERVAL=2/);
  assert.match(ics, /RRULE:FREQ=YEARLY\r\n/);
  assert.match(ics, /TRIGGER:-PT39H/, '2 days before at 9am');
  assert.equal(B.trigger(0), 'PT9H');
  assert.ok(ics.split('\r\n').every((l) => l.length <= 75), 'lines folded');
  assert.equal((ics.match(/BEGIN:VEVENT/g) || []).length, (ics.match(/END:VEVENT/g) || []).length);
});

test('pages: both languages, offline list complete, nothing sent anywhere', () => {
  const read = (f) => readFileSync(new URL(`../bill-calendar/${f}`, import.meta.url), 'utf8');
  const en = read('index.html'); const es = read('es.html'); const sw = read('sw.js');
  assert.match(en, /<html lang="en">/); assert.match(es, /<html lang="es">/);
  assert.ok(en.includes('href="es.html"') && es.includes('href="./"'));
  for (const id of ['grid', 'list', 'soon', 'bills', 'stats', 'ics', 'backup', 'restore', 'bill-form']) { assert.ok(en.includes(`id="${id}"`), id); assert.ok(es.includes(`id="${id}"`), id); }
  for (const f of ['index.html', 'es.html', 'app.js', 'manifest.webmanifest', 'manifest-es.webmanifest', 'icon-192.png', '../lib/billcal.js', '../lib/dates.js']) assert.ok(sw.includes(`'${f}'`), f);
  assert.equal(JSON.parse(read('manifest-es.webmanifest')).start_url, './es.html');
  assert.doesNotMatch(read('app.js') + readFileSync(new URL('../lib/billcal.js', import.meta.url), 'utf8'), /fetch\(|XMLHttpRequest|sendBeacon/);
});
