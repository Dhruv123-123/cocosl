import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import * as F from '../lib/family.js';

test('tasks per household, per adult and per child', () => {
  const d = F.emptyFamily();
  const a = F.addMember(d, { name: 'Alex' });
  const b = F.addMember(d, { name: 'Bea', kind: 'adult' });
  const c = F.addMember(d, { name: 'Cam', kind: 'child' });
  assert.throws(() => F.addMember(d, { name: '  ' }), /name/);
  const t = F.tasks(d);
  const household = F.STEPS.filter((s) => s[1] === 'household').length;
  const adult = F.STEPS.filter((s) => s[1] === 'adult').length;
  const child = F.STEPS.filter((s) => s[1] === 'child').length;
  assert.equal(t.length, household + adult * 2 + child);
  assert.equal(t[0].stepId, 'safe-word'); // the family safe word comes first
  assert.ok(t.some((x) => x.stepId === 'freeze-transunion' && x.memberId === b.id && x.bureau.name === 'TransUnion'));
  assert.ok(t.some((x) => x.stepId === 'child-freeze' && x.memberId === c.id));
  assert.ok(!t.some((x) => x.stepId === 'freeze-equifax' && x.memberId === c.id), 'children get the child freeze step, not the adult one');
  assert.ok(t.some((x) => x.memberId === a.id));
});

test('progress, next step and removing someone', () => {
  const d = F.emptyFamily();
  const a = F.addMember(d, { name: 'Alex' });
  let p = F.progress(d);
  assert.equal(p.done, 0);
  assert.equal(p.next.stepId, 'safe-word');
  assert.equal(F.toggle(d, null, 'safe-word', '2026-11-07'), true);
  F.toggle(d, a.id, 'freeze-equifax', '2026-11-07');
  p = F.progress(d);
  assert.equal(p.done, 2);
  assert.equal(p.pct, Math.round((2 / p.total) * 100));
  assert.equal(p.next.stepId, 'scam-talk');
  assert.deepEqual(p.byMember.map((m) => [m.name, m.done]), [['Whole family', 1], ['Alex', 1]]);
  assert.ok(p.minutesLeft > 0);
  assert.equal(F.toggle(d, a.id, 'freeze-equifax'), false, 'ticking again unticks');
  F.toggle(d, a.id, 'phone-pin');
  F.removeMember(d, a.id);
  assert.deepEqual(Object.keys(d.done), ['home:safe-word']);
  assert.deepEqual(F.loadFamily('{bad'), F.emptyFamily());
  assert.equal(F.loadFamily(JSON.stringify(d)).done['home:safe-word'], '2026-11-07');
});

test('never stores secrets, and bureau links are https', () => {
  for (const b of Object.values(F.BUREAUS)) { assert.match(b.url, /^https:\/\//); assert.match(b.phone, /^1-8\d\d-\d{3}-\d{4}$/); }
  const d = F.emptyFamily();
  F.addMember(d, { name: 'Alex' });
  F.toggle(d, null, 'safe-word');
  assert.doesNotMatch(JSON.stringify(d), /word"\s*:\s*"(?!\d{4}-)/);
  const html = readFileSync(new URL('../family/index.html', import.meta.url), 'utf8');
  assert.match(html, /never ask for or save passwords, PINs or your safe word/);
});
