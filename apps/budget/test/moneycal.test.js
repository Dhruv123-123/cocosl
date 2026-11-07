import { test } from 'node:test';
import assert from 'node:assert/strict';
import { allEvents, eventsFor, calendarFile, BRANDS, GROUPS } from '../lib/moneycal.js';
import { QUARTERS } from '../../freelance-invoices/lib/setaside.js';

test('estimated tax dates match the set-aside app', () => {
  const dues = new Set(allEvents().filter((e) => e.group === 'freelance' && /^Estimated tax due/.test(e.en[0])).map((e) => e.date));
  for (const y of [2026, 2027]) for (const q of QUARTERS[y]) if (q.due >= '2026-09-15') assert.ok(dues.has(q.due), q.due);
});

test('Black Friday is the day after the fourth Thursday', () => {
  for (const e of allEvents().filter((x) => /^Black Friday/.test(x.en[0]))) {
    const d = new Date(`${e.date}T12:00:00Z`);
    assert.equal(d.getUTCDay(), 5);
    assert.ok(d.getUTCDate() >= 23 && d.getUTCDate() <= 29, e.date);
  }
});

test('challenge check-ins are Sundays with the classic running total', () => {
  const c = allEvents().filter((e) => e.id.startsWith('challenge-2'));
  assert.equal(c.length, 11);
  for (const e of c) assert.equal(new Date(`${e.date}T12:00:00Z`).getUTCDay(), 0);
  assert.match(c[0].en[1], /Week 6: about \$21 saved/); // Feb 7, 2027 is in week 6: 1+2+...+6
});

test('each brand gets a year of its own events, in its language, with no duplicates', () => {
  for (const [key, b] of Object.entries(BRANDS)) {
    const { events, ics } = calendarFile(key, { from: '2026-11-07', stamp: new Date('2026-11-07T00:00:00Z') });
    assert.ok(events.length >= 8, `${key}: ${events.length}`);
    for (const e of events) assert.ok(b.groups.includes(e.group));
    assert.ok(events.every((e) => e.date >= '2026-11-07' && e.date < '2027-11-08'));
    assert.equal(new Set(events.map((e) => `${e.date}${e.title}`)).size, events.length);
    assert.match(ics, /^BEGIN:VCALENDAR\r\n/);
    assert.equal((ics.match(/BEGIN:VEVENT/g) || []).length, events.length);
    if (b.lang === 'es') assert.match(ics, /Calendario de dinero de Dinero Simple/);
  }
  assert.ok(calendarFile('1099', { from: '2026-11-07' }).events.some((e) => /One week to estimated tax/.test(e.title)));
  assert.ok(!calendarFile('mms', { from: '2026-11-07' }).events.some((e) => e.group === 'scams'));
});

test('a custom choice of groups', () => {
  const e = eventsFor({ groups: ['challenge'], from: '2026-11-07' });
  assert.ok(e.every((x) => x.group === 'challenge'));
  assert.ok(GROUPS.includes('scams'));
});
