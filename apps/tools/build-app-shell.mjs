// Work out every file the Money Made Simple app (app/) has to save so its ten tools open offline:
// each tool's page, plus every local script, stylesheet and icon it loads, following static
// `import ... from './x.js'` and literal `import('./x.js')` all the way down. Writes app/precache.json.
// Run from apps/: node tools/build-app-shell.mjs   (CI checks the file is up to date)
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

if (import.meta.url === `file://${process.argv[1]}`) {
  const pc = buildPrecache();
  writeFileSync(join(ROOT, 'app', 'precache.json'), `${JSON.stringify(pc, null, 1)}\n`);
  console.log(`app/precache.json: ${pc.en.length} files (en), ${pc.es.length} (es), version ${pc.version}`);
}
