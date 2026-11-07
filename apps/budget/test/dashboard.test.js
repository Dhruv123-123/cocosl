import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { importBankCsv } from '../lib/budget.js';
import { categorize, buildDashboard, workbookSheets, CATEGORIES, catName } from '../lib/dashboard.js';
import { buildXlsx, crc32, colName, dateSerial, sheetName } from '../lib/xlsx.js';

// Read a stored (uncompressed) ZIP back into { name: text }.
function unzip(bytes) {
  const dv = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  const out = {}; let p = 0; const dec = new TextDecoder();
  while (dv.getUint32(p, true) === 0x04034b50) {
    assert.equal(dv.getUint16(p + 8, true), 0, 'stored method');
    const size = dv.getUint32(p + 18, true); const nl = dv.getUint16(p + 26, true); const xl = dv.getUint16(p + 28, true);
    const name = dec.decode(bytes.slice(p + 30, p + 30 + nl));
    const data = bytes.slice(p + 30 + nl + xl, p + 30 + nl + xl + size);
    assert.equal(crc32(data), dv.getUint32(p + 14, true), `crc ${name}`);
    out[name] = dec.decode(data);
    p += 30 + nl + xl + size;
  }
  assert.equal(dv.getUint32(p, true), 0x02014b50, 'central directory follows');
  return out;
}

const CSV = `Date,Description,Amount
09/01/2026,PAYROLL DIRECT DEP ACME,2650.00
09/02/2026,PARKVIEW APTS RENT,-1400.00
09/03/2026,NETFLIX.COM 866-579-7172 CA,-15.49
09/05/2026,KROGER #555,-82.10
09/07/2026,SHELL OIL 5744,-41.00
09/09/2026,UBER EATS 8005928996,-22.00
09/10/2026,ONLINE TRANSFER TO SAVINGS,-200.00
09/12/2026,CHASE CREDIT CRD AUTOPAY,-350.00
09/18/2026,MYSTERY SHOP LLC,-25.00
10/01/2026,PAYROLL DIRECT DEP ACME,2650.00
10/04/2026,AMAZON MKTPL*AB12,-63.20
10/05/2026,AMAZON REFUND,20.00
10/08/2026,OVERDRAFT FEE,-35.00
10/09/2026,ZELLE FROM MOM,50.00
`;

test('crc32 and helpers', () => {
  assert.equal(crc32(new TextEncoder().encode('123456789')), 0xcbf43926);
  assert.deepEqual([0, 25, 26, 27, 701, 702].map(colName), ['A', 'Z', 'AA', 'AB', 'ZZ', 'AAA']);
  assert.equal(dateSerial('1900-03-01'), 61);
  assert.equal(dateSerial('2026-11-07'), 46333);
  assert.equal(dateSerial('nope'), null);
  assert.equal(sheetName('a/b:c?'), 'a b c');
  assert.equal(sheetName('x'.repeat(40)).length, 31);
});

test('categorize: the common bank descriptions', () => {
  const cases = [
    ['PAYROLL DIRECT DEP ACME', -2650, 'income'], ['PARKVIEW APTS RENT', 1400, 'housing'], ['NETFLIX.COM 866-579-7172 CA', 15.49, 'subscriptions'],
    ['KROGER #555', 82.1, 'groceries'], ['SHELL OIL 5744', 41, 'transport'], ['UBER EATS 8005928996', 22, 'dining'], ['UBER TRIP HELP.UBER.COM', 14, 'transport'],
    ['ONLINE TRANSFER TO SAVINGS', 200, 'savings'], ['CHASE CREDIT CRD AUTOPAY', 350, 'transfers'], ['Payment Thank You - Web', -350, 'transfers'],
    ['AMAZON MKTPL*AB12', 63.2, 'shopping'], ['AMAZON REFUND', -20, 'shopping'], ['OVERDRAFT FEE', 35, 'fees'], ['ZELLE FROM MOM', -50, 'transfers'],
    ['NAVIENT ED LOAN', 210, 'debt'], ['GEICO AUTO', 128, 'insurance'], ['CVS/PHARMACY #0441', 18.4, 'health'], ['ATM WITHDRAWAL 1234', 60, 'cash'],
    ['VANGUARD BUY', 500, 'savings'], ['MYSTERY SHOP LLC', 25, 'other'], ['IRS TREAS 310 TAX REF', -1200, 'income'], ['SOME CO DEPOSIT', -80, 'income'],
    ['PAGO DE NOMINA', -1800, 'income'], ['SUPERMERCADO EL SOL', 45, 'groceries'],
  ];
  for (const [note, amount, want] of cases) assert.equal(categorize(note, amount), want, note);
  assert.equal(categorize('MYSTERY SHOP LLC #22', 25, { 'mystery shop llc': 'fun' }), 'fun', 'remembered choice wins');
  assert.equal(categorize('MYSTERY SHOP LLC', 25, { 'mystery shop llc': 'bogus' }), 'other', 'unknown override ignored');
});

test('buildDashboard: monthly totals, refunds, transfers not counted', () => {
  const d = buildDashboard(importBankCsv(CSV).transactions);
  assert.deepEqual(d.months, ['2026-09', '2026-10']);
  assert.deepEqual(d.totals['2026-09'], { income: 2650, spend: 1585.59, save: 200, left: 864.41 });
  assert.equal(d.byCat.shopping['2026-10'], 43.2, 'refund lowers shopping');
  assert.equal(d.byCat.transfers['2026-09'], 350);
  assert.equal(d.byCat.transfers['2026-10'], -50);
  assert.equal(d.totals['2026-10'].income, 2650, 'Zelle from family is not income');
  assert.deepEqual(d.uncategorized.map((u) => u.merchant), ['mystery shop llc']);
  const withRule = buildDashboard(importBankCsv(CSV).transactions, { overrides: { 'mystery shop llc': 'fun' } });
  assert.equal(withRule.uncategorized.length, 0);
  assert.equal(withRule.byCat.fun['2026-09'], 25);
});

