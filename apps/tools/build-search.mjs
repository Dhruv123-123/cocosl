// Builds search-index.json for the hub's search box from the hub's own tool cards, plus each tool
// page's title, meta description and headings (so FAQ questions are searchable too).
// Run from apps/: node tools/build-search.mjs   (no dependencies; Netlify runs it on deploy)
import { readFileSync, writeFileSync, existsSync, statSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const decode = (s) => s.replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;|&rsquo;/g, "'").replace(/&nbsp;/g, ' ');
const text = (html) => decode(html.replace(/<[^>]+>/g, ' ')).replace(/\s+/g, ' ').trim();

export function cardsFromHub(html) {
  const out = [];
  const sections = [...html.matchAll(/<section id="([^"]+)"[^>]*>\s*<h2[^>]*>([\s\S]*?)<\/h2>([\s\S]*?)<\/section>/g)];
  for (const [, id, h2, body] of sections) {
    for (const m of body.matchAll(/<a class="card[^"]*" href="([^"]+)">([\s\S]*?)<\/a>/g)) {
      const title = text((/<h3>([\s\S]*?)<\/h3>/.exec(m[2]) || [])[1] || '');
      const desc = text((/<p>([\s\S]*?)<\/p>/.exec(m[2]) || [])[1] || '');
      if (title) out.push({ u: m[1], t: title, d: desc, s: text(h2), sid: id });
    }
  }
  return out;
}

export function keywordsFromPage(html) {
  const bits = [];
  const title = /<title>([\s\S]*?)<\/title>/.exec(html);
  if (title) bits.push(text(title[1]).replace(/\|.*$/, ''));
  const desc = /<meta name="description" content="([^"]*)"/.exec(html);
  if (desc) bits.push(decode(desc[1]));
  for (const m of html.matchAll(/<h[1-3][^>]*>([\s\S]*?)<\/h[1-3]>/g)) bits.push(text(m[1]));
  // Unique words, so the index stays small.
  const seen = new Set();
  return bits.join(' ').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').split(/[^a-z0-9%$]+/)
    .filter((w) => w.length > 2 && !seen.has(w) && seen.add(w)).join(' ');
}

function pageFile(href) {
  const clean = href.split(/[?#]/)[0];
  const p = join(root, clean);
  if (existsSync(p) && statSync(p).isDirectory()) return join(p, 'index.html');
  return p;
}

export function buildIndex() {
  const hub = readFileSync(join(root, 'index.html'), 'utf8');
  return cardsFromHub(hub).map((c) => {
    const f = pageFile(c.u);
    return { ...c, k: existsSync(f) ? keywordsFromPage(readFileSync(f, 'utf8')) : '' };
  });
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const index = buildIndex();
  writeFileSync(join(root, 'search-index.json'), `${JSON.stringify(index)}\n`);
  console.log(`search-index.json: ${index.length} tools`);
}
