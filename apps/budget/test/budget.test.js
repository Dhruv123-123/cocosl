import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as b from '../lib/budget.js';
import { PLANS, planFor, can } from '../lib/plans.js';

const NOW = new Date('2026-11-07T12:00:00Z');

test('new state has default categories and the current month', () => {
  const s = b.createState(NOW);
  assert.equal(s.categories.length, 8);
  assert.ok(s.months['2026-11']);
});

test('summary: plan, spend, left and unassigned', () => {
  const s = b.createState(NOW);
  const [rent, groceries] = s.categories;
  b.setIncome(s, '2026-11', 3000);
  b.setPlan(s, '2026-11', rent.id, 1200);
  b.setPlan(s, '2026-11', groceries.id, 400);
  b.addTransaction(s, { date: '2026-11-01', amount: 1200, categoryId: rent.id });
  b.addTransaction(s, { date: '2026-11-03', amount: 455.5, categoryId: groceries.id });
  b.addTransaction(s, { date: '2026-11-04', amount: -20, categoryId: groceries.id, note: 'refund' });
  b.addTransaction(s, { date: '2026-10-30', amount: 99, categoryId: groceries.id }); // other month
  const sum = b.summarize(s, '2026-11');
  assert.equal(sum.planned, 1600);
  assert.equal(sum.unassigned, 1400);
  assert.equal(sum.spent, 1635.5);
  const g = sum.rows.find((r) => r.id === groceries.id);
  assert.equal(g.spent, 435.5);
  assert.equal(g.left, -35.5);
  assert.equal(g.over, true);
  assert.equal(sum.rows.find((r) => r.id === rent.id).over, false);
  assert.equal(sum.transactions.length, 3);
});

test('50/30/20 split check', () => {
  const s = b.createState(NOW);
  b.setIncome(s, '2026-11', 4000);
  const needs = s.categories.find((c) => c.group === 'needs');
  const save = s.categories.find((c) => c.group === 'savings');
  b.setPlan(s, '2026-11', needs.id, 2000);
  b.setPlan(s, '2026-11', save.id, 800);
  const split = b.summarize(s, '2026-11').split;
  assert.equal(split.needs.pct, 50);
  assert.equal(split.savings.pct, 20);
  assert.equal(split.wants.pct, 0);
});

test('a new month copies the previous plan', () => {
  const s = b.createState(NOW);
  b.setIncome(s, '2026-11', 2500);
  b.setPlan(s, '2026-11', s.categories[0].id, 900);
  b.ensureMonth(s, '2026-12');
  assert.equal(s.months['2026-12'].income, 2500);
  assert.equal(s.months['2026-12'].plan[s.categories[0].id], 900);
  s.months['2026-12'].plan[s.categories[0].id] = 1;
  assert.equal(s.months['2026-11'].plan[s.categories[0].id], 900, 'copy, not shared reference');
});

test('category limits and duplicates', () => {
  const s = b.createState(NOW);
  b.addCategory(s, 'Pets', 'needs', { limit: 10 });
  b.addCategory(s, 'Gifts', 'wants', { limit: 10 });
  assert.throws(() => b.addCategory(s, 'Travel', 'wants', { limit: 10 }), b.LimitError);
  assert.throws(() => b.addCategory(s, 'pets'), /already exists/);
  assert.throws(() => b.addCategory(s, '  '), /name/);
});

test('removing a category uncategorises its transactions', () => {
  const s = b.createState(NOW);
  const c = s.categories[4];
  b.addTransaction(s, { date: '2026-11-05', amount: 12, categoryId: c.id });
  b.removeCategory(s, c.id);
  assert.equal(s.transactions[0].categoryId, null);
  assert.equal(b.summarize(s, '2026-11').uncategorized, 12);
});

test('transaction validation', () => {
  const s = b.createState(NOW);
  assert.throws(() => b.addTransaction(s, { date: '11/7/2026', amount: 5 }), /date/);
  assert.throws(() => b.addTransaction(s, { date: '2026-11-07', amount: 0 }), /amount/);
});

test('loadState survives garbage and keeps good data', () => {
  assert.equal(b.loadState('not json', NOW).categories.length, 8);
  assert.equal(b.loadState('{"foo":1}', NOW).categories.length, 8);
  const s = b.createState(NOW);
  b.addTransaction(s, { date: '2026-11-02', amount: 3 });
  assert.equal(b.loadState(JSON.stringify(s), NOW).transactions.length, 1);
});

test('goal plan', () => {
  const g = b.goalPlan({ target: 1200, saved: 200, deadline: '2027-05' }, NOW);
  assert.equal(g.months, 6);
  assert.equal(g.monthly, 166.67);
});

test('CSV parser handles quotes, commas and newlines', () => {
  const rows = b.parseCsv('a,b,c\r\n"x, y","He said ""hi""","line1\nline2"\n');
  assert.deepEqual(rows, [['a', 'b', 'c'], ['x, y', 'He said "hi"', 'line1\nline2']]);
});

test('bank CSV with one signed amount column (spending negative)', () => {
  const csv = 'Transaction Date,Description,Amount\n11/01/2026,"KROGER #123",-54.20\n11/02/2026,PAYROLL,2100.00\n11/03/2026,STARBUCKS,-6.45\n11/04/2026,"AMAZON, MKTP",-19.99\n';
  const { transactions, skipped } = b.importBankCsv(csv);
  assert.equal(skipped, 0);
  assert.deepEqual(transactions.map((t) => t.amount), [54.2, -2100, 6.45, 19.99]);
  assert.equal(transactions[0].date, '2026-11-01');
  assert.equal(transactions[3].note, 'AMAZON, MKTP');
});

test('bank CSV with debit and credit columns', () => {
  const csv = 'Date,Payee,Debit,Credit\n2026-11-01,Rent,1200.00,\n2026-11-02,Refund,,15.00\nbad,row,1,\n';
  const { transactions, skipped } = b.importBankCsv(csv);
  assert.deepEqual(transactions.map((t) => t.amount), [1200, -15]);
  assert.equal(skipped, 1);
});

test('bank CSV without the needed columns explains why', () => {
  assert.match(b.importBankCsv('foo,bar\n1,2\n').error, /Date and Amount/);
});

test('category guessing', () => {
  const s = b.createState(NOW);
  const id = b.guessCategory(s, 'KROGER #123 CINCINNATI');
  assert.equal(s.categories.find((c) => c.id === id).name, 'Groceries');
  assert.equal(b.guessCategory(s, 'zzz unknown'), null);
});

test('CSV export escapes fields', () => {
  const s = b.createState(NOW);
  b.addTransaction(s, { date: '2026-11-02', amount: 3.5, categoryId: s.categories[1].id, note: 'milk, "fresh"' });
  assert.equal(b.exportCsv(s), 'Date,Amount,Category,Note\n2026-11-02,3.50,Groceries,"milk, ""fresh"""\n');
});

test('plans gate Pro features', () => {
  assert.equal(planFor(null), PLANS.free);
  assert.equal(planFor({ valid: true }), PLANS.pro);
  assert.equal(can(null, 'csvImport'), false);
  assert.equal(can({ valid: true }, 'csvImport'), true);
  assert.equal(can(null, 'backup'), true);
});
