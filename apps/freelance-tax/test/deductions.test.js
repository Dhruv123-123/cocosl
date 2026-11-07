import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { ITEMS, AUTOMATIC, findDeductions, savingPer100, scheduleOf } from '../lib/deductions.js';
import { federalTax } from '../lib/tax.js';

test('18 questions, unique ids, each with a rule, a place on the return and an irs.gov source', () => {
  assert.equal(ITEMS.length, 18);
  assert.equal(new Set(ITEMS.map((i) => i.id)).size, 18);
  for (const it of ITEMS) {
    assert.match(it.q, /\?$/, it.id);
    assert.ok(it.rule.length > 40 && /^Schedule (C|1)/.test(it.where) && it.source.startsWith('irs.gov/'), it.id);
  }
  assert.equal(AUTOMATIC.length, 2);
});

test('2026 figures in the rules', () => {
  const text = ITEMS.map((i) => i.rule).join(' ');
  for (const s of ['72.5¢', '$5 a square foot', '300 sq ft', '$2,500', '$4,400', '$8,750', '$2,000', '$5,000', '50%']) assert.ok(text.includes(s), s);
});

test('answers map to deductions; health, retirement and HSA are Schedule 1', () => {
  assert.deepEqual(findDeductions({ car: true, phone: false, health: true }).map((i) => i.id), ['car', 'health']);
  assert.deepEqual(findDeductions({}), []);
  assert.deepEqual(ITEMS.filter((i) => scheduleOf(i) === '1').map((i) => i.id), ['health', 'retirement', 'hsa']);
});

test('$100 of Schedule C expense saves more than $100 of an adjustment (SE tax too)', () => {
  const c = savingPer100(60000, 'single', 'C'), one = savingPer100(60000, 'single', '1');
  assert.ok(c > 22 && c < 24, String(c));
  assert.ok(one > 9 && one < 11, String(one));
  assert.equal(savingPer100(50), 0);
  assert.ok(savingPer100(120000) > savingPer100(30000));
});

test('aboveLine in federalTax lowers income tax only, and defaults to 0', () => {
  const a = federalTax({ profit: 60000 }), b = federalTax({ profit: 60000, aboveLine: 5000 });
  assert.equal(a.seTax, b.seTax);
  assert.ok(b.incomeTax < a.incomeTax);
  assert.equal(federalTax({ profit: 60000, aboveLine: 0 }).total, a.total);
});

test('page: own Netlify form with the hidden deductions field, FAQ schema, no outside links', () => {
  const html = readFileSync(new URL('../deduction-finder/index.html', import.meta.url), 'utf8');
  for (const s of ['name="deduction-finder"', 'name="deductions"', 'netlify-honeypot', '"@type":"FAQPage"', 'about/']) assert.ok(html.includes(s), s);
  assert.ok(!/<a [^>]*href="https?:/.test(html));
});
