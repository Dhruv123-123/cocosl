// Every tool on the "embed this tool" page exists, loads lib/embed-page.js (so it hides its chrome, sizes the iframe
// and shows the credit link), and the snippet page is up to date.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { join, dirname, posix } from 'node:path';
import { fileURLToPath } from 'node:url';
import { TOOLS, PLANS, embedPage } from '../../tools/build-embed-page.mjs';
import { embedState, HIDE } from '../embed-page.js';

const root = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const fileFor = (p) => (p.endsWith('/') ? `${p}index.html` : p);

for (const t of TOOLS) {
  for (const path of [t.en, t.es].filter(Boolean)) {
    test(`${path} can be embedded`, () => {
      const file = fileFor(path);
      assert.ok(existsSync(join(root, file)), `${file} exists`);
      const src = /<script type="module" src="([^"]*embed-page\.js)"><\/script>/.exec(readFileSync(join(root, file), 'utf8'))?.[1];
      assert.ok(src, `${file} loads embed-page.js`);
      const resolved = posix.normalize(posix.join(posix.dirname(file), src));
      assert.equal(resolved, `${file.split('/')[0]}/lib/embed-page.js`);
      assert.ok(existsSync(join(root, resolved)));
      // The loader only accepts paths of this shape.
      assert.match(path, /^[a-z0-9-]+(\/[a-z0-9-]+)*(\/|\.html)$/);
    });
  }
}

test('embedded state: brand and language from the path, frame ids sanitised', () => {
  assert.equal(embedState('?x=1', '/scam-checker/'), null);
  assert.deepEqual(embedState('?embed=1&frame=abc123', '/scam-checker/es/'), { frame: 'abc123', brand: 'Scam Shield', credit: 'Herramienta gratis de Scam Shield' });
  assert.equal(embedState('?embed=1&frame=<script>', '/budget/afford.html').frame, '');
  assert.equal(embedState('?embed=1', '/budget/afford.html').credit, 'Free tool by Money Made Simple');
  assert.equal(embedState('?embed=1', '/budget/plan-quincena.html').brand, 'Dinero Simple');
  assert.equal(embedState('?embed=1', '/freelance-invoices/rate.html').brand, '1099 Money');
  assert.match(HIDE, /header\.top/);
});

test('embed.html is up to date (run node tools/build-embed-page.mjs) and lists every tool and plan', () => {
  const html = readFileSync(join(root, 'embed.html'), 'utf8');
  assert.equal(html, embedPage());
  for (const t of TOOLS) assert.ok(html.includes(`value="${t.id}"`), t.id);
  for (const p of PLANS) assert.ok(html.includes(p.price), p.name);
});