test('buildDashboard keeps the latest 12 months', () => {
  const tx = Array.from({ length: 15 }, (_, i) => ({ date: `${2025 + Math.floor(i / 12)}-${String((i % 12) + 1).padStart(2, '0')}-10`, amount: 10, note: 'KROGER' }));
  const d = buildDashboard(tx);
  assert.equal(d.months.length, 12);
  assert.equal(d.months[0], '2025-04');
  assert.equal(d.droppedMonths, 3);
});

test('importBankCsv reads Spanish headers', () => {
  const es = importBankCsv('Fecha,Descripción,Monto\n10/01/2026,NOMINA ACME,1800.00\n10/02/2026,EL SUPER #12,-45.10\n');
  assert.equal(es.error, undefined);
  assert.deepEqual(es.transactions.map((t) => t.amount), [-1800, 45.1]);
  const split = importBankCsv('Fecha,Concepto,Cargo,Abono\n10/01/2026,NOMINA,,1800.00\n10/02/2026,FARMACIA,20.00,\n');
  assert.deepEqual(split.transactions.map((t) => [t.note, t.amount]), [['NOMINA', -1800], ['FARMACIA', 20]]);
});

test('workbook: four sheets, live formulas with cached values, dropdown, escaping', () => {
  const tx = importBankCsv(CSV + '10/10/2026,"=CMD() <b>&""x""\u0007",-5.00\n').transactions;
  const d = buildDashboard(tx);
  const sheets = workbookSheets(d, { made: '2026-11-07', budgets: { groceries: 400 } });
  assert.deepEqual(sheets.map((s) => s.name), ['Summary', 'Transactions', 'Categories', 'How to use']);
  const files = unzip(buildXlsx(sheets, { title: 'Money dashboard' }));
  for (const f of ['[Content_Types].xml', '_rels/.rels', 'xl/workbook.xml', 'xl/_rels/workbook.xml.rels', 'xl/styles.xml', 'xl/sharedStrings.xml', 'xl/worksheets/sheet1.xml', 'xl/worksheets/sheet4.xml']) assert.ok(files[f], f);
  const summary = files['xl/worksheets/sheet1.xml'];
  assert.match(summary, /<f>SUMIFS\('Transactions'!\$E\$2:\$E\$\d+,'Transactions'!\$D\$2:\$D\$\d+,\$A5,'Transactions'!\$B\$2:\$B\$\d+,B\$4\)<\/f><v>2650<\/v>/);
  assert.match(summary, /<f>-SUMIFS\(/);
  assert.match(summary, /<pane xSplit="1" ySplit="4"/);
  const tsheet = files['xl/worksheets/sheet2.xml'];
  assert.match(tsheet, /<dataValidation type="list"[^>]*sqref="D2:D\d+"><formula1>'Categories'!\$A\$2:\$A\$\d+<\/formula1>/);
  assert.match(tsheet, /<autoFilter ref="A1:E\d+"\/>/);
  assert.match(tsheet, /<c r="A2" s="3"><v>46266<\/v><\/c>/, 'dates are real dates');
  // Descriptions are text, never formulas, and XML-escaped with control characters dropped.
  assert.doesNotMatch(tsheet, /<f>CMD/);
  assert.ok(files['xl/sharedStrings.xml'].includes('=CMD() &lt;b&gt;&amp;&quot;x&quot;</t>'));
  assert.doesNotMatch(files['xl/sharedStrings.xml'], /\u0007/);
  assert.match(files['xl/workbook.xml'], /fullCalcOnLoad="1"/);
  // Every category the summary looks up is in the Categories list.
  for (const c of CATEGORIES) assert.ok(files['xl/sharedStrings.xml'].includes(`>${catName(c.key, 'en').replace(/&/g, '&amp;')}<`), c.key);
});

test('workbook in Spanish uses Spanish sheet names and labels', () => {
  const d = buildDashboard(importBankCsv(CSV).transactions);
  const sheets = workbookSheets(d, { lang: 'es', made: '2026-11-07' });
  assert.deepEqual(sheets.map((s) => s.name), ['Resumen', 'Movimientos', 'Categorías', 'Cómo usarlo']);
  const files = unzip(buildXlsx(sheets));
  assert.match(files['xl/worksheets/sheet1.xml'], /SUMIFS\('Movimientos'!/);
  assert.ok(files['xl/sharedStrings.xml'].includes('>Supermercado<'));
  assert.ok(files['xl/sharedStrings.xml'].includes('>Te sobra<'));
});

test('pages: both languages, linked to each other, nothing uploaded', () => {
  const read = (f) => readFileSync(new URL(`../${f}`, import.meta.url), 'utf8');
  const en = read('money-dashboard.html'); const es = read('tablero-dinero.html'); const js = read('money-dashboard.js');
  assert.match(en, /<html lang="en">/); assert.match(es, /<html lang="es">/);
  assert.ok(en.includes('href="tablero-dinero.html"') && es.includes('href="money-dashboard.html"'));
  for (const f of ['money-dashboard.html', 'tablero-dinero.html', 'money-dashboard.js', 'lib/dashboard.js', 'lib/xlsx.js']) assert.ok(read('sw.js').includes(`'${f}'`), f);
  assert.doesNotMatch(js + read('lib/dashboard.js') + read('lib/xlsx.js'), /fetch\(|XMLHttpRequest|sendBeacon/);
});
