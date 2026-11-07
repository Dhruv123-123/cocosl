import test from 'node:test';
import assert from 'node:assert/strict';
import { dueDate, longDate, totals, nextNumber, lateFeeLine, missing } from '../lib/invoice.js';

test('due dates count calendar days from the invoice date', () => {
  assert.equal(dueDate('2027-06-01', 'net30'), '2027-07-01');
  assert.equal(dueDate('2027-12-20', 'net15'), '2028-01-04');
  assert.equal(dueDate('2027-06-01', 'receipt'), '2027-06-01');
  assert.equal(dueDate('', 'net30'), '');
  assert.equal(longDate('2027-06-30'), 'June 30, 2027');
});

test('totals: line items, optional sales tax, deposit already paid', () => {
  const t = totals([{ desc: 'Design', qty: 10, rate: 75 }, { desc: 'Revisions', qty: '2', rate: '$75' }, { desc: '', qty: '', rate: '' }], { taxRate: 0, deposit: 450 });
  assert.equal(t.lines.length, 2);
  assert.equal(t.subtotal, 900);
  assert.equal(t.due, 450);
  assert.equal(totals([{ desc: 'Kit', qty: 1, rate: 100 }], { taxRate: 7.25 }).due, 107.25);
  assert.equal(totals([{ desc: 'X', qty: 1, rate: 100 }], { deposit: 500 }).due, 0, 'deposit never makes it negative');
});

test('invoice numbers keep their prefix and padding', () => {
  assert.equal(nextNumber('2026-014'), '2026-015');
  assert.equal(nextNumber('INV9'), 'INV10');
  assert.equal(nextNumber('099'), '100');
  assert.equal(nextNumber(''), '001');
});

test('late fee line and the ready-to-send checklist', () => {
  assert.equal(lateFeeLine(1.5, '2027-07-01'), 'A late fee of 1.5% per month applies to any balance unpaid after July 1, 2027, as agreed.');
  assert.equal(lateFeeLine(0, '2027-07-01'), '');
  assert.equal(missing({}).length, 8);
  assert.deepEqual(missing({ fromName: 'A', fromEmail: 'a@x.com', toName: 'B', number: '1', issued: '2027-06-01', payHow: 'link', items: [{ desc: 'Work', qty: 1, rate: 10 }] }), []);
});
