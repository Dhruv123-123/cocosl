import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { parseStatement, parseLine, leadingDate, moneyValue } from '../lib/statement.js';
import { findRecurring } from '../lib/recurring.js';

const today = '2026-11-07';

test('dates: numeric, ISO, month names, posting dates, and the year rolls back', () => {
  assert.equal(leadingDate('10/03 X', today).date, '2026-10-03');
  assert.equal(leadingDate('10-03-25 X', today).date, '2025-10-03');
  assert.equal(leadingDate('2026-09-14 X', today).date, '2026-09-14');
  assert.equal(leadingDate('Sept 14, 2026 X', today).date, '2026-09-14');
  assert.equal(leadingDate('14 Oct X', today).date, '2026-10-14');
  assert.equal(leadingDate('Dec 28 X', '2027-01-05').date, '2026-12-28', 'December read in January is last year');
  assert.equal(leadingDate('Mayor 3 x', today), null);
  assert.equal(leadingDate('Opening balance', today), null);
});

test('amounts: balance column ignored, negatives, parentheses and CR', () => {
  assert.deepEqual(parseLine('10/03 10/04 NETFLIX.COM 866-579-7172 CA 15.49 1,234.56', today), { date: '2026-10-03', amount: 15.49, credit: false, note: 'NETFLIX.COM 866-579-7172 CA' });
  assert.equal(moneyValue('(24.99)').value, -24.99);
  assert.equal(moneyValue('-$1,024.00').value, -1024);
  assert.equal(moneyValue('20.00 CR').credit, true);
  assert.equal(parseLine('10/03 PAYMENT THANK YOU', today), null, 'no amount');
});

test('plain statement text finds the subscriptions and keeps income out', () => {
  const text = [
    'Statement period Aug 1 - Nov 1', 'Date Description Amount Balance',
    ...['08', '09', '10'].flatMap((m) => [`${m}/03 NETFLIX.COM 866-579-7172 CA 15.49 1,234.56`, `${m}/09 SPOTIFY USA *P${m}A9 11.99`, `${m}/01 PAYROLL DIRECT DEP 2,650.00`, `${m}/14 PLANET FITNESS #1022 24.99`]),
    '10/20 BEST BUY 00123 129.99', '11/02 AMAZON MKTPLACE 20.00 CR',
  ].join('\n');
  const r = parseStatement(text, { today });
  assert.equal(r.format, 'text');
  assert.equal(r.transactions.length, 14);
  assert.ok(r.transactions.filter((t) => /PAYROLL|AMAZON/.test(t.note)).every((t) => t.amount < 0), 'income and credits are not spending');
  const subs = findRecurring(r.transactions, { today }).subscriptions.map((s) => s.name);
  for (const name of ['NETFLIX', 'SPOTIFY', 'PLANET FITNESS']) assert.ok(subs.some((n) => n.toUpperCase().includes(name)), name);
  assert.ok(!subs.some((n) => /PAYROLL|BEST BUY/.test(n)));
});

test('online banking with spending shown negative', () => {
  const r = parseStatement('Oct 3 NETFLIX.COM -15.49\nSep 3 NETFLIX.COM -15.49\nOct 1 EMPLOYER PAYROLL 2,650.00', { today });
  assert.deepEqual(r.transactions.map((t) => t.amount), [15.49, 15.49, -2650]);
});

test('pasted CSV and tab-separated tables go through the CSV reader', () => {
  const csv = parseStatement('Date,Description,Amount\n10/03/2026,NETFLIX.COM,-15.49\n09/03/2026,NETFLIX.COM,-15.49', { today });
  assert.equal(csv.format, 'csv');
  assert.equal(csv.transactions.length, 2);
  const tab = parseStatement('Date\tDescription\tAmount\n10/03/2026\tNETFLIX.COM\t-15.49\n09/03/2026\tSPOTIFY, USA\t-11.99', { today });
  assert.equal(tab.format, 'table');
  assert.deepEqual(tab.transactions.map((t) => t.note), ['NETFLIX.COM', 'SPOTIFY, USA']);
});

test('empty or unreadable pastes explain what to do', () => {
  assert.match(parseStatement('', { today }).error, /Paste/);
  assert.match(parseStatement('hello there\nnothing here', { today }).error, /start with a date/);
  const html = readFileSync(new URL('../subscriptions.html', import.meta.url), 'utf8');
  assert.match(html, /id="paste-form"/);
  assert.match(html, /Nothing is uploaded/);
});
