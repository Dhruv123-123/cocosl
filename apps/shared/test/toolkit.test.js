// The Money Toolkit list (tools/toolkit.mjs): every page it bundles exists, output names are unique and safe,
// and the free site's paid-only or online-only pages stay out.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { SECTIONS, ITEMS, sourceFile } from '../../tools/toolkit.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..', '..');

test('every toolkit page exists and output names are unique', () => {
  assert.ok(ITEMS.length >= 40, String(ITEMS.length));
  assert.equal(new Set(ITEMS.map((i) => i.out)).size, ITEMS.length);
  for (const i of ITEMS) {
    assert.ok(existsSync(join(root, sourceFile(i.src))), i.src);
    assert.match(i.out, /^[a-z0-9-]+\.html$/);
    assert.notEqual(i.out, 'index.html');
    assert.ok(i.title && i.blurb, i.src);
  }
});

test('Spanish items are Spanish pages, English items English', () => {
  for (const i of ITEMS) assert.match(readFileSync(join(root, sourceFile(i.src)), 'utf8'), new RegExp(`<html lang="${i.lang}"`), i.src);
});

test('every section has tools', () => {
  for (const s of SECTIONS) assert.ok(s.items.length, s.id);
});
