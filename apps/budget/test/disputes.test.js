import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import * as D from '../lib/disputes.js';

const base = { target: 'experian', item: 'Metro Bank Card', reason: 'wrong-late', method: 'online', sent: '2026-11-01' };

test('validation', () => {
  assert.throws(() => D.makeDispute({ ...base, target: 'acme' }), /who you sent/);
  assert.throws(() => D.makeDispute({ ...base, item: ' ' }), /Name the item/);
  assert.throws(() => D.makeDispute({ ...base, sent: '' }), /date you sent/);
  assert.throws(() => D.makeDispute({ ...base, received: '2026-10-01' }), /before you sent/);
  const d = D.makeDispute({ ...base, reason: 'bogus', method: 'pigeon', extended: 'on' });
  assert.deepEqual([d.reason, d.method, d.extended], ['other', 'online', true]);
});

test('30-day clock: online starts when sent, mail is estimated, received date wins, 45 days when extended', () => {
  assert.equal(D.clock(D.makeDispute(base), '2026-11-07').due, '2026-12-01');
  const mail = D.clock(D.makeDispute({ ...base, method: 'mail' }), '2026-11-07');
  assert.deepEqual([mail.start, mail.due, mail.estimatedStart], ['2026-11-06', '2026-12-06', true]);
  const got = D.clock(D.makeDispute({ ...base, method: 'mail', received: '2026-11-04' }), '2026-11-07');
  assert.deepEqual([got.due, got.estimatedStart], ['2026-12-04', false]);
  assert.equal(D.clock(D.makeDispute({ ...base, extended: true }), '2026-11-07').due, '2026-12-16');
});

test('states move from waiting to overdue, and a reply closes the clock', () => {
  const d = D.makeDispute(base); // due 2026-12-01, results by 2026-12-08
  assert.equal(D.clock(d, '2026-11-07').state, 'waiting');
  assert.equal(D.clock(d, '2026-11-27').state, 'due-soon');
  assert.equal(D.clock(d, '2026-12-03').state, 'late');
  assert.equal(D.clock(d, '2026-12-09').state, 'overdue');
  assert.match(D.nextSteps(d, '2026-12-09').join(' '), /consumerfinance\.gov\/complaint/);
  const data = { disputes: [d] };
  assert.throws(() => D.setOutcome(data, d.id, 'verified', ''), /date/);
  D.setOutcome(data, d.id, 'verified', '2026-11-20');
  assert.equal(D.clock(d, '2026-12-09').state, 'answered');
  assert.match(D.nextSteps(d, '2026-12-09').join(' '), /100 words/);
  assert.match(D.nextSteps({ ...d, outcome: 'deleted' }, '2026-12-09').join(' '), /comes back/);
});

test('board, summary and calendar reminders', () => {
  const data = D.emptyDisputes();
  const a = D.addDispute(data, { ...base, sent: '2026-09-01' });
  const b = D.addDispute(data, { ...base, target: 'equifax', sent: '2026-11-05' });
  const c = D.addDispute(data, { ...base, target: 'transunion', sent: '2026-10-20' });
  D.setOutcome(data, c.id, 'deleted', '2026-11-06');
  const today = '2026-11-07';
  assert.deepEqual(D.board(data, today).map((r) => r.id), [a.id, b.id, c.id]);
  assert.deepEqual(D.summary(data, today), { total: 3, open: 2, overdue: 1, removedOrFixed: 1, nextDue: '2026-12-05' });
  const ev = D.reminderEvents(data, today);
  assert.deepEqual(ev.map((e) => e.date), ['2026-12-05', '2026-12-12'], 'past and answered disputes get no reminders');
  D.removeDispute(data, a.id);
  assert.equal(data.disputes.length, 2);
  assert.equal(D.loadDisputes('{bad').disputes.length, 0);
  assert.equal(D.loadDisputes(JSON.stringify({ disputes: [{ target: 'x', sent: '2026-01-01' }, b] })).disputes.length, 1);
});

test('page stays clear of credit repair: free, tracking only, no letters or paid features', () => {
  const html = readFileSync(new URL('../disputes.html', import.meta.url), 'utf8');
  const js = readFileSync(new URL('../disputes.js', import.meta.url), 'utf8');
  assert.match(html, /isn't a credit repair service and doesn't write letters/);
  assert.match(html, /Nobody can legally remove accurate/);
  assert.doesNotMatch(html + js, /pricing\.html|data-upgrade|upsell|currentPlan|REPLACE_ME|gumroad|lemonsqueezy/i);
  for (const t of Object.values(D.TARGETS)) if (t.url) assert.match(t.url, /^https:\/\//);
});
