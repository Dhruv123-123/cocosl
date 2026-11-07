// Checks the quarterly-tax reminder emails in emails/reminders/: dates, weekdays, links, disclaimers.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readdirSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const dir = join(dirname(fileURLToPath(import.meta.url)), '..', 'emails', 'reminders');
const DEADLINES = ['2027-01-15', '2027-04-15', '2027-06-15', '2027-09-15'];
const DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
  'October', 'November', 'December'];

const emails = readdirSync(dir).filter((f) => /^\d\d-.*\.md$/.test(f)).sort().map((file) => {
  const text = readFileSync(join(dir, file), 'utf8');
  const m = text.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  assert.ok(m, `${file}: front matter`);
  const fm = Object.fromEntries(m[1].split('\n').map((l) => {
    const i = l.indexOf(':');
    return [l.slice(0, i).trim(), l.slice(i + 1).trim().replace(/^"(.*)"$/, '$1')];
  }));
  return { file, fm, body: m[2] };
});

const utc = (s) => new Date(`${s}T12:00:00Z`);
const diffDays = (a, b) => Math.round((utc(a) - utc(b)) / 86400000);

test('twelve reminders, three per deadline: 7 days before, the day before, the day after', () => {
  assert.equal(emails.length, 12);
  emails.forEach((e, i) => {
    assert.equal(Number(e.fm.order), i + 1, `${e.file}: order`);
    for (const k of ['send_on', 'deadline', 'subject', 'preheader', 'goal']) assert.ok(e.fm[k], `${e.file}: ${k}`);
  });
  for (const d of DEADLINES) {
    const offsets = emails.filter((e) => e.fm.deadline === d).map((e) => diffDays(e.fm.send_on, d));
    assert.deepEqual(offsets, [-7, -1, 1], `offsets for ${d}`);
  }
});

test('every deadline is a weekday', () => {
  for (const d of DEADLINES) assert.ok(![0, 6].includes(utc(d).getUTCDay()), d);
});

test('every "Weekday, Month D(, YYYY)" in the text names the right weekday', () => {
  const re = new RegExp(`(${DAYS.join('|')}),? (${MONTHS.join('|')}) (\\d{1,2})(?:, (\\d{4}))?`, 'g');
  let checked = 0;
  for (const e of emails) {
    const year = e.fm.deadline.slice(0, 4);
    for (const [, day, month, date, y] of `${e.fm.subject}\n${e.fm.preheader}\n${e.body}`.matchAll(re)) {
      const iso = `${y || year}-${String(MONTHS.indexOf(month) + 1).padStart(2, '0')}-${date.padStart(2, '0')}`;
      // A date in January named in a September email is next year's.
      const fixed = !y && MONTHS.indexOf(month) < 3 && Number(e.fm.deadline.slice(5, 7)) > 6
        ? `${Number(year) + 1}${iso.slice(4)}` : iso;
      assert.equal(DAYS[utc(fixed).getUTCDay()], day, `${e.file}: ${day} ${month} ${date} (${fixed})`);
      checked += 1;
    }
  }
  assert.ok(checked >= 12, `only ${checked} dated mentions checked`);
});

test('the right tax year is named for each payment', () => {
  for (const e of emails.filter((x) => x.fm.deadline === '2027-01-15')) {
    if (/tax year/.test(e.body)) assert.match(e.body, /tax year 2026/, e.file);
    assert.doesNotMatch(e.body, /tax year 2027/, e.file);
  }
  for (const e of emails.filter((x) => x.fm.deadline !== '2027-01-15')) {
    assert.doesNotMatch(e.body.replace(/2026 balance|2026 return|for 2026|your 2026|2026 contributions|2026 SEP|2026 AGI|extended 2026/g, ''),
      /tax year 2026/, e.file);
  }
});

test('placeholders, links and disclaimers', () => {
  let trackerLinks = 0;
  for (const e of emails) {
    const placeholders = [...e.body.matchAll(/\{\{(\w+)\}\}/g)].map((m) => m[1]);
    for (const p of placeholders) assert.ok(['calculator_url', 'tracker_url'].includes(p), `${e.file}: {{${p}}}`);
    trackerLinks += placeholders.filter((p) => p === 'tracker_url').length;
    assert.match(e.body, /Educational content, not tax, legal or financial advice/, e.file);
    assert.doesNotMatch(e.body, /guarantee|act now|last chance to buy|only \d+ left/i, e.file);
    assert.doesNotMatch(e.body, /\$\{|\$ROUTINE|\$FOOT/, `${e.file}: unexpanded template text`);
    // The safe harbor never "avoids" the penalty without "generally".
    for (const line of e.body.split('\n')) {
      if (/avoids? the underpayment penalty/.test(line)) assert.match(line, /generally/, `${e.file}: ${line}`);
    }
  }
  assert.equal(trackerLinks, 1, 'the tracker is linked once across the whole series');
});
