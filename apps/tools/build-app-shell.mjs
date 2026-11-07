// Work out every file the Money Made Simple app (app/) has to save so its ten tools open offline:
// each tool's page, plus every local script, stylesheet and icon it loads, following static
// `import ... from './x.js'` and literal `import('./x.js')` all the way down. Writes app/precache.json.
// Also writes scam-checker/sw.js, the Scam Shield app's worker, with its own install list
// (scam-checker deploys on its own too, so that list never leaves scam-checker/).
// Run from apps/: node tools/build-app-shell.mjs   (a test checks both files are up to date)
import { readFileSync, writeFileSync, existsSync, statSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { join, dirname, posix } from 'node:path';
import { fileURLToPath } from 'node:url';
import { TOOLS, urlFor } from '../app/tools.js';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const SHELL = ['app/', 'app/app.js', 'app/tools.js', 'app/manifest.webmanifest', 'budget/icon-192.png', 'budget/icon-512.png', 'budget/icon-maskable-512.png', 'sw.js'];

const fileOf = (u) => { const f = join(ROOT, u); return existsSync(f) && statSync(f).isDirectory() ? join(f, 'index.html') : f; };
const local = (ref) => ref && !/^(https?:|data:|mailto:|tel:|#|\/\/)/.test(ref);
const clean = (ref) => ref.split('#')[0].split('?')[0];

/** Site-relative paths (from apps/) that one page or script needs, not counting itself. */
export function refsOf(path, text) {
  const base = path.endsWith('/') ? path : posix.dirname(path) + '/';
  const out = new Set();
  const add = (ref) => { if (local(ref)) { const p = posix.normalize(base + clean(ref)); if (p && !p.startsWith('..')) out.add(p); } };
  if (/\.html$|\/$/.test(path)) {
    for (const m of text.matchAll(/<script[^>]*\ssrc="([^"]+)"/g)) add(m[1]);
    for (const m of text.matchAll(/<link[^>]*\srel="(?:stylesheet|icon|manifest|apple-touch-icon)"[^>]*\shref="([^"]+)"/g)) add(m[1]);
    for (const m of text.matchAll(/<link[^>]*\shref="([^"]+)"[^>]*\srel="(?:stylesheet|icon|manifest|apple-touch-icon)"/g)) add(m[1]);
  } else if (path.endsWith('.js')) {
    for (const m of text.matchAll(/(?:^|[\s;])(?:import|export)\s[^'"`;]*?from\s*'([^']+)'/gm)) add(m[1]);
    for (const m of text.matchAll(/^import\s+'([^']+)'/gm)) add(m[1]);
    for (const m of text.matchAll(/import\(\s*'([^']+)'\s*\)/g)) add(m[1]);
  }
  return [...out];
}

export function crawl(starts) {
  const seen = new Set();
  const queue = [...starts];
  while (queue.length) {
    const p = queue.shift();
    if (seen.has(p)) continue;
    const f = fileOf(p);
    if (!existsSync(f)) throw new Error(`missing: ${p}`);
    seen.add(p);
    if (/\.(html|js)$|\/$/.test(p)) for (const r of refsOf(p, readFileSync(f, 'utf8'))) if (!seen.has(r)) queue.push(r);
  }
  return [...seen].sort();
}

const fromApp = (u) => posix.normalize(`app/${u}`);
export function buildPrecache() {
  const lists = {};
  for (const lang of ['en', 'es']) lists[lang] = crawl([...SHELL, ...TOOLS.map((t) => fromApp(urlFor(t, lang)))]);
  const hash = createHash('sha256');
  for (const p of [...new Set([...lists.en, ...lists.es])].sort()) hash.update(p).update(readFileSync(fileOf(p)));
  return { version: hash.digest('hex').slice(0, 12), en: lists.en, es: lists.es };
}

// ---------- Scam Shield app (scam-checker/app/) ----------
const SCAM_STARTS = ['scam-checker/app/', 'scam-checker/app/checklist.html', 'scam-checker/app/quiz.html', 'scam-checker/app/report.html', 'scam-checker/app/manifest.webmanifest',
  'scam-checker/app/icon-192.png', 'scam-checker/app/icon-512.png', 'scam-checker/app/icon-maskable-512.png',
  'scam-checker/', 'scam-checker/link/', 'scam-checker/family/', 'scam-checker/scams/', 'scam-checker/privacy.html', 'scam-checker/es/', 'scam-checker/es/enlace/'];

// ---------- 1099 Money app (freelance-invoices/app/) ----------
const TEN99_STARTS = ['freelance-invoices/app/', 'freelance-invoices/app/quarterly.html', 'freelance-invoices/app/mileage.html', 'freelance-invoices/app/deductions.html',
  'freelance-invoices/app/manifest.webmanifest', 'freelance-invoices/app/icon-192.png', 'freelance-invoices/app/icon-512.png', 'freelance-invoices/app/icon-maskable-512.png',
  'freelance-invoices/', 'freelance-invoices/side-hustle.html', 'freelance-invoices/rate.html', 'freelance-invoices/set-aside/'];

export const buildScamSw = () => buildSiteSw('scam-checker', SCAM_STARTS, 'scam-shield', 'Scam Shield');
export const buildTen99Sw = () => buildSiteSw('freelance-invoices', TEN99_STARTS, 'money-1099', '1099 Money');

/** A service worker for one app folder (which can deploy on its own), with every file its pages need. */
export function buildSiteSw(dir, starts, cachePrefix, name) {
  const files = crawl(starts);
  for (const f of files) if (!f.startsWith(`${dir}/`)) throw new Error(`outside ${dir}: ${f}`);
  const rel = files.map((f) => f.slice(dir.length + 1) || './');
  const hash = createHash('sha256');
  for (const f of files) hash.update(f).update(readFileSync(fileOf(f)));
  const version = `${cachePrefix}-${hash.digest('hex').slice(0, 12)}`;
  return `// GENERATED by tools/build-app-shell.mjs. Do not edit: change the pages, then run it again.
// Offline support for the ${name} site and app (scope: this folder). Pages are network first, so
// people get updates online and the saved copy offline; files are served from the cache at once.
// Nothing anyone types is cached, and only GETs to this site are touched.
const VERSION = '${version}';
const SHELL = ${JSON.stringify(rel, null, 0).replace(/","/g, '", "')};

self.addEventListener('install', (e) => e.waitUntil(caches.open(VERSION).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting())));
self.addEventListener('activate', (e) => e.waitUntil(
  caches.keys().then((keys) => Promise.all(keys.filter((k) => k.startsWith('${cachePrefix}-') && k !== VERSION).map((k) => caches.delete(k)))).then(() => self.clients.claim()),
));
self.addEventListener('fetch', (e) => {
  const req = e.request;
  const url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== self.location.origin || url.pathname.startsWith('/api/')) return;
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).then((res) => {
      if (res.ok) { const copy = res.clone(); caches.open(VERSION).then((c) => c.put(req, copy)); }
      return res;
    }).catch(async () => (await caches.match(req, { ignoreSearch: true })) || caches.match(new URL('app/', self.registration.scope).href)));
    return;
  }
  e.respondWith(caches.match(req).then((hit) => {
    const fresh = fetch(req).then((res) => {
      if (res.ok) { const copy = res.clone(); caches.open(VERSION).then((c) => c.put(req, copy)); }
      return res;
    }).catch(() => hit);
    return hit || fresh;
  }));
});
`;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  writeFileSync(join(ROOT, 'scam-checker', 'sw.js'), buildScamSw());
  writeFileSync(join(ROOT, 'freelance-invoices', 'sw.js'), buildTen99Sw());
  console.log('scam-checker/sw.js and freelance-invoices/sw.js written');
  const pc = buildPrecache();
  writeFileSync(join(ROOT, 'app', 'precache.json'), `${JSON.stringify(pc, null, 1)}\n`);
  console.log(`app/precache.json: ${pc.en.length} files (en), ${pc.es.length} (es), version ${pc.version}`);
}
