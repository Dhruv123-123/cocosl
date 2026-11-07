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
  ['/', '#search-results a', async (page) => {
    await page.fill('#q', 'my wife and I');
    await page.waitForSelector('#search-results a');
    if (!/couples/i.test(await page.textContent('#search-results'))) throw new Error('search did not find the couples tool');
    if (await page.locator('#budgeting').isVisible()) throw new Error('sections should hide while searching');
  }],
  ['/es/', '#search-results a', async (page) => {
    await page.fill('#q', 'préstamo');
    await page.waitForSelector('#search-results a');
    if (!/herramienta/.test(await page.textContent('#search-count'))) throw new Error('Spanish count text');
  }],
  ['/freelance-invoices/side-hustle.html', '#result .big-num', async (page) => {
    await page.selectOption('#kind', 'etsy');
    if (!(await page.locator('[name=listings]').isVisible())) throw new Error('Etsy listing fields hidden');
    await page.selectOption('#kind', 'driver');
    if (await page.locator('[name=orders]').isVisible()) throw new Error('seller fields shown for a driver');
    if (!/an hour, after costs and taxes/.test(await page.textContent('#result'))) throw new Error('result');
  }],
  ['/budget/first-paycheck.html', '#match-out .callout', async (page) => {
    await page.fill('#salary', '55000');
    await page.selectOption('#w4 [name=jobs]', 'two');
    if (!/Withholding Estimator/.test(await page.textContent('#w4-out'))) throw new Error('W-4 two-job advice');
    if (!/\$1,650\.00/.test(await page.textContent('#match-out'))) throw new Error('match math');
    await page.fill('#takehome', '3500');
    if (!/\$1,750\.00/.test(await page.textContent('#budget-out'))) throw new Error('50/30/20');
    await page.check('[data-done=w4]');
    if (!/1 of 5 steps done/.test(await page.textContent('#progress'))) throw new Error('progress');
  }],
  ['/freelance-invoices/set-aside/', '#widget .w-date', async (page) => {
    await page.fill('#amount', '2000');
    await page.fill('#paid [name=date]', '2026-10-02');
    await page.click('#paid button[type=submit]');
    if (!/Move \$420\.00/.test(await page.textContent('#move'))) throw new Error('set-aside at 21%');
    await page.selectOption('#year', '2026');
    await page.fill('[data-sent="2026-Q4"]', '100');
    await page.dispatchEvent('[data-sent="2026-Q4"]', 'change');
    await page.waitForTimeout(50);
    if (!/\$420/.test(await page.textContent('#quarters'))) throw new Error('quarter total');
  }],
  ['/scam-checker/', '#check', async (page) => {
    await page.fill('#message', 'USPS: your package is on hold due to an unpaid fee. Pay within 24 hours at https://usps-redelivery-help.top/pay');
    await page.click('#check');
    await page.waitForSelector('#result .guide-link a');
    if (!/scams\/usps-text-scam\//.test(await page.getAttribute('#result .guide-link a', 'href'))) throw new Error('guide link');
  }],
  ['/budget/money-personality.html', '#result h2', async (page) => {
    for (const q of await page.locator('.q-options').all()) await q.locator('input').nth(3).check();
    if (!/The Worrier/.test(await page.textContent('#result'))) throw new Error('worrier result');
    if ((await page.locator('#result a[href*="emergency-fund"]').count()) < 1) throw new Error('tool link');
  }],
  ['/budget/savings-challenge.html', '#progress .score-big', async (page) => {
    await page.fill('[name=start]', '2026-01-05');
    if (!/\$52\.00/.test(await page.textContent('#weeks'))) throw new Error('classic amounts');
    await page.check('[data-week="1"]');
    if (!/1\/52/.test(await page.textContent('#progress'))) throw new Error('tick');
    await page.selectOption('[name=plan]', 'even');
    await page.fill('[name=goal]', '5200');
    if (!/\$100\.00/.test(await page.textContent('#weeks'))) throw new Error('even goal');
  }],
  ['/budget/bill-calendar/', '#list .due', async (page) => {
    const d = new Date(); const iso = (x) => `${x.getFullYear()}-${String(x.getMonth() + 1).padStart(2, '0')}-${String(x.getDate()).padStart(2, '0')}`;
    const soon = new Date(d.getFullYear(), d.getMonth(), Math.min(d.getDate() + 2, 28));
    await page.fill('[name=name]', 'Phone'); await page.fill('[name=amount]', '85'); await page.fill('[name=start]', iso(soon));
    await page.click('#save');
    await page.fill('[name=name]', 'Rent'); await page.fill('[name=amount]', '1450'); await page.fill('[name=start]', iso(new Date(d.getFullYear(), d.getMonth() + 1, 1)));
    await page.click('#save');
    if (!/Phone/.test(await page.textContent('#bills')) || !/Rent/.test(await page.textContent('#bills'))) throw new Error('bills list');
    if ((await page.locator('#grid .cell.has').count()) < 1) throw new Error('grid shows no bill');
    await page.locator('#list input[type=checkbox]').first().check();
    if (!/\$85/.test(await page.textContent('#stats'))) throw new Error(`paid total: ${await page.textContent('#stats')}`);
    await page.click('#next');
    if (!/Rent/.test(await page.textContent('#list'))) throw new Error('next month');
    const [dl] = await Promise.all([page.waitForEvent('download'), page.click('#ics')]);
    const ics = await (await import('node:fs/promises')).readFile(await dl.path(), 'utf8');
    if (!/RRULE:FREQ=MONTHLY/.test(ics) || !/SUMMARY:Pay Rent due/.test(ics) && !/SUMMARY:Pay Rent/.test(ics)) throw new Error('ics');
    await page.reload();
    if (!/Phone/.test(await page.textContent('#bills'))) throw new Error('not saved');
  }],
  ['/budget/bill-calendar/es.html', '#bills li', async (page) => {
    if (!/Dom/.test(await page.textContent('#weekdays'))) throw new Error('es weekdays');
    if (!/Cada mes/.test(await page.textContent('[name=freq]'))) throw new Error('es freqs');
  }],
  ['/budget/money-dashboard.html', '#summary table', async (page) => {
    await page.click('#sample');
    await page.waitForSelector('#summary table');
    const sum = await page.textContent('#summary');
    if (!/Groceries/.test(sum) || !/Left over/.test(sum)) throw new Error(`summary rows: ${sum}`);
    if (!/\$5,300/.test(await page.textContent('#stats'))) throw new Error('average money in');
    const pick = page.locator('#sort select').first();
    if (!(await pick.count())) throw new Error('no merchants to sort');
    await pick.selectOption('fun');
    if (!/Fun & going out/.test(await page.textContent('#summary'))) throw new Error('sorting did not update the summary');
    await page.fill('[data-budget=groceries]', '350'); await page.dispatchEvent('[data-budget=groceries]', 'change');
    const [dl] = await Promise.all([page.waitForEvent('download'), page.click('#download')]);
    if (!/^money-dashboard-\d{4}-\d{2}-to-\d{4}-\d{2}\.xlsx$/.test(dl.suggestedFilename())) throw new Error(`file name ${dl.suggestedFilename()}`);
    const buf = await (await import('node:fs/promises')).readFile(await dl.path());
    if (buf.readUInt32LE(0) !== 0x04034b50 || buf.length < 4000) throw new Error('not an xlsx zip');
    await page.evaluate(() => localStorage.clear());
  }],
  ['/budget/tablero-dinero.html', '#summary table', async (page) => {
    await page.click('#sample');
    await page.waitForSelector('#summary table');
    if (!/Supermercado/.test(await page.textContent('#summary'))) throw new Error('es categories');
    const [dl] = await Promise.all([page.waitForEvent('download'), page.click('#download')]);
    if (!/^tablero-de-dinero-.*-a-.*\.xlsx$/.test(dl.suggestedFilename())) throw new Error(`es file name ${dl.suggestedFilename()}`);
  }],
  ['/budget/reto-ahorro.html', '#progress .score-big', async (page) => {
    if (!/Semana 1/.test(await page.textContent('#weeks'))) throw new Error('es weeks');
  }],
  ['/budget/checkup.html', '#report .score-big', async (page) => {
    for (const r of await page.locator('.q-options').all()) await r.locator('input').nth(2).check();
    if (!/Grade F/.test(await page.textContent('#report'))) throw new Error('worst case grade');
    if (!/Fix these first/.test(await page.textContent('#report'))) throw new Error('fix list');
    for (const r of await page.locator('.q-options').all()) await r.locator('input').first().check();
    if (!/Grade A/.test(await page.textContent('#report'))) throw new Error('best case grade');
  }],
  ['/budget/couples.html', '#split h3', async (page) => {
    await page.fill('[name=name0]', 'Alex'); await page.fill('[name=income0]', '6000');
    await page.fill('[name=name1]', 'Sam'); await page.fill('[name=income1]', '4000');
    await page.fill('#expense-form [name=name]', 'Rent'); await page.fill('#expense-form [name=amount]', '2000'); await page.click('#expense-form button[type=submit]');
    await page.fill('#expense-form [name=name]', 'Groceries'); await page.fill('#expense-form [name=amount]', '600');
    await page.selectOption('#e-paid', 'a'); await page.click('#expense-form button[type=submit]');
    const split = await page.textContent('#split');
    if (!/Alex: \$1,200\.00/.test(split) || !/Sam sends Alex \$240\.00/.test(split)) throw new Error(`split wrong: ${split}`);
    await page.check('[data-check=win]');
    if (!/1 of 8 done/.test(await page.textContent('#streak'))) throw new Error('checklist');
    await page.reload();
    if ((await page.locator('#expenses li').count()) !== 2) throw new Error('not saved');
  }],
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
  ['/money-calculators/take-home-pay/', '#result .big', async (page) => {
    await page.selectOption('[name=state]', 'CA');
    if (await page.locator('[name=stateRate]').isVisible()) throw new Error('custom rate box should hide once a state is picked');
    if (!/California income tax/.test(await page.textContent('#result'))) throw new Error('state row missing');
    await page.selectOption('[name=state]', 'TX');
    if (!/doesn't tax wages/.test(await page.textContent('#result'))) throw new Error('no-tax state line missing');
  }],
  ['/money-calculators/es/', '.tiles'],
  ['/money-calculators/student-loans/', '#result .plans-table', async (page) => {
    await page.selectOption('[name=cohort]', 'after2026');
    if (!/Tiered Standard/.test(await page.textContent('#result'))) throw new Error('tiered plan missing');
    if (!/Verify with your loan servicer/.test(await page.textContent('#result'))) throw new Error('servicer note missing');
  }],
  ['/money-calculators/es/student-loans/', '#result .plans-table'],
  ['/money-calculators/rent-vs-buy/', '#result .big', async (page) => {
    await page.fill('[name=years]', '25');
    if (!/Buying comes out ahead/.test(await page.textContent('#result'))) throw new Error('rent vs buy result');
  }],
  ['/money-calculators/es/rent-vs-buy/', '#result .big'],
  ['/money-calculators/compound-interest/?embed=1', '.embed-credit'],
  ['/money-calculators/embed/', '#embed-form', async (page) => {
    await page.waitForSelector('#e-preview iframe');
    if (!/Most popular/.test(await page.innerHTML('#e-calc'))) throw new Error('top 3 group');
    await page.selectOption('#e-calc', 'take-home-pay');
    await page.fill('#e-licence', 'demo');
    await page.dispatchEvent('#e-licence', 'change');
    if (!/data-licence="demo"/.test(await page.inputValue('#e-code'))) throw new Error('licence in code');
    const frame = page.frameLocator('#e-preview iframe').last();
    await frame.locator('.partner-cta .btn').waitFor();
    if (await frame.locator('.embed-credit a').count()) throw new Error('licensed embed should drop the credit link');
  }],
  ['/money-calculators/debt-payoff/?embed=1&accent=1f3a8a&theme=dark&radius=4', '#result .big', async (page) => {
    const v = await page.evaluate(() => [getComputedStyle(document.documentElement).getPropertyValue('--gold').trim(), getComputedStyle(document.querySelector('[data-print=avalanche]')).color]);
    if (v[0] !== '#1f3a8a' || v[1] !== 'rgb(255, 255, 255)') throw new Error(`accent ${v}`);
    if (!(await page.locator('.embed-credit a').count())) throw new Error('free embed keeps the credit');
  }],
  ['/money-calculators/es/debt-payoff/', '#result .chart-axis'],
  ['/money-calculators/debt-payoff/', '#result .chart-axis', async (page) => {
    if ((await page.locator('#result svg.chart path').count()) !== 2) throw new Error('two strategy lines');
    if (!/Total debt falls from/.test(await page.getAttribute('#result svg.chart', 'aria-label'))) throw new Error('debt chart label');
  }],
  ['/money-calculators/tax-refund/', '#result .big', async (page) => {
    if (!/Estimated refund: \$780\.00/.test(await page.textContent('#result .big'))) throw new Error('default refund');
    await page.selectOption('[name=filing]', 'hoh');
    await page.fill('[name=wages]', '30000');
    await page.fill('[name=withheld]', '800');
    await page.fill('[name=kids]', '2');
    const t = await page.textContent('#result');
    if (!/\$4,200\.00/.test(t) || !/EITC Assistant/.test(t) || !/Rev\. Proc\. 2025-32/.test(t)) throw new Error('hoh refund, EITC note or sources');
  }],
  ['/money-calculators/es/tax-refund/', '#result .big', async (page) => {
    if (!/Reembolso estimado/.test(await page.textContent('#result .big'))) throw new Error('es refund');
  }],
  ['/budget/paycheck-plan.html', '#budgets label', async (page) => {
    await page.fill('[name=pay]', '1600'); await page.selectOption('[name=freq]', 'biweekly');
    if (!/\$3,200/.test(await page.textContent('#income'))) throw new Error('monthly');
    await page.click('#use-split');
    if (!/Every dollar has a job/.test(await page.textContent('#left'))) throw new Error(`zero-based: ${await page.textContent('#left')}`);
    await page.fill('[data-cat=dining]', '500');
    if (!/more than you earn/.test(await page.textContent('#left'))) throw new Error('over');
    const [dl] = await Promise.all([page.waitForEvent('download'), page.click('#csv')]);
    const csv = await (await import('node:fs/promises')).readFile(await dl.path(), 'utf8');
    if (!/^Category,Monthly budget/.test(csv) || !/Eating out & delivery,500/.test(csv)) throw new Error('csv');
    await page.click('#to-dashboard');
    await page.waitForURL(/money-dashboard\.html/);
    if ((await page.inputValue('[data-budget=dining]')) !== '500') throw new Error('plan did not reach the dashboard budgets');
  }],
  ['/budget/sinking-funds.html', '#funds .fund', async (page) => {
    await page.click('#ideas [data-i="0"]');
    await page.fill('[name=saved]', '150');
    await page.click('#fund-form button[type=submit]');
    await page.fill('[name=name]', 'Trip'); await page.fill('[name=target]', '1200');
    const d = new Date(); await page.fill('[name=due]', `${d.getFullYear() + 1}-${String(d.getMonth() + 1).padStart(2, '0')}-28`);
    await page.click('#fund-form button[type=submit]');
    if ((await page.locator('#funds .fund').count()) !== 2) throw new Error('two funds');
    if (!/Car insurance\t900\t/.test(await page.inputValue('#t-funds'))) throw new Error('tsv');
    if (!/\tCar insurance\t150/.test(await page.inputValue('#t-deposits'))) throw new Error('deposits');
    await page.reload();
    if ((await page.locator('#funds .fund').count()) !== 2) throw new Error('not saved');
  }],
  ['/budget/fondos-ahorro.html', '#ideas .chip'],
  ['/app/', '#tools .tile', async (page) => {
    if ((await page.locator('#tools .tile').count()) !== 10) throw new Error('ten tools');
    await page.waitForSelector('#status.ready', { timeout: 30000 });
    await page.evaluate(() => navigator.serviceWorker.ready);
    await page.waitForFunction(() => !!navigator.serviceWorker.controller, null, { timeout: 10000 });
    await page.context().setOffline(true);
    try {
      for (const [u, sel] of [['/budget/split-bills.html', '#h-people'], ['/money-calculators/take-home-pay/', 'h1'], ['/scam-checker/', 'h1'], ['/app/?source=pwa', '#tools .tile']]) {
        await page.goto(`${new URL(page.url()).origin}${u}`);
        if (!(await page.locator(sel).first().textContent())?.trim()) throw new Error(`offline: ${u}`);
      }
    } finally { await page.context().setOffline(false); }
    await page.click('#lang');
    if (!/Dividir gastos/.test(await page.textContent('#tools'))) throw new Error('spanish');
    await page.click('#lang');
  }],
  ['/scam-checker/app/', '#tiles .tile', async (page) => {
    await page.waitForSelector('#status.ready', { timeout: 30000 });
    await page.waitForFunction(() => !!navigator.serviceWorker.controller, null, { timeout: 15000 });
    await page.context().setOffline(true);
    try {
      for (const [u, sel] of [['/scam-checker/app/report.html', '#places li'], ['/scam-checker/', 'h1'], ['/scam-checker/link/', 'h1'], ['/scam-checker/app/?source=pwa', '#tiles .tile']]) {
        await page.goto(`${new URL(page.url()).origin}${u}`);
        if (!(await page.locator(sel).first().textContent())?.trim()) throw new Error(`offline: ${u}`);
      }
    } finally { await page.context().setOffline(false); }
  }],
  ['/scam-checker/app/checklist.html', '#verdict h2', async (page) => {
    await page.check('input[name=urgent][value=yes]');
    if (!/Some red flags/.test(await page.textContent('#verdict'))) throw new Error('medium');
    await page.check('input[name=pay][value=yes]');
    if (!/Very likely a scam/.test(await page.textContent('#verdict'))) throw new Error('high');
    if (!(await page.locator('#why-pay').isVisible())) throw new Error('why');
    await page.reload();
    if (!(await page.isChecked('input[name=pay][value=yes]'))) throw new Error('not saved');
  }],
  ['/scam-checker/app/quiz.html', '#score h2', async (page) => {
    for (let i = 0; i < 10; i++) await page.click(`button[data-i="${i}"][data-a="1"]`);
    if (!/You got \d+ of 10/.test(await page.textContent('#score'))) throw new Error('score');
  }],
  ['/scam-checker/app/report.html', '#advice .first', async (page) => {
    await page.click('#situations [data-s=text]');
    if (!/7726/.test(await page.textContent('#advice'))) throw new Error('spam text');
    await page.selectOption('#state', 'TX');
    if (!(await page.getAttribute('#ag a', 'href')).includes('texasattorneygeneral.gov')) throw new Error('AG');
  }],
  ['/budget/wedding-budget.html', '#cats .wcat', async (page) => {
    await page.fill('[name=total]', '30000'); await page.fill('[name=guests]', '100');
    await page.click('#split');
    if ((await page.inputValue('[data-k=venue][data-f=budget]')) !== '4800') throw new Error('split');
    await page.fill('[data-k=venue][data-f=estimate]', '6300');
    await page.fill('[data-k=venue][data-f=paid]', '2000');
    if (!/Over plan: Venue/.test(await page.textContent('#notes'))) throw new Error('over warning');
    if (!/\$315\.00/.test(await page.textContent('#stats'))) throw new Error('per guest');
    if (!/^Venue\t4800\t6300\t2000\n/.test(await page.inputValue('#t-rows'))) throw new Error('tsv');
    await page.reload();
    if ((await page.inputValue('[data-k=venue][data-f=paid]')) !== '2000') throw new Error('not saved');
  }],
  ['/budget/presupuesto-boda.html', '#cats .wcat'],
  ['/budget/split-bills.html', '#moves li', async (page) => {
    await page.click('#add-person');
    for (const [i, n, inc] of [[0, 'Ana', '6000'], [1, 'Ben', '3000'], [2, 'Cy', '3000']]) { await page.fill(`[data-i="${i}"][data-f=name]`, n); await page.fill(`[data-i="${i}"][data-f=income]`, inc); }
    await page.fill('#bill-form [name=name]', 'Rent'); await page.fill('#bill-form [name=amount]', '2400');
    await page.click('#bill-form button[type=submit]');
    await page.fill('#bill-form [name=name]', 'Internet'); await page.fill('#bill-form [name=amount]', '90');
    await page.selectOption('#b-paid', '1'); await page.selectOption('#b-split', 'equal');
    await page.click('#bill-form button[type=submit]');
    const moves = await page.textContent('#moves');
    if (!/Cy pays Ana \$630\.00/.test(moves) || !/Ben pays Ana \$540\.00/.test(moves)) throw new Error(`moves: ${moves}`);
    const dl = page.waitForEvent('download'); await page.click('#csv');
    const csv = await (await import('node:fs/promises')).readFile(await (await dl).path(), 'utf8');
    if (!/^Bill,Amount,Paid by,Split,Ana,Ben,Cy/.test(csv)) throw new Error('csv');
    await page.reload();
    if ((await page.locator('#bills li').count()) !== 2) throw new Error('not saved');
  }],
  ['/budget/dividir-gastos.html', '#h-people'],
  ['/budget/money-calendar.html?brand=1099', '#preview li', async (page) => {
    if (!/1099 Money/.test(await page.textContent('#brand'))) throw new Error('brand');
    if (!/estimated tax/i.test(await page.textContent('#preview'))) throw new Error('freelancer dates');
    const [dl] = await Promise.all([page.waitForEvent('download'), page.click('#download')]);
    const ics = await (await import('node:fs/promises')).readFile(await dl.path(), 'utf8');
    if (!/BEGIN:VCALENDAR/.test(ics) || !/X-WR-CALNAME:1099 Money money calendar/.test(ics)) throw new Error('ics');
  }],
  ['/budget/calendario-dinero.html', '#preview li', async (page) => {
    if (!/Dinero Simple/.test(await page.textContent('#brand'))) throw new Error('es brand');
  }],
  ['/budget/plan-quincena.html', '#split li', async (page) => {
    if (!/Necesidades/.test(await page.textContent('#split'))) throw new Error('es split');
  }],
  ['/freelance-invoices/rate.html', '#result .big-num', async (page) => {
    if (!/\$110/.test(await page.textContent('#result .big-num'))) throw new Error(`default rate ${await page.textContent('#result .big-num')}`);
    await page.fill('[name=current]', '50');
    if (!/short/.test(await page.textContent('#result'))) throw new Error('current rate');
  }],
  ['/embed.html', '#h-plans', async (page) => {
    await page.selectOption('#tool', 'scam-checker');
    await page.selectOption('#lang', 'es');
    if (!/data-tool="scam-checker\/es\/"/.test(await page.inputValue('#code'))) throw new Error('snippet');
    await page.locator('#preview').scrollIntoViewIfNeeded();
    const frame = page.frameLocator('#preview iframe');
    await frame.locator('.mms-credit').waitFor();
    if (await frame.locator('header.top').isVisible()) throw new Error('header shown in embed');
    if (!/Scam Shield/.test(await frame.locator('.mms-credit').textContent())) throw new Error('credit');
    await page.selectOption('#tool', 'calc:debt-payoff');
    if (!/mms-calc/.test(await page.inputValue('#code'))) throw new Error('calc snippet');
  }],
  ['/apps.html', '#apps .app', async (page) => {
    if ((await page.locator('#apps .app').count()) !== 6) throw new Error('six apps');
    for (const src of await page.locator('#apps img').evaluateAll((els) => els.map((e) => e.complete && e.naturalWidth))) if (!src) throw new Error('icon did not load');
    const m = await (await page.request.get(new URL('manifest.webmanifest', page.url()).href)).json();
    if (!m.icons?.length) throw new Error('hub manifest');
  }],
  ['/es/apps.html', '#apps .app', async (page) => {
    if (!/Calendario de pagos/.test(await page.textContent('#apps'))) throw new Error('es bill calendar');
    if (!/En inglés/.test(await page.textContent('#apps'))) throw new Error('english-only tag');
  }],
  ['/money-calculators/remittance-cost/', '#result .big', async (page) => {
    await page.fill('[name=amount]', '300'); await page.fill('[name=fee]', '5'); await page.fill('[name=midRate]', '18.5');
    await page.fill('[name=quotedRate]', '0'); await page.fill('[name=markupPct]', '2'); await page.fill('[name=perYear]', '12');
    await page.waitForFunction(() => /5,439\.00 arrive/.test(document.querySelector('#result .big')?.textContent || ''));
    if (!/\$132 a year/.test(await page.textContent('#result'))) throw new Error('year cost');
    await page.selectOption('[name=pay]', 'cash');
    await page.waitForFunction(() => /1% federal tax/.test(document.querySelector('#result').textContent));
  }],
  ['/money-calculators/es/remittance-cost/', '#result .big', async (page) => {
    if (!/Llegan/.test(await page.textContent('#result .big'))) throw new Error('es remit');
  }],
  ['/money-calculators/es/compound-interest/', '#result .big'],
  ['/money-calculators/es/credit-card-minimum/', '#result .big'],
  ['/scam-checker/', '#result', async (page) => {
    const outside = []; const local = (u) => /^(https?:\/\/(127\.0\.0\.1|localhost)[:/]|data:|blob:)/.test(u);
    page.on('request', (r) => { if (!local(r.url())) outside.push(r.url()); });
    await page.fill('#message', 'USPS: Your package is on hold due to an unpaid fee of $1.99. Pay now at https://usps-redelivery.top/pay or it will be returned.');
    await page.click('#check');
    await page.waitForTimeout(300);
    if (outside.length) throw new Error(`checking a message called out: ${outside.join(', ')}`);
  }],
  ['/scam-checker/es/', '#result', async (page) => { await page.click('[data-example=toll]'); }],
  ['/scam-checker/link/', '#result .score', async (page) => {
    const outside = []; page.on('request', (r) => { if (!/^(https?:\/\/(127\.0\.0\.1|localhost)[:/]|data:|blob:)/.test(r.url())) outside.push(r.url()); });
    await page.click('[data-url*=paypa1]');
    await page.waitForTimeout(300);
    if (outside.length) throw new Error(`checking a link called out: ${outside.join(', ')}`);
  }],
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
  ['/budget/holiday.html', '#bnpl table', async (page) => {
    await page.fill('#cap', '800');
    await page.fill('#person-form [name=name]', 'Sam'); await page.fill('#person-form [name=budget]', '200'); await page.click('#person-form button');
    await page.fill('#gift-form [name=item]', 'Headphones'); await page.fill('#gift-form [name=price]', '249.99'); await page.selectOption('#g-pay', 'bnpl'); await page.click('#gift-form button[type=submit]');
  }],
  ['/budget/afford.html', '#compare table', async (page) => {
    await page.fill('[name=savings]', '8000'); await page.fill('[name=keepSaved]', '3000');
    await page.fill('[name=takeHome]', '4500'); await page.fill('[name=bills]', '3000');
    if (!/Not yet/.test(await page.textContent('#verdict'))) throw new Error('car verdict');
    await page.selectOption('#kind', 'phone');
    if (!/Yes, if you pay cash/.test(await page.textContent('#verdict'))) throw new Error('phone verdict');
    if (await page.locator('[name=tradeIn]').isVisible()) throw new Error('trade-in shown for a phone');
  }],
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
for (const [path, selector, act] of checks.filter(([p]) => !process.env.SMOKE_ONLY || process.env.SMOKE_ONLY.split(",").some((x) => p.includes(x)))) {
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
