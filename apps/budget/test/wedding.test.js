import { test } from 'node:test';
import assert from 'node:assert/strict';
import { CATEGORIES, splitBudget, monthsUntil, summary, weddingCsv, weddingTsv, nameOf } from '../lib/wedding.js';

test('shares add up to 100% and the split adds up to the total exactly', () => {
  assert.equal(Math.round(CATEGORIES.reduce((t, c) => t + c[1], 0) * 1000), 1000);
  for (const total of [15000, 30000, 33333]) {
    const s = splitBudget(total);
    assert.equal(Object.values(s).reduce((a, b) => a + b, 0), total);
  }
  assert.equal(splitBudget(30000).venue, 4800);
  assert.equal(splitBudget(30000).catering, 6000);
  assert.equal(splitBudget(30000).honeymoon, 0);
});

test('months to save', () => {
  assert.equal(monthsUntil('2026-11-07', '2027-09-18'), 10);
  assert.equal(monthsUntil('2026-11-07', '2026-11-20'), 1);
  assert.equal(monthsUntil('2026-11-07', '2026-10-01'), 0);
});

test('summary uses actual, then estimate, then budget; per guest and monthly saving', () => {
  const rows = Object.fromEntries(Object.entries(splitBudget(30000)).map(([k, b]) => [k, { budget: b }]));
  rows.venue = { budget: 4800, estimate: 6300, paid: 2000 };
  rows.photo = { budget: 2400, estimate: 2200, actual: 2300, paid: 2300 };
  const s = summary({ total: 30000, guests: 100, date: '2027-09-18', saved: 4000, rows }, '2026-11-07');
  assert.equal(s.expected, 31400); // 30000 + 1500 (venue over) - 100 (photo under)
  assert.equal(s.left, -1400);
  assert.deepEqual(s.overRows, ['venue']);
  assert.equal(s.paid, 4300);
  assert.equal(s.owed, 27100);
  assert.equal(s.perGuest, 314);
  assert.equal(s.venuePerGuest, 141); // (6300 + 6000 + 1800) / 100
  assert.equal(s.monthly, 2310); // (27100 - 4000) / 10
});

test('exports in the spreadsheet column order, both languages', () => {
  const s = summary({ total: 20000, rows: { venue: { budget: 8000, paid: 1000 }, bar: { budget: 900, estimate: 1100 } } }, '2026-11-07');
  assert.match(weddingCsv(s), /^Category,Budget,Estimate,Actual,Paid,Still owed\r\nVenue,8000,,,1000,7000\r\n/);
  assert.match(weddingCsv(s), /\r\nBar and drinks,900,1100,,,1100\r\n/);
  assert.match(weddingCsv(s, 'es'), /^Categoría,Presupuesto/);
  const tsv = weddingTsv(s).split('\n');
  assert.equal(tsv.length, 20);
  assert.equal(tsv[0], 'Venue\t8000\t\t1000');
  assert.equal(tsv[2], 'Bar and drinks\t900\t1100\t');
  assert.equal(nameOf('cake', 'es'), 'Pastel y postres');
});
