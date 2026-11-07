// Offline phishing-domain list for the link checker. The address someone checks never leaves the browser:
// the page downloads one small file (phishlist/phish.bin) and looks the address up locally.
//
// The file is a Golomb-Rice coded set of hashed domain names (the same idea as a Bitcoin "GCS" filter).
// Each domain is hashed to a number below n * 2^K; the sorted numbers are stored as gaps, each written as
// a unary quotient and a K-bit remainder. That's about K + 1.5 bits a domain, instead of ~20 bytes as text.
// A host that isn't on the list matches by chance about 1 time in 2^K (K = 19: about 1 in 500,000).
//
// Data: DestroyList (MIT) and Phishing.Database (MIT). See apps/THIRD_PARTY.md and
// scam-checker/tools/refresh-blocklist.mjs, which rebuilds the file.

export const MAGIC = 'PHS1';

/** cyrb53: a fast 53-bit string hash. Same answer in node and every browser. */
export function hash53(str, seed = 0) {
  let h1 = 0xdeadbeef ^ seed;
  let h2 = 0x41c6ce57 ^ seed;
  for (let i = 0; i < str.length; i++) {
    const ch = str.charCodeAt(i);
    h1 = Math.imul(h1 ^ ch, 2654435761);
    h2 = Math.imul(h2 ^ ch, 1597334677);
  }
  h1 = Math.imul(h1 ^ (h1 >>> 16), 2246822507) ^ Math.imul(h2 ^ (h2 >>> 13), 3266489909);
  h2 = Math.imul(h2 ^ (h2 >>> 16), 2246822507) ^ Math.imul(h1 ^ (h1 >>> 13), 3266489909);
  return 4294967296 * (2097151 & h2) + (h1 >>> 0);
}

const TWO_PART = ['co.uk', 'org.uk', 'com.mx', 'com.au', 'co.in', 'com.br', 'co.jp', 'com.ar', 'com.co'];
/** The host and each parent domain down to the registrable one: a.b.evil.com -> a.b.evil.com, b.evil.com, evil.com. */
export function candidates(host) {
  const h = String(host || '').toLowerCase().replace(/\.$/, '').replace(/^www\./, '');
  if (!h || !h.includes('.') || /^[\d.]+$/.test(h)) return h ? [h] : [];
  const parts = h.split('.');
  const min = TWO_PART.includes(parts.slice(-2).join('.')) ? 3 : 2;
  const out = [];
  for (let i = 0; parts.length - i >= min; i++) out.push(parts.slice(i).join('.'));
  return out;
}

/** Normalise one line of a source list to a bare lowercase hostname, or '' to skip it. */
export function cleanDomain(line) {
  let s = String(line || '').trim().toLowerCase();
  if (!s || s.startsWith('#') || s.startsWith('!')) return '';
  s = s.replace(/^(0\.0\.0\.0|127\.0\.0\.1)\s+/, '').replace(/^\|\|/, '').replace(/\^.*$/, '').replace(/^\*\./, '').replace(/^www\./, '').replace(/\.$/, '');
  if (!/^[a-z0-9_-]+(\.[a-z0-9_-]+)+$/.test(s) || s.length > 253) return '';
  return s;
}

// ---------- encode (refresh script and tests) ----------
export function encode(domains, { k = 19, date = '' } = {}) {
  const list = [...new Set(domains)];
  const n = list.length;
  const m = n * 2 ** k;
  const vals = Float64Array.from(list.map((d) => hash53(d) % m)).sort();
  const bytes = [];
  let cur = 0; let bits = 0;
  const put = (bit) => { cur = (cur << 1) | bit; bits++; if (bits === 8) { bytes.push(cur); cur = 0; bits = 0; } };
  let prev = 0;
  for (const v of vals) {
    const gap = v - prev; prev = v;
    const q = Math.floor(gap / 2 ** k);
    const r = gap - q * 2 ** k;
    for (let i = 0; i < q; i++) put(1);
    put(0);
    for (let b = k - 1; b >= 0; b--) put(Math.floor(r / 2 ** b) % 2);
  }
  if (bits) { cur <<= 8 - bits; bytes.push(cur); }
  // Header: "PHS1", k (1 byte), n (4 bytes), date "YYYY-MM-DD" (10 bytes).
  const head = new Uint8Array(19);
  head.set([...MAGIC].map((c) => c.charCodeAt(0)), 0);
  head[4] = k;
  new DataView(head.buffer).setUint32(5, n);
  head.set([...String(date).padEnd(10).slice(0, 10)].map((c) => c.charCodeAt(0)), 9);
  const out = new Uint8Array(head.length + bytes.length);
  out.set(head, 0); out.set(bytes, head.length);
  return out;
}

// ---------- decode and look up (browser) ----------
/** Decode a phish.bin buffer into { k, n, m, date, vals (sorted Float64Array) }. */
export function decode(buf) {
  const u8 = buf instanceof Uint8Array ? buf : new Uint8Array(buf);
  if (u8.length < 19 || String.fromCharCode(...u8.subarray(0, 4)) !== MAGIC) throw new Error('not a phish list');
  const k = u8[4];
  const n = new DataView(u8.buffer, u8.byteOffset).getUint32(5);
  const date = String.fromCharCode(...u8.subarray(9, 19)).trim();
  const vals = new Float64Array(n);
  let pos = 19 * 8; const end = u8.length * 8;
  const bit = () => { const b = (u8[pos >> 3] >> (7 - (pos & 7))) & 1; pos++; return b; };
  let prev = 0;
  for (let i = 0; i < n; i++) {
    let q = 0;
    while (pos < end && bit()) q++;
    let r = 0;
    for (let b = 0; b < k; b++) r = r * 2 + bit();
    prev += q * 2 ** k + r;
    vals[i] = prev;
  }
  return { k, n, m: n * 2 ** k, date, vals };
}

function hasVal(vals, v) {
  let lo = 0; let hi = vals.length - 1;
  while (lo <= hi) { const mid = (lo + hi) >> 1; if (vals[mid] === v) return true; if (vals[mid] < v) lo = mid + 1; else hi = mid - 1; }
  return false;
}

/** The first of the host's candidate domains that is on the list, or null. */
export function lookup(set, host) {
  if (!set || !set.n) return null;
  for (const c of candidates(host)) if (hasVal(set.vals, hash53(c) % set.m)) return c;
  return null;
}

let loading = null;
/** Fetch and decode the list once per page. Resolves to null if it can't be loaded (the checker still works). */
export function loadBlocklist(url, fetchImpl = globalThis.fetch) {
  if (!loading) {
    loading = fetchImpl(url).then((r) => (r.ok ? r.arrayBuffer() : null)).then((b) => (b ? decode(b) : null)).catch(() => null);
  }
  return loading;
}
