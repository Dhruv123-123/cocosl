// Rebuild phishlist/phish.bin, the offline phishing-domain list the link checker uses.
//   node scam-checker/tools/refresh-blocklist.mjs            (download fresh lists, then build)
//   node scam-checker/tools/refresh-blocklist.mjs --from dir (build from files already downloaded)
// Run it every week or two, then `node tools/build-app-shell.mjs`, `npm test`, and commit.
//
// What goes in (both lists are MIT; credits in apps/THIRD_PARTY.md):
//   1. DestroyList "Primary Active": curated phishing domains whose DNS still resolves (checked daily).
//   2. Phishing.Database "ACTIVE" domains that DestroyList also lists (Primary or Community Active), so a
//      domain from it has two independent reports. All of Phishing.Database is ~390,000 domains, too big to ship.
// What's taken out:
//   - DestroyList's allowlist (its false-positive list), and every official domain the checker knows.
//   - Shared hosts: if one parent domain has 25+ listed subdomains (pages.dev, duckdns.org, github.io) only
//     the subdomains are kept, never the parent, so a real site on that host isn't flagged.
// The file must stay under MAX_BYTES (checked by test/blocklist.test.js); past MAX_ENTRIES, or if the file
// would be too big, the end of the list is trimmed, so DestroyList entries are kept first.
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { cleanDomain, encode, candidates } from '../lib/blocklist.js';
import { OFFICIAL_DOMAINS } from '../lib/scan.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT = join(HERE, '..', 'phishlist');
export const K = 19;
export const MAX_BYTES = 420 * 1024;
export const MAX_ENTRIES = 170000;
export const SOURCES = {
  primaryActive: 'https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary_active/domains.txt',
  primary: 'https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/primary/domains.txt',
  communityActive: 'https://raw.githubusercontent.com/phishdestroy/destroylist/main/rootlist/formats/community_active/domains.txt',
  allow: 'https://raw.githubusercontent.com/phishdestroy/destroylist/main/allow/allowlist.json',
  phishingDatabase: 'https://raw.githubusercontent.com/Phishing-Database/Phishing.Database/master/phishing-domains-ACTIVE.txt',
};
const FILES = { primaryActive: 'dl-primary-active.txt', primary: 'dl-primary.txt', communityActive: 'dl-community-active.txt', allow: 'dl-allowlist.json', phishingDatabase: 'pd-active.txt' };

const lines = (text) => text.split(/\r?\n/).map(cleanDomain).filter(Boolean);

/** Pure: build the domain list from the five source texts. Exported for the tests. */
export function buildList({ primaryActive, primary, communityActive, allow, phishingDatabase }, { maxEntries = MAX_ENTRIES } = {}) {
  const a = lines(primaryActive);
  const dl = new Set([...lines(primary), ...lines(communityActive), ...a]);
  const pd = lines(phishingDatabase).filter((d) => dl.has(d));
  const allowed = new Set();
  const allowSuffix = [];
  for (const x of JSON.parse(allow || '[]')) {
    const s = String(x).toLowerCase().trim();
    if (s.startsWith('.')) allowSuffix.push(s); else if (s) allowed.add(s);
  }
  const official = Object.values(OFFICIAL_DOMAINS).flat().map((d) => d.replace(/^\./, ''));
  const isAllowed = (d) => allowed.has(d) || allowSuffix.some((s) => d.endsWith(s) || d === s.slice(1))
    || official.some((o) => d === o || d.endsWith('.' + o));
  let list = [...new Set([...a, ...pd])].filter((d) => !isAllowed(d));
  // Shared hosts: a parent with many listed children is a platform, not a scam site.
  const kids = new Map();
  for (const d of list) for (const p of candidates(d).slice(1)) kids.set(p, (kids.get(p) || 0) + 1);
  const shared = new Set([...kids].filter(([, c]) => c >= 25).map(([p]) => p));
  list = list.filter((d) => !shared.has(d));
  if (list.length > maxEntries) list = list.slice(0, maxEntries);
  return { list, counts: { destroyList: a.length, phishingDatabaseBoth: pd.length, kept: list.length }, shared: [...shared].sort() };
}

async function main() {
  const fromIdx = process.argv.indexOf('--from');
  const texts = {};
  if (fromIdx > 0) {
    const dir = process.argv[fromIdx + 1];
    for (const [key, f] of Object.entries(FILES)) texts[key] = readFileSync(join(dir, f), 'utf8');
  } else {
    for (const [key, url] of Object.entries(SOURCES)) {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`${url}: ${res.status}`);
      texts[key] = await res.text();
      console.log(`downloaded ${key}: ${Math.round(texts[key].length / 1024)} KB`);
    }
  }
  const { list, counts, shared } = buildList(texts);
  const date = new Date().toISOString().slice(0, 10);
  let bin = encode(list, { k: K, date });
  let kept = list;
  while (bin.length > MAX_BYTES) { kept = kept.slice(0, Math.floor(kept.length * 0.95)); bin = encode(kept, { k: K, date }); }
  if (!existsSync(OUT)) mkdirSync(OUT, { recursive: true });
  writeFileSync(join(OUT, 'phish.bin'), bin);
  const meta = { date, entries: kept.length, bytes: bin.length, k: K, falseMatchOdds: `about 1 in ${(2 ** K).toLocaleString('en-US')} per address`, counts, sharedHostsSkipped: shared.length, sample: kept.find((d) => d.split('.').length === 2) || kept[0], sources: SOURCES };
  writeFileSync(join(OUT, 'phish-meta.json'), `${JSON.stringify(meta, null, 2)}\n`);
  console.log(`phishlist/phish.bin: ${kept.length.toLocaleString('en-US')} domains, ${Math.round(bin.length / 1024)} KB (limit ${MAX_BYTES / 1024} KB)`);
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) main().catch((e) => { console.error(e.message); process.exit(1); });
