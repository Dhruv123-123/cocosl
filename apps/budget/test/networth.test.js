import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import * as N from '../lib/networth.js';
import { buildPdf, pdfText, wrap } from '../lib/pdf.js';

const sample = () => {
  const s = N.emptySheet();
  N.addItem(s, { side: 'asset', kind: 'cash', name: 'Savings', value: '4,800' });
  N.addItem(s, { side: 'asset', kind: 'retirement', name: '401(k)', value: '22000' });
  N.addItem(s, { side: 'debt', kind: 'card', name: 'Visa', value: '$3,200' });
  N.addItem(s, { side: 'debt', kind: 'student', name: '', value: '18000' });
  return s;
};

test('totals, categories and the debt ratio', () => {
  const s = sample();
  const t = N.totals(s);
  assert.deepEqual([t.assets, t.debts, t.net, t.debtRatio, t.liquid], [26800, 21200, 5600, 79, 4800]);
  assert.deepEqual(t.debtsByKind.map((d) => [d.kind, d.total]), [['card', 3200], ['student', 18000]]);
  assert.equal(s.items[3].name, 'Student loans', 'blank names use the category');
  assert.throws(() => N.addItem(s, { side: 'asset', value: '-5' }), /\$0 or more/);
  assert.throws(() => N.addItem(s, { side: 'maybe', value: '5' }), /own or owe/);
  N.updateItem(s, s.items[2].id, '1200');
  assert.equal(N.totals(s).net, 7600);
  N.removeItem(s, s.items[0].id);
  assert.equal(N.totals(s).debtRatio, 87);
});

test('snapshots: one per day, trend since last and first', () => {
  const s = sample();
  assert.equal(N.trend(s), null);
  N.takeSnapshot(s, '2026-09-01');
  N.updateItem(s, s.items[2].id, '2200');
  N.takeSnapshot(s, '2026-10-01');
  N.updateItem(s, s.items[0].id, '5800');
  N.takeSnapshot(s, '2026-11-01');
  N.takeSnapshot(s, '2026-11-01');
  assert.equal(s.snapshots.length, 3, 'saving twice on a day replaces it');
  assert.deepEqual(N.trend(s), { sincePrev: 1000, prevDate: '2026-10-01', sinceFirst: 2000, firstDate: '2026-09-01', count: 3 });
  N.removeSnapshot(s, '2026-10-01');
  assert.equal(N.trend(s).sincePrev, 2000);
  const back = N.loadSheet(JSON.stringify(s));
  assert.deepEqual(back, s);
  assert.deepEqual(N.loadSheet('{oops'), N.emptySheet());
});

test('notes in plain words', () => {
  const s = sample();
  assert.match(N.notes(s).join(' '), /Credit card debt/);
  assert.match(N.notes(s, 2400).join(' '), /about 2 months of essential costs/);
  const neg = N.emptySheet();
  N.addItem(neg, { side: 'debt', kind: 'student', value: '30000' });
  assert.match(N.notes(neg).join(' '), /negative, which is common/);
  assert.match(N.toCsv(s), /^"Type","Category","Name","Value"\r\n"Own","Cash and savings","Savings","4800"/);
});

test('the PDF is a valid, readable file with the numbers in it', () => {
  const lines = [{ text: 'Net worth snapshot', size: 20, bold: true }, { rule: true }, { text: 'Net worth · “today”', right: '$5,600.00' }, ...Array.from({ length: 60 }, (_, i) => ({ text: `Line ${i} (with parens) and a backslash \\`, right: '$1.00' }))];
  const bytes = buildPdf(lines, { title: 'Test report' });
  const text = String.fromCharCode(...bytes);
  assert.match(text, /^%PDF-1\.4/);
  assert.match(text, /%%EOF\n$/);
  assert.match(text, /\/Count 2 /, 'long reports flow onto a second page');
  assert.match(text, /\(\$5,600\.00\) Tj/);
  assert.match(text, /\(Net worth \xb7 "today"\) Tj/);
  assert.match(text, /\(Line 3 \\\(with parens\\\) and a backslash \\\\\) Tj/);
  // Every xref offset points at its object.
  const xref = Number(/startxref\n(\d+)/.exec(text)[1]);
  const offsets = text.slice(xref).split('\n').slice(3).filter((l) => / 00000 n $/.test(l)).map((l) => Number(l.slice(0, 10)));
  offsets.forEach((o, i) => assert.equal(text.slice(o, o + `${i + 1} 0 obj`.length), `${i + 1} 0 obj`));
  assert.equal(pdfText('日本'), '??');
  assert.ok(wrap('word '.repeat(80), 11, 300).length > 3);
});

test('page: saved locally only, PDF export, Budget Pro slot', () => {
  const html = readFileSync(new URL('../networth.html', import.meta.url), 'utf8');
  const js = readFileSync(new URL('../networth.js', import.meta.url), 'utf8');
  assert.match(html, /never sent to a server/);
  assert.match(html, /href="pricing\.html\?from=networth" data-upgrade="networth"/);
  assert.match(js, /buildPdf/);
  assert.doesNotMatch(js, /fetch\(|XMLHttpRequest|sendBeacon/);
});
