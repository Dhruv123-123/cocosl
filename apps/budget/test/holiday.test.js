import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import * as H from '../lib/holiday.js';

const today = '2026-11-20';

function sample() {
  const p = H.emptyPlan();
  H.setCap(p, '800');
  const mom = H.addPerson(p, { name: 'Mom', budget: '150' });
  const sam = H.addPerson(p, { name: 'Sam', budget: '200' });
  H.addPerson(p, { name: 'Teacher gifts', budget: '60' });
  H.addGift(p, { personId: mom.id, item: 'Cardigan', price: '89', bought: true });
  H.addGift(p, { personId: mom.id, item: 'Candle', price: '32' });
  H.addGift(p, { personId: sam.id, item: 'Headphones', price: '249.99', pay: 'bnpl', bnplType: 'pay4' });
  H.addExtra(p, { kind: 'travel', amount: '180' });
  return { p, mom, sam };
}

test('people, gifts, extras and the cap', () => {
  const { p } = sample();
  const s = H.summary(p, today);
  assert.deepEqual(s.people.map((x) => [x.name, x.planned, x.over, x.left]), [['Mom', 121, 0, 29], ['Sam', 249.99, 49.99, 0], ['Teacher gifts', 0, 0, 60]]);
  assert.equal(s.giftsPlanned, 370.99);
  assert.equal(s.reserved, 89, 'unspent budgets still count toward the total');
  assert.equal(s.expected, 639.99);
  assert.equal(s.spent, 269, 'bought gifts plus extras');
  assert.deepEqual([s.overCap, s.capLeft, s.pct], [0, 160.01, 80]);
  assert.throws(() => H.addPerson(p, { name: ' ' }), /name/);
  assert.throws(() => H.addGift(p, { personId: 'nobody', item: 'x', price: 1 }), /who the gift is for/);
  assert.throws(() => H.addGift(p, { personId: p.people[0].id, item: 'x', price: 10, pay: 'bnpl', bnplType: 'monthly', months: 1, apr: 10 }), /monthly payments/);
});

test('pay in 4: four payments two weeks apart, no interest, still paying into January', () => {
  const c = H.bnplCost(249.99, { type: 'pay4' }, '2026-12-10');
  assert.deepEqual(c.payments.map((x) => [x.date, x.amount]), [['2026-12-10', 62.49], ['2026-12-24', 62.49], ['2027-01-07', 62.49], ['2027-01-21', 62.52]]);
  assert.deepEqual([c.interest, c.total, c.last], [0, 249.99, '2027-01-21']);
});

test('monthly plan: amortized interest and a true cost', () => {
  const c = H.bnplCost(1000, { type: 'monthly', apr: 29.99, months: 12 }, '2026-12-01');
  assert.equal(c.payments.length, 12);
  assert.equal(c.payments[0].date, '2027-01-01');
  assert.equal(c.last, '2027-12-01');
  assert.ok(c.interest > 160 && c.interest < 175, `interest ${c.interest}`);
  assert.equal(c.total, Math.round((1000 + c.interest) * 100) / 100);
  assert.equal(Math.round(c.payments.reduce((t, x) => t + x.amount, 0) * 100) / 100, c.total);
  const zero = H.bnplCost(600, { type: 'monthly', apr: 0, months: 6 }, '2026-12-01');
  assert.deepEqual([zero.each, zero.interest, zero.total], [100, 0, 600]);
});

test('warnings: over the cap, over a budget, BNPL months and stacking, card balance', () => {
  const { p, mom } = sample();
  let w = H.warnings(p, today).map((x) => x.text).join(' | ');
  assert.match(w, /Sam's gifts are \$49\.99 over their budget/);
  assert.match(w, /still be paying for these gifts in January 2027/);
  assert.match(w, /interest-free only if every payment goes through on time/);
  assert.doesNotMatch(w, /over your cap/);
  H.addGift(p, { personId: mom.id, item: 'Tablet', price: '329', pay: 'bnpl', bnplType: 'monthly', months: '6', apr: '29.99' });
  H.addGift(p, { personId: mom.id, item: 'Boots', price: '120', pay: 'bnpl' });
  H.addGift(p, { personId: mom.id, item: 'Watch', price: '200', pay: 'carry' });
  w = H.warnings(p, today).map((x) => x.text).join(' | ');
  assert.match(w, /over your cap/);
  assert.match(w, /add \$\d+\.\d\d in interest/);
  assert.match(w, /3 buy now, pay later plans/);
  assert.match(w, /\$200\.00 goes on a card you're carrying a balance on/);
});

test('saving, loading and removing', () => {
  const { p, mom } = sample();
  const back = H.loadPlan(JSON.stringify(p));
  assert.deepEqual(back, p);
  assert.equal(H.toggleBought(p, p.gifts[1].id), true);
  H.removePerson(p, mom.id);
  assert.equal(p.gifts.length, 1, 'their gifts go too');
  H.removeExtra(p, p.extras[0].id);
  assert.equal(H.summary(p, today).extras, 0);
  assert.deepEqual(H.loadPlan('nope'), H.emptyPlan());
});

test('page: private, BNPL explained, Budget Pro slot', () => {
  const html = readFileSync(new URL('../holiday.html', import.meta.url), 'utf8');
  assert.match(html, /Saved in this browser only/);
  assert.match(html, /href="pricing\.html\?from=holiday" data-upgrade="holiday"/);
  assert.doesNotMatch(readFileSync(new URL('../holiday.js', import.meta.url), 'utf8'), /fetch\(/);
});
