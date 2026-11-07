// Near-duplicate check for the site, the same method as research/scouting/site_audit.py (PR #2):
// take each page's <main> text, drop the digits, and compare 5-word sequences between pages.
//   node tools/seo-audit.mjs        prints a table, exits 1 if any page is a near-duplicate
// "shared" = share of a page's 5-word sequences that also appear on its closest sibling.
// "unique" = share that appears on no other page.
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join, dirname, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
export const LIMIT_SHARED = 0.5; // a page sharing half its wording with a sibling is a near-duplicate

function pagesIn(dir) {
  const out = [];
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) { if (!/^(node_modules|test|tools|lib|img|downloads|emails|lead-magnet)$/.test(name)) out.push(...pagesIn(p)); }
    else if (name === 'index.html') out.push(p);
  }
  return out;
}

export function mainText(html) {
  const m = html.match(/<main>([\s\S]*?)<\/main>/);
  return (m ? m[1] : html)
    .replace(/<(script|style|form)[\s\S]*?<\/\1>/g, ' ')
    .replace(/<[^>]+>/g, ' ').replace(/&[a-z#0-9]+;/g, ' ')
    .toLowerCase().replace(/[0-9]/g, '').replace(/[^a-z' ]+/g, ' ').split(/\s+/).filter(Boolean);
}

const shingles = (words) => new Set(words.slice(0, Math.max(0, words.length - 4)).map((_, i) => words.slice(i, i + 5).join(' ')));

export function audit(dir = root) {
  const pages = pagesIn(dir).map((f) => {
    const html = readFileSync(f, 'utf8');
    const path = relative(dir, f).replace(/index\.html$/, '') || '/';
    return { path, noindex: /name="robots" content="[^"]*noindex/.test(html), words: mainText(html) };
  }).filter((p) => !p.noindex && p.words.length >= 60);
  for (const p of pages) p.set = shingles(p.words);
  return pages.map((p) => {
    let shared = 0, closest = '';
    const others = new Set();
    for (const q of pages) {
      if (q === p) continue;
      let n = 0;
      for (const s of p.set) if (q.set.has(s)) { n++; others.add(s); }
      if (n / p.set.size > shared) { shared = n / p.set.size; closest = q.path; }
    }
    return { path: p.path, words: p.words.length, shared, closest, unique: 1 - others.size / p.set.size };
  }).sort((a, b) => b.shared - a.shared);
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const rows = audit();
  const pct = (x) => `${Math.round(x * 100)}%`;
  console.log('| Page | Words | Shared with closest | Closest | Unique |\n|---|---|---|---|---|');
  for (const r of rows) console.log(`| ${r.path} | ${r.words} | ${pct(r.shared)} | ${r.closest} | ${pct(r.unique)} |`);
  process.exit(rows.some((r) => r.shared > LIMIT_SHARED) ? 1 : 0);
}
