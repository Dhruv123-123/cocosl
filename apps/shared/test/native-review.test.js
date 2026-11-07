// Every Spanish page must be on the native review list (NATIVE_REVIEW_ES.md) so none goes out unchecked.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';
import { ROOT } from '../../tools/sync-shared.mjs';

const SKIP = new Set(['node_modules', 'scam-extension', '.netlify']);
function walk(dir, out = []) {
  for (const f of readdirSync(dir)) {
    if (SKIP.has(f)) continue;
    const p = join(dir, f);
    if (statSync(p).isDirectory()) walk(p, out); else if (f.endsWith('.html')) out.push(relative(ROOT, p));
  }
  return out;
}

test('every Spanish page is on the native review list', () => {
  const list = readFileSync(join(ROOT, 'NATIVE_REVIEW_ES.md'), 'utf8');
  const spanish = walk(ROOT).filter((f) => /<html lang="es"/.test(readFileSync(join(ROOT, f), 'utf8')));
  assert.ok(spanish.length >= 30, `found ${spanish.length}`);
  for (const f of spanish) {
    const asDir = f.replace(/index\.html$/, '');
    assert.ok(list.includes(`\`${f}\``) || list.includes(`\`${asDir}\``), `${f} is Spanish but not on NATIVE_REVIEW_ES.md`);
  }
});
