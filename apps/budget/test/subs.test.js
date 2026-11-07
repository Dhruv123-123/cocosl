import { test } from 'node:test';
import assert from 'node:assert/strict';
import { SERVICES, GROUPS, totals, guessLine, matchService, storeFor, yearlyOf } from '../lib/subs.js';
import { merchantKey } from '../lib/recurring.js';

test('30 services, each with a price, a group, cancel steps and an https help link', () => {
  assert.equal(SERVICES.length, 30);
  assert.equal(new Set(SERVICES.map((s) => s.id)).size, 30);
  const groups = new Set(GROUPS.map(([g]) => g));
  for (const s of SERVICES) {
    assert.ok(groups.has(s.group), s.id);
    assert.ok(s.price > 0 && ['month', 'year'].includes(s.per), s.id);
    assert.match(s.url, /^https:\/\/[^\s]+$/, s.id);
    assert.ok(s.how.length > 20 && s.keys.length, s.id);
  }
});

test('totals: monthly and yearly prices add up to a yearly figure', () => {
  const t = totals([{ price: 19.99, per: 'month' }, { price: 65, per: 'year' }, { price: 0, per: 'month' }]);
  assert.equal(t.count, 2);
  assert.equal(t.yearly, 304.88);
  assert.equal(t.monthly, 25.41);
  assert.equal(t.daily, 0.84);
  assert.equal(t.tenYears, 3048.8);
  assert.equal(yearlyOf(10, 'week'), 520);
  assert.deepEqual(totals([]), { count: 0, yearly: 0, monthly: 0, daily: 0, tenYears: 0 });
});

test('the guess comparison', () => {
  assert.deepEqual(guessLine(50, 142), { kind: 'more', ratio: 2.8, gap: 92 });
  assert.equal(guessLine(100, 60).kind, 'less');
  assert.equal(guessLine(100, 105).kind, 'close');
  assert.equal(guessLine('', 100), null);
});

test('bank statement lines match the right service, and app-store charges are spotted', () => {
  const m = (note) => matchService(`${merchantKey(note)} ${note.toLowerCase()}`)?.id;
  assert.equal(m('NETFLIX.COM 866-579-7172 CA'), 'netflix');
  assert.equal(m('SPOTIFY USA *P1A9C3'), 'spotify');
  assert.equal(m('PLANET FITNESS #1022'), 'planetfitness');
  assert.equal(m('Google YouTube TV'), 'yttv');
  assert.equal(m('KROGER #555'), undefined);
  assert.equal(storeFor('APPLE.COM/BILL 866-712-7753'), 'apple');
  assert.equal(storeFor('GOOGLE *Duolingo'), 'google');
  assert.equal(storeFor('NETFLIX.COM'), null);
});
