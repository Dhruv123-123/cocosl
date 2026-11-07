import { test } from 'node:test';
import assert from 'node:assert/strict';
import { cardModel, wrap, BRANDS } from '../sharecard.js';

test('subscription card shows only the total and the count', () => {
  const m = cardModel('subs', { yearly: 1284.5, count: 12, names: ['Netflix'] }, 'https://tools.example.com/budget/subscriptions.html?x=1');
  assert.equal(m.big, '$1,285 a year');
  assert.equal(m.line, '12 subscriptions · $3.52 a day');
  assert.equal(m.url, 'tools.example.com/budget/subscriptions');
  assert.ok(!JSON.stringify(m).includes('Netflix'));
  const hidden = cardModel('subs', { yearly: 1284.5, count: 1, showTotal: false }, 'x.com/a.html');
  assert.equal(hidden.big, '1 subscription');
  assert.ok(!JSON.stringify(hidden).includes('1,28'));
});

test('quiz card shows the score', () => {
  const m = cardModel('quiz', { right: 9, total: 10 }, 'shield.example/app/quiz.html');
  assert.equal(m.brand, 'scam');
  assert.equal(m.big, 'I spotted 9 of 10');
  assert.equal(m.url, 'shield.example/app/quiz');
  assert.match(cardModel('quiz', { right: 4, total: 10 }).line, /do better/);
  assert.ok(BRANDS[m.brand]);
  assert.throws(() => cardModel('other'));
});

test('wrap splits text to fit', () => {
  const ctx = { measureText: (t) => ({ width: t.length * 10 }) };
  assert.deepEqual(wrap(ctx, 'one two three four', 90), ['one two', 'three', 'four']);
});
