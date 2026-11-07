import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { search, norm } from '../../hub-search.js';
import { buildIndex, cardsFromHub } from '../../tools/build-search.mjs';

const read = (f) => readFileSync(new URL(`../../${f}`, import.meta.url), 'utf8');
const index = buildIndex();
const top = (q) => search(index, q)[0]?.t;

test('index covers every tool card on the hub and is up to date', () => {
  const cards = cardsFromHub(read('index.html'));
  assert.equal(index.length, cards.length);
  assert.ok(index.length >= 25);
  for (const item of index) assert.ok(item.t && item.u && item.s && item.k, item.u);
  assert.deepEqual(JSON.parse(read('search-index.json')), index, 'run: node tools/build-search.mjs');
});

test('finds the right tool for everyday searches', () => {
  assert.equal(top('paycheck'), 'Paycheck calculator by state');
  assert.equal(top('my wife and I'), 'Money date: couples budget');
  assert.equal(top('student loan'), 'Student loan repayment chooser');
  assert.equal(top('how much car can I afford'), 'Can I afford this?');
  assert.equal(top('rent or buy a house'), 'Rent vs buy');
  assert.equal(top('christmas'), 'Holiday spending planner');
  assert.equal(top('late invoice'), 'Invoice tracker and late fee calculator');
  assert.match(search(index, 'scam text').map((r) => r.t).join(' '), /Is this a scam\?/);
  assert.deepEqual(search(index, 'zzzz'), []);
  assert.deepEqual(search(index, '  the and  '), []);
  assert.equal(norm('Préstamo'), 'prestamo');
});

test('hub page: labelled search box, results live region, offline', () => {
  const html = read('index.html');
  assert.match(html, /<label for="q">Search all tools<\/label>/);
  assert.match(html, /role="search"/);
  assert.match(html, /id="search-count"[^>]*aria-live="polite"/);
  assert.match(html, /src="hub-search\.js"/);
  const sw = read('sw.js');
  assert.match(sw, /'hub-search\.js', 'search-index\.json'/);
  assert.match(read('netlify.toml'), /node tools\/build-search\.mjs/);
  assert.doesNotMatch(read('hub-search.js'), /fetch\('http/, 'only fetches the local index');
});
