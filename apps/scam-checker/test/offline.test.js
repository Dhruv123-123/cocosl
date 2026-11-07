// The text and link checkers must never send what people paste anywhere: every check runs on pattern
// rules in the browser. This fails if a network call creeps into the checking code. (The only request
// on the page is the optional newsletter form in signup.js, which sends an email address, never a message.)
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const NET = /\bfetch\s*\(|XMLHttpRequest|sendBeacon|WebSocket|EventSource|import\s*\(\s*['"`]https?:|from\s+['"`]https?:/;
const CHECKING = ['lib/scan.js', 'lib/site.js', 'lib/i18n.js', 'lib/vendor.js', 'app.js', 'link.js', 'vendor.js'];

test('the checking code makes no network calls', () => {
  for (const f of CHECKING) {
    const src = readFileSync(new URL(`../${f}`, import.meta.url), 'utf8');
    assert.doesNotMatch(src, NET, `${f} must stay offline`);
  }
});

test('the only page script that talks to the network is the newsletter form', () => {
  const app = readFileSync(new URL('../app.js', import.meta.url), 'utf8');
  assert.match(app, /setupSignup/);
  assert.doesNotMatch(app, /analyzeMessage\([^)]*\)[^;]*fetch/);
});
