import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import * as E from '../lib/embed-options.js';
import config from '../config.js';

const P = (q) => new URLSearchParams(q);
const LIC = { licensees: [{ key: 'cu1', name: 'River CU', domains: ['rivercu.org'], cta: { label: 'Open savings', url: 'https://rivercu.org/save' } }] };

test('accent colours: valid hex only, with readable button text', () => {
  assert.equal(E.normalizeHex('1F6FEB'), '#1f6feb');
  assert.equal(E.normalizeHex('#abc'), '#aabbcc');
  assert.equal(E.normalizeHex('red;background:url(x)'), null);
  assert.equal(E.inkFor('#1f3a8a'), '#ffffff', 'dark accent gets white text');
  assert.equal(E.inkFor('#f2b134'), '#0b1d13', 'light accent gets dark text');
  for (const hex of ['#1f6feb', '#f2b134', '#7c3aed', '#00a36c', '#ff0000']) assert.ok(E.contrast(hex, E.inkFor(hex)) >= 3.9, hex);
});

test('free embed: credit link stays, styling applies', () => {
  const o = E.embedOptions(P('embed=1&accent=1f6feb&theme=dark&radius=40'), 'https://blog.example/', LIC);
  assert.deepEqual([o.accent, o.accentInk, o.theme, o.radius, o.showCredit, o.licensed, o.cta], ['#1f6feb', '#ffffff', 'dark', 24, true, false, null]);
  assert.equal(E.embedOptions(P('theme=neon'), '', {}).theme, 'auto');
  assert.equal(E.embedOptions(P(''), '', {}).radius, null);
});

test('licence: only on the licensee domain (and subdomains)', () => {
  let o = E.embedOptions(P('licence=cu1'), 'https://www.rivercu.org/tools', LIC);
  assert.deepEqual([o.licensed, o.showCredit, o.partner, o.cta.url], [true, false, 'River CU', 'https://rivercu.org/save']);
  o = E.embedOptions(P('licence=cu1'), 'https://copycat.example/', LIC);
  assert.deepEqual([o.licensed, o.showCredit, o.licenceProblem], [false, true, 'domain']);
  assert.equal(E.embedOptions(P('licence=nope'), 'https://rivercu.org/', LIC).licenceProblem, 'key');
  assert.equal(E.embedOptions(P('licence=cu1'), '', LIC).licensed, false, 'no referrer, no licence');
  assert.equal(E.hostAllowed('https://evilrivercu.org/', ['rivercu.org']), false);
});

test('licensee buttons must be https', () => {
  const bad = { licensees: [{ key: 'k', name: 'X', domains: ['x.org'], cta: { label: 'Go', url: 'javascript:alert(1)' } }] };
  assert.equal(E.embedOptions(P('licence=k'), 'https://x.org/', bad).cta, null);
});

test('demo licence works on localhost only; real licence keys are not in the repo by default', () => {
  assert.deepEqual(config.embed.licensees.map((l) => l.key), ['demo']);
  assert.ok(config.embed.licensees[0].domains.every((d) => ['localhost', '127.0.0.1'].includes(d)));
});

test('embed.js passes styling, licence and safe starting values to the iframe', () => {
  const src = readFileSync(new URL('../embed.js', import.meta.url), 'utf8');
  for (const k of ['accent', 'theme', 'radius', 'licence']) assert.match(src, new RegExp(`'${k}'`));
  assert.match(src, /data-values/);
  assert.match(src, /\[a-zA-Z0-9\.\]\{1,20\}/, 'values are limited to letters, digits and dots');
});
