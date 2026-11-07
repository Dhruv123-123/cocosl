import { test } from 'node:test';
import assert from 'node:assert/strict';
import { CATEGORIES, estimates, summary, movingCsv, movingTsv, nameOf } from '../lib/moving.js';

test('the 11 categories in the Moving Budget Sheet order', () => {
  assert.deepEqual(CATEGORIES.map((c) => c[1]), ['Movers or truck rental', 'Fuel and mileage', 'Packing supplies', 'Storage', 'Travel and lodging', 'Deposits (new place)', 'Overlap rent', 'Utility setup', 'Cleaning', 'Time off work', 'Buffer']);
});

test('local DIY move, 2 bedrooms', () => {
  const e = estimates({ miles: 20, size: '2br', method: 'diy', cars: 1, newRent: 1500, depositMonths: 1, overlapDays: 10, daysOff: 1, dayPay: 200 });
  assert.equal(e.local, true);
  assert.equal(e.values.movers, 170);
  assert.equal(e.values.fuel, 10); // 20/10*3.5 + 20/25*3.5 = 7 + 2.8
  assert.equal(e.values.deposits, 1500);
  assert.equal(e.values.overlap, 500);
  assert.equal(e.values.travel, 0);
  assert.equal(e.values.timeoff, 200);
  const sub = 170 + 10 + 150 + 0 + 0 + 1500 + 500 + 150 + 200 + 200;
  assert.equal(e.values.buffer, Math.round(sub * 0.1));
});

test('long move: per-mile rental, driving days, nights and meals', () => {
  const e = estimates({ miles: 1200, size: '1br', method: 'diy', cars: 1, people: 2 });
  assert.equal(e.local, false);
  assert.equal(e.values.movers, 130 + 1200);
  assert.equal(e.driveDays, 3);
  assert.equal(e.values.travel, 2 * 130 + 3 * 2 * 40);
  const m = estimates({ miles: 1200, size: '3br', method: 'movers' });
  assert.ok(m.values.movers > 5000);
  assert.equal(estimates({ miles: 10, size: '3br', method: 'movers' }).values.movers, 8 * 150);
});

test('summary, CSV and the sheet paste', () => {
  const s = summary({ saved: 500, rows: { movers: { estimate: 1200, actual: 1350, paid: 300 }, packing: { estimate: 100 } } });
  assert.equal(s.expected, 1450);
  assert.equal(s.owed, 1150);
  assert.equal(s.short, 650);
  assert.equal(s.rows[0].diff, -150);
  assert.match(movingCsv(s), /^Category,Estimate,Actual,Paid,Still to pay\r\nMovers or truck rental,1200,1350,300,1050\r\n/);
  const tsv = movingTsv(s).split('\n');
  assert.equal(tsv.length, 11);
  assert.equal(tsv[0], 'Movers or truck rental\t1200\t1350\t300');
  assert.equal(tsv[2], 'Packing supplies\t100\t\t');
  assert.equal(nameOf('overlap', 'es'), 'Renta doble');
});
