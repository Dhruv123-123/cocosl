import { test } from 'node:test';
import assert from 'node:assert/strict';
import { QUESTIONS, verdict, QUIZ, quizScore, PLACES, SITUATIONS, STATE_AGS, agFor } from '../lib/scamapp.js';

test('checklist verdicts', () => {
  assert.equal(verdict({}).level, 'none');
  assert.equal(verdict({ firstContact: false, urgent: false }).level, 'low');
  assert.equal(verdict({ firstContact: true }).level, 'low');
  assert.equal(verdict({ urgent: true }).level, 'medium');
  assert.equal(verdict({ pay: true }).level, 'high'); // gift cards / crypto on its own
  assert.equal(verdict({ urgent: true, link: true }).level, 'high');
  assert.equal(new Set(QUESTIONS.map((q) => q.id)).size, QUESTIONS.length);
});

test('quiz has ten items, a mix of scams and real ones, and scores', () => {
  assert.equal(QUIZ.length, 10);
  const real = QUIZ.filter((x) => !x.a).length;
  assert.ok(real >= 2 && real <= 4);
  const all = Object.fromEntries(QUIZ.map((x, i) => [i, x.a]));
  assert.deepEqual(quizScore(all), { right: 10, total: 10, done: true });
  assert.equal(quizScore({ 0: true }).done, false);
});

test('report directory: every situation points at real entries, safe link schemes, every state', () => {
  for (const s of SITUATIONS) for (const k of s.places) assert.ok(PLACES[k], `${s.id}: ${k}`);
  for (const p of Object.values(PLACES)) assert.match(p.url, /^(https:\/\/|sms:|mailto:|tel:)/);
  for (const k of ['ftc', 'ic3', 'idtheft']) assert.ok(PLACES[k]);
  assert.equal(STATE_AGS.length, 56); // 50 states, DC and 5 territories
  for (const [code, name, url] of STATE_AGS) { assert.match(code, /^[A-Z]{2}$/); assert.ok(name); assert.match(url, /^https:\/\//); }
  assert.equal(agFor('TX')[1], 'Texas');
  assert.equal(agFor('ZZ'), null);
});
