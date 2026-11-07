import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { TOOLS, urlFor } from '../../app/tools.js';
import { buildPrecache, refsOf } from '../../tools/build-app-shell.mjs';
import { appHomeUrl, addAppHome, homesFrom } from '../app-home.js';

const root = join(dirname(fileURLToPath(import.meta.url)), '..', '..');

test('the app has ten tools and every page exists in both languages', () => {
  assert.equal(TOOLS.length, 10);
  assert.equal(new Set(TOOLS.map((t) => t.id)).size, 10);
  for (const t of TOOLS) for (const lang of ['en', 'es']) {
    const p = join(root, 'app', urlFor(t, lang));
    assert.ok(existsSync(p.endsWith('/') ? join(p, 'index.html') : p), `${t.id} ${lang}`);
    assert.ok(t.name[lang] && t.blurb[lang], `${t.id} ${lang} text`);
  }
});

test('precache.json is up to date and covers each tool page and its scripts', () => {
  const pc = buildPrecache();
  assert.deepEqual(JSON.parse(readFileSync(join(root, 'app', 'precache.json'), 'utf8')), pc, 'run: node tools/build-app-shell.mjs');
  for (const f of ['budget/split-bills.html', 'budget/lib/splitbills.js', 'budget/lib/app-home.js', 'money-calculators/take-home-pay/', 'money-calculators/lib/state-tax-2026.js', 'scam-checker/lib/scan.js', 'app/app.js']) assert.ok(pc.en.includes(f), f);
  assert.ok(pc.es.includes('budget/dividir-gastos.html') && pc.es.includes('money-calculators/es/take-home-pay/'));
});

test('refsOf follows scripts, styles and imports', () => {
  assert.deepEqual(refsOf('budget/x.html', '<link rel="stylesheet" href="style.css"><script type="module" src="x.js"></script><a href="other.html">').sort(), ['budget/style.css', 'budget/x.js']);
  assert.deepEqual(refsOf('budget/lib/a.js', "import { b } from './b.js';\nimport c from '../c.js';\nconst d = await import('./d.js');\nimport x from 'https://cdn/x.js';").sort(), ['budget/c.js', 'budget/lib/b.js', 'budget/lib/d.js']);
});

test('the app manifest opens tool pages inside the app', () => {
  const m = JSON.parse(readFileSync(join(root, 'app', 'manifest.webmanifest'), 'utf8'));
  assert.equal(m.scope, '../');
  assert.equal(m.id, '/app/');
  assert.match(readFileSync(join(root, 'app', 'app.js'), 'utf8'), /register\('\.\.\/sw\.js', \{ scope: '\.\.\/' \}\)/);
});

test('no service worker deletes another app\'s cache', () => {
  for (const f of ['sw.js', 'budget/sw.js', 'budget/bill-calendar/sw.js', 'freelance-invoices/set-aside/sw.js']) {
    const s = readFileSync(join(root, f), 'utf8');
    assert.match(s, /k\.startsWith\('[a-z-]+'\) && k !== (CACHE|VERSION)/, f);
  }
});

test('home button only inside the installed app, not on the home screen itself', () => {
  const home = 'https://x.app/app/';
  assert.equal(appHomeUrl({ standalone: true, saved: home, here: 'https://x.app/budget/' }), home);
  assert.equal(appHomeUrl({ standalone: false, saved: home, here: 'https://x.app/budget/' }), null);
  assert.equal(appHomeUrl({ standalone: true, saved: null, here: 'https://x.app/budget/' }), null);
  assert.equal(appHomeUrl({ standalone: true, saved: home, here: 'https://x.app/app/?source=pwa' }), null);
  assert.equal(appHomeUrl({ standalone: true, saved: 'https://evil.example/app/', here: 'https://x.app/budget/' }), null);
  assert.equal(addAppHome(undefined, undefined), false);
  // Two apps: the closest scope wins.
  const both = JSON.stringify({ 'https://x.app/': 'https://x.app/app/', 'https://x.app/scam-checker/': 'https://x.app/scam-checker/app/' });
  assert.equal(appHomeUrl({ standalone: true, saved: both, here: 'https://x.app/scam-checker/link/' }), 'https://x.app/scam-checker/app/');
  assert.equal(appHomeUrl({ standalone: true, saved: both, here: 'https://x.app/budget/' }), 'https://x.app/app/');
  assert.deepEqual(homesFrom('https://x.app/app/'), { 'https://x.app/': 'https://x.app/app/' });
});

