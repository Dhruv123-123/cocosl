import { test } from 'node:test';
import assert from 'node:assert/strict';
import { emptySheet, addItem, takeSnapshot, netWorthSheet } from '../lib/networth.js';
import { buildXlsx } from '../lib/xlsx.js';
import { buildDashboard, workbookSheets } from '../lib/dashboard.js';

function sample() {
  const s = emptySheet();
  addItem(s, { side: 'asset', kind: 'cash', name: 'Savings', value: 4800 });
  addItem(s, { side: 'debt', kind: 'card', name: 'Visa', value: 1200 });
  addItem(s, { side: 'asset', kind: 'vehicle', name: 'Car', value: 9000 });
  takeSnapshot(s, '2026-10-01');
  s.items[0].value = 5300;
  takeSnapshot(s, '2026-11-01');
  return s;
}

test('net worth sheet: totals are SUMIF formulas over the item rows only, snapshots compute change', () => {
  const sh = netWorthSheet(sample());
  const cells = sh.rows.flat().filter((c) => c && c.f);
  const owned = cells.find((c) => /"Own"/.test(c.f));
  assert.match(owned.f, /^SUMIF\(\$A\$5:\$A\$7,"Own",\$D\$5:\$D\$7\)$/);
  assert.equal(owned.v, 14300);
  const net = cells.find((c) => /^D\d+-D\d+$/.test(c.f) && c.s === 'total');
  assert.equal(net.v, 13100);
  const change = cells.filter((c) => /^D(\d+)-D(\d+)$/.test(c.f) && c.s === 'money');
  assert.equal(change.length, 1);
  assert.equal(change[0].v, 500);
  // The owned total's own row is outside its range (no circular reference).
  const ownedRow = sh.rows.findIndex((r) => r && r.includes(owned)) + 1;
  assert.ok(ownedRow > 7);
});

test('Spanish labels and an empty tracker', () => {
  const sh = netWorthSheet(sample(), { lang: 'es' });
  assert.equal(sh.name, 'Patrimonio');
  assert.ok(sh.rows.flat().some((c) => c && c.f && /"Tienes"/.test(c.f)));
  assert.ok(netWorthSheet(emptySheet()).rows.length > 5);
});

test('the dashboard workbook takes the net worth tab before How to use, and the file builds', () => {
  const dash = buildDashboard([{ date: '2026-10-03', amount: 2500, note: 'PAYROLL' }, { date: '2026-10-05', amount: -80, note: 'KROGER' }]);
  const sheets = workbookSheets(dash, { extra: [netWorthSheet(sample())] });
  assert.deepEqual(sheets.map((s) => s.name), ['Summary', 'Transactions', 'Categories', 'Net worth', 'How to use']);
  const bytes = buildXlsx(sheets, { title: 'Test' });
  assert.ok(bytes.length > 2000);
});
