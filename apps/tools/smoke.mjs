// Browser smoke test: serves apps/ locally, opens every page in Chromium, fails on console errors
// or missing results. Needs Playwright (`npm i -D playwright` or a preinstalled copy).
// Run from apps/: node tools/smoke.mjs [--shots dir]
import { createServer } from 'node:http';
import { readFile, stat, mkdir } from 'node:fs/promises';
import { extname, join, normalize, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const types = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.webmanifest': 'application/manifest+json', '.png': 'image/png', '.xml': 'application/xml', '.txt': 'text/plain' };

const server = createServer(async (req, res) => {
  let p = normalize(decodeURIComponent(new URL(req.url, 'http://x').pathname)).replace(/^(\.\.[/\\])+/, '');
  let file = join(root, p);
  try { if ((await stat(file)).isDirectory()) file = join(file, 'index.html'); const body = await readFile(file); res.writeHead(200, { 'content-type': types[extname(file)] || 'application/octet-stream' }); res.end(body); }
  catch { res.writeHead(404); res.end('not found'); }
});

const checks = [
  // [path, selector that must contain text after load, optional action]
  ['/', 'h1'],
  ['/money-calculators/', '.tiles'],
  ['/money-calculators/debt-payoff/', '#result .big'],
  ['/money-calculators/compound-interest/', '#result .big'],
  ['/money-calculators/emergency-fund/', '#result .big'],
  ['/money-calculators/savings-interest/', '#result .big'],
  ['/money-calculators/credit-card-minimum/', '#result .big'],
  ['/money-calculators/roth-vs-traditional/', '#result .big'],
  ['/money-calculators/es/', '.tiles'],
  ['/money-calculators/es/debt-payoff/', '#result .big'],
  ['/money-calculators/es/compound-interest/', '#result .big'],
  ['/money-calculators/es/credit-card-minimum/', '#result .big'],
  ['/scam-checker/', '#result', async (page) => {
    await page.fill('#message', 'USPS: Your package is on hold due to an unpaid fee of $1.99. Pay now at https://usps-redelivery.top/pay or it will be returned.');
    await page.click('#check');
  }],
  ['/scam-checker/es/', '#result', async (page) => { await page.click('[data-example=toll]'); }],
  ['/scam-checker/scams/', '.tiles'],
  ['/scam-checker/scams/toll-text-scam/', '#result', async (page) => {
    await page.fill('#guide-msg', 'URGENT: unpaid toll of $4.15, pay at ezpass-help.top now or face a late fee');
    await page.click('#guide-check button');
    await page.waitForURL(/scam-checker\/$/);
  }],
  ['/budget/subscriptions.html', '#results', async (page) => { await page.click('#sample'); }],
  ['/budget/', '#summary', async (page) => {
    await page.fill('#income', '3200');
    await page.fill('#tx-amount', '42.50');
    await page.click('#tx-add');
  }],
];

let playwright;
try { playwright = createRequire(import.meta.url)('playwright'); } catch { console.log('Playwright not installed: skipping browser smoke test.'); process.exit(0); }

const shotsIdx = process.argv.indexOf('--shots');
const shots = shotsIdx > -1 ? process.argv[shotsIdx + 1] : null;
if (shots) await mkdir(shots, { recursive: true });

await new Promise((r) => server.listen(0, r));
const base = `http://127.0.0.1:${server.address().port}`;
const browser = await playwright.chromium.launch();
let failed = 0;
for (const [path, selector, act] of checks) {
  for (const viewport of [{ width: 1280, height: 900 }, { width: 390, height: 844 }]) {
    const page = await browser.newPage({ viewport });
    const errors = [];
    page.on('console', (m) => { if (m.type() === 'error' && !/favicon|plausible/.test(m.text())) errors.push(m.text()); });
    page.on('pageerror', (e) => errors.push(e.message));
    await page.goto(base + path, { waitUntil: 'networkidle' });
    if (act) await act(page);
    const text = (await page.locator(selector).first().textContent({ timeout: 3000 }).catch(() => '')) || '';
    const scroll = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
    const ok = errors.length === 0 && text.trim().length > 0 && !scroll;
    if (!ok) failed++;
    console.log(`${ok ? 'ok  ' : 'FAIL'} ${path} @${viewport.width}px${errors.length ? ' errors: ' + errors.join(' | ') : ''}${text.trim() ? '' : ' (empty ' + selector + ')'}${scroll ? ' (horizontal scroll)' : ''}`);
    if (shots) await page.screenshot({ path: join(shots, `${path.replace(/\W+/g, '_') || 'root'}-${viewport.width}.png`), fullPage: true });
    await page.close();
  }
}
await browser.close();
server.close();
process.exit(failed ? 1 : 0);
