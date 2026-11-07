// Opens the calculator in Chromium at desktop and phone width, fills in a case and checks the
// result. Run: node tools/smoke.mjs [screenshotDir]   (needs Playwright; not part of `npm test`)
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { extname, join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const types = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.xml': 'application/xml', '.jpg': 'image/jpeg', '.pdf': 'application/pdf' };
const server = createServer(async (req, res) => {
  const path = join(root, decodeURIComponent(new URL(req.url, 'http://x').pathname).replace(/\/$/, '/index.html'));
  try { res.writeHead(200, { 'Content-Type': types[extname(path)] || 'text/plain' }); res.end(await readFile(path)); }
  catch { res.writeHead(404); res.end(); }
}).listen(0);
const url = `http://127.0.0.1:${server.address().port}/`;
const { chromium } = createRequire(import.meta.url)('playwright');
const browser = await chromium.launch();
const shots = process.argv[2];
let failed = false;
for (const [name, viewport] of [['desktop', { width: 1280, height: 900 }], ['phone', { width: 390, height: 844 }]]) {
  const page = await browser.newPage({ viewport });
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  page.on('console', (m) => m.type() === 'error' && errors.push(m.text()));
  await page.goto(url + '?profit=60000&status=single&nextQuarter=1&priorYearTax=6500&priorYearAgi=52000&paidSoFar=0&stateRate=0&w2Wages=0&withholding=0');
  const big = await page.textContent('.result .big');
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
  const ok = big.trim() === '$1,625' && !overflow && !errors.length;
  if (!ok) failed = true;
  console.log(name, ok ? 'ok' : 'FAIL', { big, overflow, errors });
  if (shots) await page.screenshot({ path: `${shots}/${name}.png`, fullPage: name === 'phone' });
  // The funnel pages: landing page with the signup form, and the download page.
  for (const [slug, sel] of [['free/', 'form.signup'], ['free/thanks/', 'a[download]']]) {
    await page.goto(url + slug);
    const found = await page.locator(sel).count();
    const wide = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
    const pdf = slug.includes('thanks') ? (await fetch(new URL(await page.getAttribute(sel, 'href'), page.url()))).status : 200;
    const good = found === 1 && !wide && pdf === 200 && !errors.length;
    if (!good) failed = true;
    console.log(name, slug, good ? 'ok' : 'FAIL', { found, wide, pdf, errors });
    if (shots) await page.screenshot({ path: `${shots}/${name}-${slug.replace(/\//g, '_')}.png`, fullPage: true });
  }
  await page.close();
}
await browser.close();
server.close();
process.exit(failed ? 1 : 0);
