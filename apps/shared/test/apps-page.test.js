// Every installable app is on the install page, and every manifest it lists is complete:
// a name, a start page that exists and links the manifest, standalone display, and 192px and 512px PNG icons
// that exist at the size the manifest says.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, existsSync, statSync } from 'node:fs';
import { join, dirname, posix } from 'node:path';
import { fileURLToPath } from 'node:url';
import { APPS, appsPage } from '../../tools/build-apps-page.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..', '..');

function manifests(dir = '', out = []) {
  for (const f of readdirSync(join(root, dir))) {
    if (f === 'node_modules' || f.startsWith('.')) continue;
    const p = dir ? `${dir}/${f}` : f;
    if (statSync(join(root, p)).isDirectory()) manifests(p, out);
    else if (f.endsWith('.webmanifest')) out.push(p);
  }
  return out;
}

const pngSize = (file) => { const b = readFileSync(file); assert.equal(b.toString('ascii', 1, 4), 'PNG', `${file} is a PNG`); return `${b.readUInt32BE(16)}x${b.readUInt32BE(20)}`; };

test('every web app manifest is on the install page', () => {
  assert.deepEqual(manifests().sort(), APPS.map((a) => a.manifest).sort());
});

for (const app of APPS) {
  test(`${app.manifest} is complete and its icons exist`, () => {
    const m = JSON.parse(readFileSync(join(root, app.manifest), 'utf8'));
    const dir = posix.dirname(app.manifest);
    assert.ok(m.name && m.short_name, 'name and short_name');
    assert.ok(m.short_name.length <= 15, 'short_name fits under an icon');
    assert.equal(m.display, 'standalone');
    assert.ok(m.theme_color && m.background_color);
    const sizes = new Set();
    for (const icon of m.icons) {
      const file = join(root, dir, icon.src);
      assert.ok(existsSync(file), `${icon.src} exists`);
      if (icon.type === 'image/png') { assert.equal(pngSize(file), icon.sizes, `${icon.src} is ${icon.sizes}`); sizes.add(icon.sizes); }
    }
    assert.ok(sizes.has('192x192') && sizes.has('512x512'), '192 and 512 PNG icons');
    assert.ok(m.icons.some((i) => /maskable/.test(i.purpose || '')), 'a maskable icon for Android');
    for (const s of m.shortcuts || []) for (const i of s.icons || []) assert.ok(existsSync(join(root, dir, i.src)), `shortcut icon ${i.src}`);
    const start = join(root, app.open);
    assert.ok(existsSync(start), `${app.open} exists`);
    const href = /<link rel="manifest" href="([^"]+)"/.exec(readFileSync(start, 'utf8'))?.[1];
    assert.equal(posix.normalize(posix.join(posix.dirname(app.open), href)), app.manifest, `${app.open} links ${app.manifest}`);
    const startUrl = posix.normalize(posix.join(dir, m.start_url.split('?')[0]));
    assert.ok(existsSync(join(root, startUrl.endsWith('/') || startUrl === '.' ? join(startUrl, 'index.html') : startUrl)), `start_url ${m.start_url}`);
  });
}

test('apps.html and es/apps.html are up to date (run node tools/build-apps-page.mjs)', () => {
  assert.equal(readFileSync(join(root, 'apps.html'), 'utf8'), appsPage('en'));
  assert.equal(readFileSync(join(root, 'es/apps.html'), 'utf8'), appsPage('es'));
});

test('the install pages link every app and only local icons', () => {
  for (const lang of ['en', 'es']) {
    const html = appsPage(lang);
    for (const [, src] of html.matchAll(/<img src="([^"]+)"/g)) assert.ok(existsSync(join(root, lang === 'es' ? 'es' : '', src)), src);
    for (const [, href] of html.matchAll(/<a class="btn" href="([^"]+)"/g)) {
      const p = join(root, lang === 'es' ? 'es' : '', href);
      assert.ok(existsSync(href.endsWith('/') ? join(p, 'index.html') : p), href);
    }
  }
});
