// Renders the X header (1500x500) into images/. The profile picture is the same logo as LinkedIn
// (../linkedin/images/page-logo.png). Needs Playwright.
//   node launch/1099-money/threads-x/render_header.mjs
import { mkdirSync } from 'node:fs';
import { createRequire } from 'node:module';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const out = join(dirname(fileURLToPath(import.meta.url)), 'images');
// X puts the round profile photo over the bottom-left of the header, so the text sits right of centre.
const html = `<!doctype html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box;margin:0}body{width:1500px;height:500px;background:#f7f3ea;color:#14213d;
font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;display:flex;align-items:center;justify-content:flex-end;
padding:0 90px;border-bottom:14px solid #3cc6a0;overflow:hidden}
.t{text-align:right;max-width:930px}h1{font-size:64px;font-weight:800;line-height:1.08}h1 b{color:#ff7a45}
p{font-size:30px;color:#56607a;margin-top:20px}</style></head><body>
<div class="t"><h1>Freelance money, <b>in plain numbers</b></h1>
<p>Rates, invoices, contracts and the IRS. Free calculators at 1099money.netlify.app</p></div></body></html>`;

const { chromium } = createRequire(import.meta.url)('playwright');
mkdirSync(out, { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1500, height: 500 }, deviceScaleFactor: 1 });
await page.setContent(html);
if (await page.evaluate(() => document.body.scrollWidth > 1500 || document.body.scrollHeight > 500)) throw new Error('header overflows');
await page.screenshot({ path: join(out, 'x-header.png') });
await browser.close();
console.log('rendered images/x-header.png');
