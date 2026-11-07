import { test } from 'node:test';
import assert from 'node:assert/strict';
import { findRecurring, merchantKey } from '../lib/recurring.js';
import { importBankCsv } from '../lib/budget.js';

const monthly = (note, amount, months, day = 5) =>
  months.map((m) => ({ date: `2026-${String(m).padStart(2, '0')}-${String(day).padStart(2, '0')}`, amount, note: note.replace('{m}', String(m)) }));

test('merchant names are normalised across messy bank descriptions', () => {
  assert.equal(merchantKey('POS DEBIT 11/03 NETFLIX.COM 866-579-7172 CA'), 'netflix.com');
  assert.equal(merchantKey('NETFLIX.COM #4821'), 'netflix.com');
  assert.equal(merchantKey('Spotify USA *P2A9C3'), 'spotify');
});

test('finds monthly subscriptions, ignores one-offs and regular groceries', () => {
  const txs = [
    ...monthly('NETFLIX.COM {m}/05 CA', 15.49, [6, 7, 8, 9, 10, 11]),
    ...monthly('PLANET FITNESS #{m}22', 24.99, [7, 8, 9, 10, 11], 17),
    { date: '2026-09-02', amount: 499, note: 'BEST BUY 00123' },
    ...[1, 8, 15, 22, 29].map((d) => ({ date: `2026-10-${String(d).padStart(2, '0')}`, amount: 40 + d, note: 'KROGER #555' })),
    { date: '2026-10-03', amount: -2100, note: 'PAYROLL' },
  ];
  const r = findRecurring(txs);
  assert.deepEqual(r.subscriptions.map((s) => s.key).sort(), ['netflix.com', 'planet fitness']);
  const n = r.subscriptions.find((s) => s.key === 'netflix.com');
  assert.equal(n.cadence, 'monthly');
  assert.equal(n.yearly, 185.88);
  assert.equal(n.confidence, 'very likely');
  assert.equal(r.yearlyTotal, round(185.88 + 24.99 * 12));
});

test('flags price increases', () => {
  const txs = [...monthly('SPOTIFY USA', 10.99, [7, 8, 9]), ...monthly('SPOTIFY USA', 11.99, [10, 11])];
  const s = findRecurring(txs).subscriptions[0];
  assert.equal(s.priceChange, 1);
  assert.equal(s.amount, 11.99);
});

test('yearly renewals and stale (cancelled) subscriptions', () => {
  const txs = [
    { date: '2024-03-10', amount: 99, note: 'AMAZON PRIME*AB12' }, { date: '2025-03-10', amount: 139, note: 'AMAZON PRIME*CD34' },
    ...monthly('HULU 877-824-4858', 7.99, [1, 2, 3]),
  ];
  const r = findRecurring(txs, { today: '2026-11-07' });
  const prime = r.subscriptions.find((s) => s.key.startsWith('amazon prime'));
  assert.equal(prime.cadence, 'yearly');
  const hulu = r.subscriptions.find((s) => s.key === 'hulu');
  assert.equal(hulu.stale, true);
  assert.equal(r.yearlyTotal, 0, 'stale ones and a lapsed yearly are excluded from the total');
});

test('works end to end from a bank CSV export', () => {
  const csv = ['Date,Description,Amount',
    ...[6, 7, 8, 9].map((m) => `${m}/12/2026,"DISNEY PLUS 888-905-7888",-13.99`),
    '9/14/2026,TARGET 0021,-63.10', '10/01/2026,DIRECT DEPOSIT,2500.00'].join('\n');
  const r = findRecurring(importBankCsv(csv).transactions);
  assert.equal(r.subscriptions.length, 1);
  assert.equal(r.subscriptions[0].name, 'Disney Plus');
  assert.equal(r.subscriptions[0].nextDate, '2026-10-12');
});

function round(n) { return Math.round(n * 100) / 100; }
