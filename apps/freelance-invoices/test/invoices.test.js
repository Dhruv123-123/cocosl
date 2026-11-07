import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import * as I from '../lib/invoices.js';
import config from '../config.js';

const base = { client: 'Northwind Studio', clientEmail: 'ap@northwind.com', number: '2026-014', project: 'October site updates', amount: '1,800', issued: '2026-10-01', terms: '30', sent: '2026-10-01' };

test('validation and due dates from terms', () => {
  assert.throws(() => I.makeInvoice({ ...base, client: '' }), /client/);
  assert.throws(() => I.makeInvoice({ ...base, amount: '0' }), /amount/);
  assert.throws(() => I.makeInvoice({ ...base, terms: 'custom', due: '2026-09-01' }), /before the invoice date/);
  assert.throws(() => I.makeInvoice({ ...base, feeType: 'percent', feeRate: '25' }), /between/);
  assert.equal(I.makeInvoice(base).due, '2026-10-31');
  assert.equal(I.makeInvoice({ ...base, terms: '0' }).due, '2026-10-01');
  assert.equal(I.makeInvoice({ ...base, terms: 'custom', due: '2026-11-20' }).due, '2026-11-20');
  assert.equal(I.makeInvoice(base).amount, 1800);
});

test('status moves from draft to overdue to paid', () => {
  const inv = I.makeInvoice({ ...base, sent: '' });
  assert.equal(I.status(inv, '2026-10-05').state, 'draft');
  inv.sent = '2026-10-01';
  assert.equal(I.status(inv, '2026-10-05').state, 'sent');
  assert.equal(I.status(inv, '2026-10-28').state, 'due-soon');
  assert.equal(I.status(inv, '2026-10-31').state, 'due-today');
  const late = I.status(inv, '2026-11-07');
  assert.deepEqual([late.state, late.daysLate, late.owed], ['overdue', 7, 1800]);
  const book = { invoices: [inv] };
  I.recordPayment(book, inv.id, '800', '2026-11-08');
  assert.deepEqual([I.status(inv, '2026-11-09').owed, I.status(inv, '2026-11-09').partly], [1000, true]);
  I.markPaid(book, inv.id, '2026-11-10');
  const paid = I.status(inv, '2026-11-12');
  assert.deepEqual([paid.state, paid.paidDate, paid.daysToPay], ['paid', '2026-11-10', 40]);
});

test('late fees: per month or part month after the grace period, or a flat fee', () => {
  const pct = I.makeInvoice({ ...base, feeType: 'percent', feeRate: '1.5', grace: '5' });
  assert.equal(I.lateFee(pct, '2026-11-05').fee, 0, 'inside the grace period');
  assert.deepEqual(I.lateFee(pct, '2026-11-06'), { fee: 27, months: 1, apr: 18 });
  assert.equal(I.lateFee(pct, '2026-12-06').months, 2);
  assert.equal(I.lateFee(pct, '2026-12-06').fee, 54);
  pct.payments.push({ amount: 1000, date: '2026-11-01' });
  assert.equal(I.lateFee(pct, '2026-11-06').fee, 12, 'on the unpaid balance only');
  const flat = I.makeInvoice({ ...base, feeType: 'flat', feeFlat: '25' });
  assert.equal(I.lateFee(flat, '2026-10-31').fee, 0);
  assert.equal(I.lateFee(flat, '2026-11-20').fee, 25);
  assert.equal(I.lateFee(I.makeInvoice(base), '2027-03-01').fee, 0, 'no fee unless the terms have one');
});

test('reminder emails: right stage, polite, amounts and fees from the terms', () => {
  const inv = I.makeInvoice({ ...base, feeType: 'percent', feeRate: '1.5' });
  assert.equal(I.suggestedStage(inv, '2026-10-20'), '');
  assert.equal(I.suggestedStage(inv, '2026-10-29'), 'before');
  assert.equal(I.suggestedStage(inv, '2026-10-31'), 'due');
  assert.equal(I.suggestedStage(inv, '2026-11-04'), 'late');
  assert.equal(I.suggestedStage(inv, '2026-11-20'), 'firm');
  assert.equal(I.suggestedStage(inv, '2026-12-05'), 'final');
  const me = { name: 'Riley Chen', business: 'Chen Design', payHow: 'https://pay.example/riley' };
  const late = I.reminderEmail(inv, 'late', '2026-11-04', me);
  assert.equal(late.subject, 'Following up on invoice 2026-014');
  assert.match(late.body, /^Hi Northwind,\n\nI wanted to follow up on invoice 2026-014 for October site updates, which was due on October 31, 2026\. The balance is \$1,800\.00, plus a late fee of \$27\.00 under the payment terms on the invoice, for a total of \$1,827\.00\./);
  assert.match(late.body, /You can pay here: https:\/\/pay\.example\/riley/);
  assert.match(late.body, /Thanks,\nRiley Chen\nChen Design$/);
  const fin = I.reminderEmail(inv, 'final', '2026-12-05', {});
  assert.match(fin.subject, /^Final notice: invoice 2026-014, 35 days overdue$/);
  assert.match(fin.body, /\[Your name\]$/);
  for (const stage of Object.keys(I.STAGES)) assert.doesNotMatch(I.reminderEmail(inv, stage, '2026-12-05', me).body, /lawsuit|sue|collections agency|undefined|NaN/i, stage);
  assert.match(I.mailto(inv, late), /^mailto:ap%40northwind\.com\?subject=Following%20up/);
});

test('summary, calendar and CSV', () => {
  const book = I.emptyBook();
  const a = I.addInvoice(book, { ...base, amount: '1000' }); // due 10-31, overdue on 11-07
  I.addInvoice(book, { ...base, client: 'Acme', amount: '500', issued: '2026-11-01' }); // due 12-01
  const c = I.addInvoice(book, { ...base, client: 'Globex', amount: '300', issued: '2026-09-01' });
  I.markPaid(book, c.id, '2026-09-21');
  const s = I.summary(book, '2026-11-07');
  assert.deepEqual(s, { outstanding: 1500, overdue: 1000, overdueCount: 1, fees: 0, paidThisYear: 300, avgDaysToPay: 20 });
  assert.equal(I.board(book, '2026-11-07')[0].id, a.id);
  assert.deepEqual(I.reminderEvents(book, '2026-11-07').map((e) => e.date), ['2026-11-07', '2026-11-28', '2026-12-01', '2026-12-08']);
  const csv = I.toCsv(book, '2026-11-07');
  assert.match(csv, /^"Invoice","Client"/);
  assert.equal(csv.trim().split('\r\n').length, 4);
  assert.equal(I.loadBook('{bad').invoices.length, 0);
});

test('page: free and private, upsell hidden until its link is real, signup form', () => {
  const html = readFileSync(new URL('../index.html', import.meta.url), 'utf8');
  assert.match(html, /Everything stays in this browser/);
  assert.match(html, /Only charge a late fee your client agreed to/);
  assert.match(html, /name="freelance-invoices"[^>]*data-netlify="true"/);
  assert.match(config.product.url, /REPLACE_ME/);
});
