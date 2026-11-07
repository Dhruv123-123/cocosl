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
  ['/money-calculators/debt-payoff/', '#print-plan h1', async (page) => {
    await page.evaluate(() => { window.print = () => {}; });
    await page.click('[data-print=avalanche]');
  }],
  ['/money-calculators/compound-interest/', '#result .big'],
  ['/money-calculators/401k-fees/', '#result table.fees'],
  ['/money-calculators/es/401k-fees/', '#result table.fees'],
  ['/medical-bills/debt.html', '#about', async (page) => { await page.fill('[name=name]', 'Sam'); await page.fill('[name=collector]', 'Apex'); await page.fill('[name=reference]', 'AR-1'); }],
  ['/scam-checker/family/', '#steps .task', async (page) => { await page.check('#steps input[type=checkbox]'); }],
  ['/medical-bills/', '#plan b', async (page) => { await page.fill('[name=patient]', 'Jordan Lee'); await page.fill('[name=provider]', 'Riverside General'); await page.fill('[name=account]', 'RG-1'); await page.check('[name=haveItemized]'); await page.check('#extra-form [name=errors][value=duplicate]'); }],
  ['/money-calculators/emergency-fund/', '#result .big'],
  ['/money-calculators/savings-interest/', '#result .big'],
  ['/money-calculators/credit-card-minimum/', '#result .big'],
  ['/money-calculators/roth-vs-traditional/', '#result .big'],
  ['/money-calculators/take-home-pay/', '#result .big'],
  ['/money-calculators/es/take-home-pay/', '#result .big'],
  ['/money-calculators/es/', '.tiles'],
  ['/money-calculators/compound-interest/?embed=1', '.embed-credit'],
  ['/money-calculators/embed/', '#embed-form', async (page) => { await page.waitForSelector('#e-preview iframe'); }],
  ['/money-calculators/es/debt-payoff/', '#result .big'],
  ['/money-calculators/es/compound-interest/', '#result .big'],
  ['/money-calculators/es/credit-card-minimum/', '#result .big'],
  ['/scam-checker/', '#result', async (page) => {
    await page.fill('#message', 'USPS: Your package is on hold due to an unpaid fee of $1.99. Pay now at https://usps-redelivery.top/pay or it will be returned.');
    await page.click('#check');
  }],
  ['/scam-checker/es/', '#result', async (page) => { await page.click('[data-example=toll]'); }],
  ['/scam-checker/link/', '#result .score', async (page) => { await page.click('[data-url*=paypa1]'); }],
  ['/scam-checker/es/enlace/', '#result .score', async (page) => { await page.click('[data-url*=usps]'); }],
  ['/scam-checker/scams/', '.tiles'],
  ['/scam-checker/es/estafas/', '.tiles'],
  ['/scam-checker/es/estafas/mensaje-peaje-sin-pagar/', '#result', async (page) => {
    await page.fill('#guide-msg', 'URGENTE: tiene un saldo de peaje pendiente de $4.15, pague ahora en ezpass-pagos.top o tendrá un cargo por mora');
    await page.click('#guide-check button');
    await page.waitForURL(/scam-checker\/es\/$/);
  }],
  ['/scam-checker/scams/toll-text-scam/', '#result', async (page) => {
    await page.fill('#guide-msg', 'URGENT: unpaid toll of $4.15, pay at ezpass-help.top now or face a late fee');
    await page.click('#guide-check button');
    await page.waitForURL(/scam-checker\/$/);
  }],
  ['/ad-script-builder/', '.script td.voice', async (page) => {
    await page.fill('[name=brand]', 'Hollowick');
    await page.fill('[name=product]', 'Cedar & Smoke candle');
    await page.fill('[name=fact1]', 'wooden wick that crackles while it burns all evening long');
    await page.fill('[name=fact2]', 'hand-poured soy wax');
    await page.click('#builder button[type=submit]');
    await page.click('#another');
  }],
  ['/budget/subscriptions.html', '#results', async (page) => { await page.click('#sample'); }],
  ['/budget/bills.html', '#bills .bill', async (page) => { await page.fill('#b-name', 'Internet'); await page.fill('#b-monthly', '80'); await page.click('#bill-form button'); }],
  ['/budget/deals.html', '#result .countdown', async (page) => { await page.fill('[name=balance]', '400'); await page.fill('[name=end]', '2030-01-15'); await page.fill('[name=apr]', '29.99'); await page.fill('[name=payment]', '50'); await page.click('#deal-form button[type=submit]'); }],
  ['/budget/rate.html', '#rate-result .grade', async (page) => { await page.click('#rate-form button'); }],
  ['/freelance-invoices/', '#invoices .inv', async (page) => {
    await page.fill('[name=client]', 'Northwind Studio'); await page.fill('[name=clientEmail]', 'ap@northwind.com'); await page.fill('[name=amount]', '1800');
    await page.fill('[name=issued]', '2026-01-05'); await page.selectOption('#f-fee', 'percent'); await page.click('#inv-form button[type=submit]');
    await page.click('[data-act=remind]'); if (!(await page.inputValue('#rem-body')).includes('Northwind')) throw new Error('no reminder text'); await page.click('#reminder .close button');
  }],
  ['/budget/subscriptions.html', '#results', async (page) => { await page.fill('#paste', ['08', '09', '10'].map((m) => `${m}/03 NETFLIX.COM 15.49\n${m}/09 SPOTIFY USA 11.99`).join('\n')); await page.click('#paste-form button'); }],
  ['/budget/networth.html', '#trend .snaps', async (page) => {
    await page.fill('[name=name]', 'Savings'); await page.fill('[name=value]', '4800'); await page.click('#item-form button');
    await page.selectOption('#f-side', 'debt'); await page.fill('[name=value]', '3200'); await page.click('#item-form button');
    await page.click('#snap');
    const [dl] = await Promise.all([page.waitForEvent('download'), page.click('#pdf')]);
    if (!/\.pdf$/.test(dl.suggestedFilename())) throw new Error('no pdf');
  }],
  ['/money-calculators/emergency-fund/?stability=variable', '#result .timeline'],
  ['/budget/disputes.html', '#disputes .dispute', async (page) => { await page.fill('[name=item]', 'Metro Bank Card'); await page.click('#dispute-form button[type=submit]'); await page.selectOption('[data-outcome] select', 'verified'); await page.click('[data-outcome] button'); }],
  ['/scam-checker/vendor/', '#result .score', async (page) => { await page.click('#example'); }],
  ['/budget/pricing.html?from=goals', '#compare tr', async (page) => { if (!(await page.locator('#from').isVisible())) throw new Error('limit message hidden'); }],
  ['/budget/', '#summary', async (page) => {
    // First run: the welcome steps set income and a 50/30/20 plan.
    await page.fill('#welcome-income', '3200');
    await page.click('#welcome-pay button[type=submit]');
    await page.click('#welcome-next');
    await page.click('#welcome [data-step="3"] button');
    if (await page.locator('#welcome').evaluate((d) => d.open)) throw new Error('welcome did not close');
    if ((await page.inputValue('#income')) !== '3200') throw new Error('onboarding income not saved');
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

// The browser extension, loaded for real. Extensions need full Chromium (channel 'chromium'), not the headless shell.
{
  const extDir = join(root, 'scam-extension');
  let ctx;
  try {
    ctx = await playwright.chromium.launchPersistentContext('', { headless: true, channel: 'chromium', args: [`--disable-extensions-except=${extDir}`, `--load-extension=${extDir}`] });
  } catch (e) { console.log(`skip scam-extension (full Chromium not available: ${e.message.split('\n')[0]})`); }
  if (ctx) {
    const sw = ctx.serviceWorkers()[0] || await ctx.waitForEvent('serviceworker', { timeout: 10000 });
    const id = new URL(sw.url()).host;
    for (const [label, url, width] of [
      ['popup', `chrome-extension://${id}/popup.html`, 380],
      ['right-click window', `chrome-extension://${id}/popup.html?window=1#m=${encodeURIComponent('USPS: package held. Pay $1.99 now: https://usps-redelivery.top/pay')}`, 420],
    ]) {
      const page = await ctx.newPage();
      await page.setViewportSize({ width, height: 640 });
      const errors = [];
      page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
      page.on('pageerror', (e) => errors.push(e.message));
      await page.goto(url);
      if (!url.includes('#m=')) { await page.fill('#message', 'Your Amazon account is locked. Verify now: http://amaz0n-secure.help/login'); await page.click('#b-check'); }
      const score = (await page.locator('#result .score').textContent({ timeout: 3000 }).catch(() => '')) || '';
      const high = /High risk/.test(score);
      const scroll = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
      const ok = errors.length === 0 && high && !scroll;
      if (!ok) failed++;
      console.log(`${ok ? 'ok  ' : 'FAIL'} scam-extension ${label}${errors.length ? ' errors: ' + errors.join(' | ') : ''}${high ? '' : ` (expected High risk, got "${score.trim()}")`}${scroll ? ' (horizontal scroll)' : ''}`);
      if (shots) await page.screenshot({ path: join(shots, `scam-extension-${label.replace(/\W+/g, '_')}.png`), fullPage: true });
      await page.close();
    }
    await ctx.close();
  }
}
process.exit(failed ? 1 : 0);