test('every service worker install list has no duplicates (Cache.addAll rejects them and the worker never installs)', () => {
  for (const f of ['sw.js', 'budget/sw.js', 'budget/bill-calendar/sw.js', 'freelance-invoices/set-aside/sw.js']) {
    const src = readFileSync(join(root, f), 'utf8').split('self.addEventListener')[0];
    const lists = {};
    for (const m of src.matchAll(/const ([A-Z]+) = (?:\[\.\.\.new Set\()?(\[[^\]]*\])/g)) {
      lists[m[1]] = JSON.parse(m[2].replace(/'/g, '"').replace(/\.\.\.([A-Z]+)/g, (_, k) => lists[k].map((x) => JSON.stringify(x)).join(',') || '"__empty__"'));
    }
    const shell = lists.SHELL;
    assert.ok(shell?.length, f);
    if (!/new Set\(/.test(src)) assert.equal(new Set(shell).size, shell.length, `${f} lists a file twice`);
    for (const p of new Set(shell)) assert.ok(existsSync(join(root, dirname(f), p.endsWith('/') || p === './' ? `${p}index.html` : p)), `${f}: ${p}`);
  }
});

test('scam-checker/sw.js is generated, up to date and stays inside scam-checker', async () => {
  const { buildScamSw } = await import('../../tools/build-app-shell.mjs');
  const sw = buildScamSw();
  assert.equal(readFileSync(join(root, 'scam-checker', 'sw.js'), 'utf8'), sw, 'run: node tools/build-app-shell.mjs');
  for (const f of ['app/', 'app/report.html', 'lib/scamapp.js', 'lib/scan.js', 'link/', 'es/']) assert.ok(sw.includes(`"${f}"`), f);
  assert.doesNotMatch(sw, /"\.\.\//);
});

test('freelance-invoices/sw.js is generated, up to date and stays inside freelance-invoices', async () => {
  const { buildTen99Sw } = await import('../../tools/build-app-shell.mjs');
  const sw = buildTen99Sw();
  assert.equal(readFileSync(join(root, 'freelance-invoices', 'sw.js'), 'utf8'), sw, 'run: node tools/build-app-shell.mjs');
  for (const f of ['app/', 'app/mileage.html', 'lib/ten99.js', 'lib/setaside.js', 'set-aside/']) assert.ok(sw.includes(`"${f}"`), f);
  assert.doesNotMatch(sw, /"\.\.\//);
});

test('every Netlify site skips the build when its folder did not change (free plan: 300 credits, 15 a deploy)', async () => {
  const { readdirSync } = await import('node:fs');
  const tomls = ['netlify.toml', ...readdirSync(root, { withFileTypes: true }).filter((d) => d.isDirectory() && existsSync(join(root, d.name, 'netlify.toml'))).map((d) => `${d.name}/netlify.toml`)];
  assert.ok(tomls.length >= 7);
  // A site that publishes on a schedule through a Netlify build hook may add `&& test -z "$INCOMING_HOOK_URL"`,
  // so hook builds run even with no new commit (INCOMING_HOOK_URL is set only on build-hook builds).
  const rule = /\[build\][^[]*ignore = "git diff --quiet \$CACHED_COMMIT_REF \$COMMIT_REF -- \.( && test -z \\"\$INCOMING_HOOK_URL\\")?"/;
  for (const t of tomls) assert.match(readFileSync(join(root, t), 'utf8'), rule, t);
  assert.match('[build]\n  ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- . && test -z \\"$INCOMING_HOOK_URL\\""', rule);
  assert.doesNotMatch('[build]\n  ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- . || true"', rule);
});
