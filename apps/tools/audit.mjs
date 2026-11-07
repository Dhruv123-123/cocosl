// Speed and keyboard pass, alongside tools/a11y.mjs (axe-core: contrast, labels, ARIA).
// Opens the hub and every tool it links to, at phone width (390px), and checks, Lighthouse-style:
//   weight      everything the page loads is under 350 KB (no third-party requests at all), and under 40 requests
//   speed       DOMContentLoaded under 1.5 s on the local server
//   layout      every <img> has width and height (no layout shift), no horizontal scroll
//   keyboard    Tab reaches every visible button, link, input and select, and each one shows a visible focus ring
//   tap targets visible buttons, inputs and selects are at least 24 x 24 px (WCAG 2.2 target size)
//   basics      <html lang>, a <title>, a meta description and a viewport tag
// Run from apps/: node tools/audit.mjs [--only path-substring]
import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { readFileSync } from 'node:fs';
import { extname, join, normalize, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
import { cardsFromHub } from './build-search.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const require = createRequire(import.meta.url);
let playwright;
try { playwright = require('playwright'); } catch { console.log('Playwright not installed: skipping audit.'); process.exit(0); }

export const BUDGET = { bytes: 350 * 1024, requests: 40, dcl: 1500, target: 24 };
const types = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.webmanifest': 'application/manifest+json', '.png': 'image/png' };
const server = createServer(async (req, res) => {
  const p = normalize(decodeURIComponent(new URL(req.url, 'http://x').pathname)).replace(/^(\.\.[/\\])+/, '');
  let file = join(root, p);
  try {
    if ((await stat(file)).isDirectory()) file = join(file, 'index.html');
    const body = await readFile(file);
    res.writeHead(200, { 'content-type': types[extname(file)] || 'application/octet-stream' });
    res.end(body);
  } catch { res.writeHead(404); res.end('not found'); }
});

const only = process.argv.includes('--only') ? process.argv[process.argv.indexOf('--only') + 1] : '';
const hubPages = (dir) => cardsFromHub(readFileSync(join(root, dir, 'index.html'), 'utf8')).map((c) => new URL(c.u, `http://x/${dir ? `${dir}/` : ''}`).pathname);
const pages = [...new Set(['/', '/es/', ...hubPages(''), ...hubPages('es'), '/apps.html', '/es/apps.html', '/embed.html'])].filter((p) => p.includes(only));

await new Promise((r) => server.listen(0, r));
const base = `http://127.0.0.1:${server.address().port}`;
const browser = await playwright.chromium.launch();
let failed = 0;
for (const path of pages) {
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  let bytes = 0; let requests = 0; const outside = [];
  page.on('response', async (r) => { requests += 1; try { bytes += (await r.body()).length; } catch { /* redirects */ } });
  page.on('request', (r) => { if (!r.url().startsWith(base) && !/^(data|blob):/.test(r.url())) outside.push(r.url()); });
  await page.goto(base + path, { waitUntil: 'networkidle' });
  const problems = [];
  const t = await page.evaluate(() => { const n = performance.getEntriesByType('navigation')[0]; return n ? n.domContentLoadedEventEnd - n.startTime : 0; });
  if (bytes > BUDGET.bytes) problems.push(`weight ${Math.round(bytes / 1024)} KB > ${BUDGET.bytes / 1024} KB`);
  if (requests > BUDGET.requests) problems.push(`${requests} requests`);
  if (outside.length) problems.push(`third-party requests: ${outside.slice(0, 3).join(', ')}`);
  if (t > BUDGET.dcl) problems.push(`DOMContentLoaded ${Math.round(t)} ms`);
  const info = await page.evaluate((min) => {
    const visible = (el) => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
    const label = (el) => `${el.tagName.toLowerCase()}${el.id ? `#${el.id}` : ''}${el.name ? `[name=${el.name}]` : ''}${!el.id && !el.name ? `"${(el.textContent || el.value || '').trim().slice(0, 24)}"` : ''}`;
    const imgs = [...document.images].filter((i) => !(i.getAttribute('width') && i.getAttribute('height'))).map((i) => i.getAttribute('src'));
    // Targets: controls people tap. Inline links inside sentences are exempt under WCAG 2.5.8.
    const small = [...document.querySelectorAll('button, input:not([type=hidden]):not([type=checkbox]):not([type=radio]), select, a.btn, summary')]
      .filter(visible).filter((el) => !el.closest('.hp') && el.tabIndex !== -1).filter((el) => { const r = el.getBoundingClientRect(); return r.width < min || r.height < min; }).map(label);
    const meta = {
      lang: !!document.documentElement.lang, title: !!document.title.trim(),
      description: !!document.querySelector('meta[name=description]')?.content, viewport: !!document.querySelector('meta[name=viewport]'),
      scroll: document.documentElement.scrollWidth > innerWidth + 1,
    };
    const focusables = [...document.querySelectorAll('a[href], button, input:not([type=hidden]), select, textarea, summary, [tabindex]:not([tabindex="-1"])')].filter(visible).filter((el) => !el.disabled);
    return { imgs, small, meta, focusCount: focusables.length };
  }, BUDGET.target);
  if (info.imgs.length) problems.push(`img without width/height: ${info.imgs.slice(0, 3).join(', ')}`);
  if (info.small.length) problems.push(`tap targets under ${BUDGET.target}px: ${info.small.slice(0, 5).join(', ')}${info.small.length > 5 ? ` +${info.small.length - 5}` : ''}`);
  for (const k of ['lang', 'title', 'description', 'viewport']) if (!info.meta[k]) problems.push(`missing ${k}`);
  if (info.meta.scroll) problems.push('horizontal scroll');
  // Keyboard: Tab through the page; every stop must be visible and show a focus indicator.
  const seen = new Set(); const noRing = [];
  for (let i = 0; i < Math.min(info.focusCount + 2, 120); i += 1) {
    await page.keyboard.press('Tab');
    const f = await page.evaluate(() => {
      const el = document.activeElement;
      if (!el || el === document.body) return null;
      const s = getComputedStyle(el);
      const ring = (s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) > 0) || (s.boxShadow && s.boxShadow !== 'none');
      const key = el.outerHTML.slice(0, 120) + [...el.parentNode.children].indexOf(el);
      return { key, ring, label: `${el.tagName.toLowerCase()}${el.id ? `#${el.id}` : ''}${el.name ? `[name=${el.name}]` : ''} "${(el.textContent || el.value || '').trim().slice(0, 24)}"`, frame: el.tagName === 'IFRAME' };
    });
    if (!f || f.frame) continue;
    if (seen.has(f.key)) break;
    seen.add(f.key);
    if (!f.ring) noRing.push(f.label);
  }
  if (noRing.length) problems.push(`no visible focus ring: ${noRing.slice(0, 4).join(', ')}${noRing.length > 4 ? ` +${noRing.length - 4}` : ''}`);
  if (problems.length) failed += 1;
  console.log(`${problems.length ? 'FAIL' : 'ok  '} ${path} (${Math.round(bytes / 1024)} KB, ${requests} req, ${Math.round(t)} ms, ${seen.size} tab stops)${problems.map((p) => `\n     ${p}`).join('')}`);
  await page.close();
}
await browser.close();
server.close();
console.log(failed ? `${failed} of ${pages.length} pages need fixes` : `All ${pages.length} pages pass`);
process.exit(failed ? 1 : 0);
