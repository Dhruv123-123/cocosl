// Checks the First Year Freelancing email course (emails/first-year/) and its signup page.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readdirSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { federalTax } from '../lib/tax.js';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const dir = join(root, 'emails', 'first-year');
const emails = readdirSync(dir).filter((f) => /^\d\d-.*\.md$/.test(f)).sort().map((file) => {
  const m = readFileSync(join(dir, file), 'utf8').match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  assert.ok(m, `${file}: front matter`);
  const fm = Object.fromEntries(m[1].split('\n').map((l) => [l.slice(0, l.indexOf(':')).trim(), l.slice(l.indexOf(':') + 1).trim()]));
  return { file, fm, body: m[2] };
});
const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const MON = { Jan: 0, Feb: 1, Mar: 2, Apr: 3, May: 4, Jun: 5, Jul: 6, Aug: 7, Sep: 8, Oct: 9, Nov: 10, Dec: 11 };

test('seven lessons, in order, over about two weeks, each with a task for today', () => {
  assert.equal(emails.length, 7);
  emails.forEach((e, i) => {
    assert.equal(Number(e.fm.order), i + 1);
    for (const k of ['day', 'subject', 'preheader', 'goal']) assert.ok(e.fm[k], `${e.file}: ${k}`);
    assert.match(e.body, /\*\*Do this today:\*\*/, e.file);
    assert.match(e.body, /not tax, legal or financial advice/, e.file);
    assert.ok(e.fm.subject.length <= 60, `${e.file}: subject length`);
  });
  const days = emails.map((e) => Number(e.fm.day));
  assert.deepEqual(days, [...days].sort((a, b) => a - b));
  assert.equal(days[0], 0);
  assert.ok(days.at(-1) <= 14);
});

test('the only product link is one mention in the last lesson', () => {
  const withTracker = emails.filter((e) => e.body.includes('{{tracker_url}}'));
  assert.deepEqual(withTracker.map((e) => e.fm.order), ['7']);
  assert.equal(withTracker[0].body.split('{{tracker_url}}').length, 2);
  const known = new Set(['calculator_url', 'rate_calculator_url', 'invoice_template_url', 'tracker_url']);
  for (const e of emails) for (const [, k] of e.body.matchAll(/\{\{(\w+)\}\}/g)) assert.ok(known.has(k), `${e.file}: {{${k}}}`);
});

test('figures match the site tax model and dated deadlines fall on weekdays', () => {
  const all = emails.map((e) => e.body).join('\n');
  const fed = federalTax({ profit: 60000 });
  assert.ok(all.includes(`$${Math.round(fed.total).toLocaleString('en-US')}`));
  assert.ok(all.includes(`$${Math.round(fed.seTax).toLocaleString('en-US')}`));
  assert.ok(all.includes('$24,500') && all.includes('$7,500') && all.includes('72.5 cents'));
  for (const [, mon, d, y] of all.matchAll(/\b(Jan|Feb|Apr|Jun|Sep|Oct|Nov) (\d{1,2}), (20\d\d)\b/g)) {
    const wd = new Date(Date.UTC(+y, MON[mon], +d)).getUTCDay();
    assert.ok(wd !== 0 && wd !== 6, `${mon} ${d}, ${y} is a ${DAYS[wd]}`);
  }
  assert.ok(!/\b(I|my) (saved|made|earned)\b/.test(all), 'no invented first-person stories');
});

test('the course has a signup page with its own Netlify form, linked from the calendar page', () => {
  const page = readFileSync(join(root, 'first-year', 'index.html'), 'utf8');
  assert.match(page, /name="first-year-course"/);
  assert.match(page, /data-thanks="thanks\/"/);
  assert.equal((page.match(/<li><strong>/g) || []).length, 7);
  assert.match(readFileSync(join(root, 'free', 'index.html'), 'utf8'), /href="\.\.\/first-year\/"/);
  assert.match(readFileSync(join(root, 'first-year', 'thanks', 'index.html'), 'utf8'), /noindex/);
});
