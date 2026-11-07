import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import * as S from '../lib/setaside.js';

test('set-aside rate: SE tax + income tax after half SE and QBI + state, minus costs', () => {
  const r = S.rate({ bracket: 22, stateRate: 5, costsPct: 0 });
  assert.ok(Math.abs(r.se - 0.153 * 0.9235) < 1e-9);
  assert.ok(Math.abs(r.income - 0.22 * (1 - (0.153 * 0.9235) / 2) * 0.8) < 1e-9);
  assert.equal(r.pct, 36);
  assert.equal(S.rate({ bracket: 12, costsPct: 10 }).pct, 21);
  assert.equal(S.rate({ bracket: 0, costsPct: 100 }).pct, 0);
  assert.equal(S.setAside(1500, 21), 315);
});

test('2026 estimated tax periods and due dates (Form 1040-ES)', () => {
  assert.deepEqual(S.QUARTERS[2026].map((q) => q.due), ['2026-04-15', '2026-06-15', '2026-09-15', '2027-01-15']);
  assert.equal(S.quarterOf('2026-05-31').q, 2);
  assert.equal(S.quarterOf('2026-06-01').q, 3);
  assert.equal(S.quarterOf('2026-12-31').due, '2027-01-15');
  assert.equal(S.QUARTERS[2027][3].due, '2028-01-18', 'Jan 15 2028 is a Saturday, Jan 17 is MLK Day');
  assert.equal(S.quarterOf('2030-01-01'), null);
});

test('next due date and days left', () => {
  assert.deepEqual([S.nextDue('2026-11-07').year, S.nextDue('2026-11-07').q], [2026, 4]);
  assert.equal(S.nextDue('2027-01-15').due, '2027-01-15');
  assert.deepEqual([S.nextDue('2027-01-16').year, S.nextDue('2027-01-16').q], [2027, 1]);
  assert.equal(S.daysUntil('2026-11-07', '2027-01-15'), 69);
  assert.equal(S.nextDue('2028-02-01'), null);
});

test('quarter totals, sent amounts and safe harbor', () => {
  const qs = S.quarters([{ date: '2026-10-02', amount: 2000, pct: 25 }, { date: '2026-02-01', amount: 1000, pct: 20 }, { date: '2025-12-01', amount: 9, pct: 50 }], 2026, { '2026-Q4': 100 });
  assert.deepEqual(qs.map((q) => [q.income, q.reserved, q.sent]), [[1000, 200, 0], [0, 0, 0], [0, 0, 0], [2000, 500, 100]]);
  assert.deepEqual(S.yearTotals(qs), { income: 3000, reserved: 700, sent: 100, stillHeld: 600 });
  assert.deepEqual(S.safeHarbor(8000), { year: 8000, quarter: 2000 });
  assert.deepEqual(S.safeHarbor(8000, true), { year: 8800, quarter: 2200 });
  assert.equal(S.safeHarbor(''), null);
});

test('PWA: manifest, icons and offline cache list point at real files', () => {
  const base = new URL('../set-aside/', import.meta.url);
  const m = JSON.parse(readFileSync(new URL('manifest.webmanifest', base), 'utf8'));
  assert.equal(m.display, 'standalone');
  assert.equal(m.scope, './');
  for (const i of m.icons) assert.ok(existsSync(new URL(i.src, base)), i.src);
  assert.ok(m.icons.some((i) => i.sizes === '512x512'));
  const sw = readFileSync(new URL('sw.js', base), 'utf8');
  const shell = JSON.parse(/const SHELL = (\[.*?\]);/s.exec(sw)[1].replace(/'/g, '"'));
  for (const f of shell) assert.ok(existsSync(new URL(f === './' ? 'index.html' : f, base)), f);
  assert.doesNotMatch(readFileSync(new URL('app.js', base), 'utf8'), /fetch\(/, 'no network calls from the app');
});
