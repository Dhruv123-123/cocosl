import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import * as K from '../lib/checkup.js';
import * as F from '../lib/firstpaycheck.js';

const all = (i) => Object.fromEntries(K.QUESTIONS.map((q) => [q.id, i]));

test('checkup: 20 questions, every option scored 0-2, every link goes somewhere real', () => {
  assert.equal(K.QUESTIONS.length, 20);
  assert.equal(new Set(K.QUESTIONS.map((q) => q.id)).size, 20);
  for (const q of K.QUESTIONS) {
    assert.ok(K.AREAS[q.area], q.id);
    assert.ok(q.o.some(([, p]) => p === 2), `${q.id} has a full-marks answer`);
    for (const [, p] of q.o) assert.ok([0, 1, 2].includes(p));
    if (!/^https:/.test(q.link)) {
      const path = q.link.split('#')[0] || './';
      const f = new URL(`../${path}${path.endsWith('/') ? 'index.html' : ''}`, import.meta.url);
      assert.ok(existsSync(f), `${q.id} -> ${q.link}`);
    }
  }
});

test('checkup: score, grade, areas and the order of fixes', () => {
  const best = K.report(all(0));
  assert.deepEqual([best.score, best.grade, best.fixes.length, best.complete], [100, 'A', 0, true]);
  const worst = K.report(Object.fromEntries(K.QUESTIONS.map((q) => [q.id, q.o.findIndex(([, p]) => p === 0)])));
  assert.equal(worst.score, 0);
  assert.equal(worst.grade, 'F');
  // Heaviest gaps first: weight 3 questions come before weight 1.
  assert.equal(worst.fixes[0].id, 'track');
  assert.ok(worst.fixes[0].urgent);
  assert.equal(worst.fixes.at(-1).urgent, false);
  const half = K.report({ cushion: 1, cards: 2 });
  assert.equal(half.answered, 2);
  assert.equal(half.score, 25);
  assert.equal(half.areas.find((a) => a.key === 'saving').score, 50);
  assert.equal(half.areas.find((a) => a.key === 'retirement').score, null);
  assert.deepEqual(half.fixes.map((f) => f.id), ['cards', 'cushion']);
  assert.equal(K.report({}).answered, 0);
  assert.deepEqual(['A', 'B', 'C', 'D', 'F'], [95, 85, 70, 55, 10].map(K.grade));
});

test('first paycheck: W-4 advice for the simple case and the tricky ones', () => {
  const simple = F.w4Advice({ jobs: 'one', married: 'no' });
  assert.equal(simple.simple, true);
  assert.match(simple.steps[1].text, /Skip it/);
  const busy = F.w4Advice({ jobs: 'two', married: 'spouse-works', kids: 2, otherDeps: 1, side: 'yes', sideIncome: 10000, bracket: 12 });
  assert.equal(busy.simple, false);
  assert.match(busy.steps[0].text, /Married filing jointly/);
  assert.equal(busy.steps[1].link, F.W4_ESTIMATOR);
  assert.match(busy.steps[2].text, /\$4,900/);
  assert.equal(busy.steps[3].extraYear, Math.round(10000 * (0.12 + 0.9235 * 0.153) * 100) / 100);
  assert.match(F.w4Advice({ married: 'no', kids: 1 }).steps[0].text, /Head of household/);
});

test('first paycheck: 401(k) match, emergency fund targets, budget splits', () => {
  const m = F.matchPlan({ salary: 55000, matchPct: 50, upToPct: 6, payPeriods: 26 });
  assert.equal(m.contributePct, 6);
  assert.equal(m.youYear, 3300);
  assert.equal(m.freeMoneyYear, 1650);
  assert.equal(m.youPerPaycheck, Math.round((3300 / 26) * 100) / 100);
  assert.equal(F.matchPlan({ salary: 500000, upToPct: 6 }).capped, true);
  assert.deepEqual(F.cushionTargets(2200).map((t) => t.amount), [1100, 2200, 6600]);
  assert.equal(F.cushionTargets(800)[0].amount, 1000);
  assert.deepEqual(F.budgetSplits(3500).fiftyThirtyTwenty, { needs: 1750, wants: 1050, savings: 700 });
  for (const x of F.EXTRAS.filter((e) => e.link)) assert.ok(existsSync(new URL(`../${x.link}index.html`, import.meta.url)), x.link);
});

test('pages: private, offline, upsell slots, sources', () => {
  for (const [page, from] of [['checkup', 'checkup'], ['first-paycheck', 'first-paycheck']]) {
    const html = readFileSync(new URL(`../${page}.html`, import.meta.url), 'utf8');
    assert.match(html, new RegExp(`href="pricing\\.html\\?from=${from}" data-upgrade="${from}"`));
    assert.doesNotMatch(readFileSync(new URL(`../${page}.js`, import.meta.url), 'utf8'), /fetch\(/);
  }
  const sw = readFileSync(new URL('../sw.js', import.meta.url), 'utf8');
  assert.match(sw, /'first-paycheck\.html', 'first-paycheck\.js', 'lib\/firstpaycheck\.js', 'checkup\.html', 'checkup\.js', 'lib\/checkup\.js'/);
  assert.match(readFileSync(new URL('../lib/firstpaycheck.js', import.meta.url), 'utf8'), /irs\.gov\/newsroom\/401k-limit-increases-to-24500/);
});
