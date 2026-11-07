// Static accessibility and speed basics for every HTML page on the site (tools/audit.mjs and tools/a11y.mjs
// check the hub-linked pages in a real browser; this covers every page, fast, on every test run):
// lang, title, description, a zoomable viewport, images with alt and size, form fields with a label,
// no third-party scripts or stylesheets, and pages kept light.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';
import { ROOT } from '../../tools/sync-shared.mjs';

const SKIP = new Set(['node_modules', '.netlify', 'scam-extension', 'test']);
function walk(dir, out = []) {
  for (const f of readdirSync(dir)) {
    if (SKIP.has(f) || f.startsWith('.')) continue;
    const p = join(dir, f);
    if (statSync(p).isDirectory()) walk(p, out); else if (f.endsWith('.html')) out.push(p);
  }
  return out;
}
const pages = walk(ROOT).map((p) => ({ file: relative(ROOT, p), html: readFileSync(p, 'utf8') }));
// Fragments and redirect stubs that are not full pages.
const isPage = (h) => /<html/i.test(h) && !/http-equiv="refresh"/i.test(h);

test('found the site pages', () => assert.ok(pages.length > 80, String(pages.length)));

for (const { file, html } of pages.filter((p) => isPage(p.html))) {
  test(`${file}: page basics`, () => {
    assert.match(html, /<html[^>]* lang="[a-z]{2}(-[A-Z]{2})?"/, 'lang');
    assert.match(html, /<title>[^<]{5,}<\/title>/, 'title');
    assert.match(html, /<meta name="viewport" content="width=device-width, initial-scale=1(, viewport-fit=cover)?"/, 'viewport');
    assert.doesNotMatch(html, /user-scalable\s*=\s*no|maximum-scale\s*=\s*1(\.0)?[",]/, 'zoom allowed');
    const body = html.replace(/<script[\s\S]*?<\/script>/g, '');
    for (const [img] of body.matchAll(/<img\b[^>]*>/g)) {
      assert.match(img, /\balt="/, `alt on ${img}`);
      assert.match(img, /\bwidth="\d+"/, `width on ${img}`);
      assert.match(img, /\bheight="\d+"/, `height on ${img}`);
    }
    // Every visible field has a label: wrapped in <label>, a <label for>, aria-label or aria-labelledby.
    const ids = new Set([...body.matchAll(/<label[^>]*\bfor="([^"]+)"/g)].map((m) => m[1]));
    const labelled = (field, at) => {
      if (/type="(hidden|submit|button|reset)"/.test(field) || /aria-label(ledby)?="/.test(field)) return true;
      const id = /\bid="([^"]+)"/.exec(field)?.[1];
      if (id && ids.has(id)) return true;
      const before = body.slice(0, at);
      return before.lastIndexOf('<label') > before.lastIndexOf('</label>');
    };
    for (const m of body.matchAll(/<(input|select|textarea)\b[^>]*>/g)) assert.ok(labelled(m[0], m.index), `label for ${m[0].slice(0, 90)}`);
    // No third-party code: scripts and stylesheets come from this site (Google Fonts and Plausible analytics excepted).
    for (const [, src] of html.matchAll(/<script[^>]+src="(https?:[^"]+)"/g)) assert.match(src, /plausible\.io/, `third-party script ${src}`);
    for (const [, href] of html.matchAll(/<link[^>]+rel="stylesheet"[^>]+href="(https?:[^"]+)"/g)) assert.match(href, /fonts\.googleapis\.com/, `third-party stylesheet ${href}`);
    assert.ok(html.length < 150 * 1024, `${Math.round(html.length / 1024)} KB of HTML`);
  });
}

test('pages without a meta description are only thank-you and utility pages', () => {
  const missing = pages.filter((p) => isPage(p.html) && !/<meta name="description" content="[^"]{20,}"/.test(p.html)).map((p) => p.file);
  const ok = (f) => /(thanks|gracias|offline|privacy|success|welcome|404)/.test(f) || /\/embed\//.test(f);
  assert.deepEqual(missing.filter((f) => !ok(f)), []);
});
