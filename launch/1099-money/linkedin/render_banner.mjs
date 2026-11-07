// Renders the LinkedIn images into images/: the 1099 Money page cover (1128x191), a personal-profile
// banner (1584x396) and the page logo (400x400). Needs Playwright.
//   node launch/1099-money/linkedin/render_banner.mjs
import { mkdirSync } from 'node:fs';
import { createRequire } from 'node:module';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const out = join(dirname(fileURLToPath(import.meta.url)), 'images');
const base = `*{box-sizing:border-box;margin:0}body{background:#f7f3ea;color:#14213d;font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;overflow:hidden}
.m{display:inline-grid;place-items:center;border-radius:50%;background:#ff7a45;color:#14213d;font-weight:800}`;
// LinkedIn covers the left part of a page cover with the logo on phones, and the bottom-left of a personal
// banner with the profile photo, so the text sits right of centre.
const images = [
  ['page-cover.png', 1128, 191, `<style>${base}
    body{display:flex;align-items:center;justify-content:flex-end;padding:0 56px;border-bottom:8px solid #3cc6a0}
    .t{text-align:right}h1{font-size:40px;font-weight:800;line-height:1.1}h1 b{color:#ff7a45}
    p{font-size:20px;color:#56607a;margin-top:10px}</style>
    <div class="t"><h1>Price it right. Pay the IRS right. <b>Keep more.</b></h1>
    <p>Free rate, tax and deduction calculators for US freelancers and consultants</p></div>`],
  ['profile-banner.png', 1584, 396, `<style>${base}
    body{display:flex;align-items:center;justify-content:flex-end;padding:0 96px;border-bottom:12px solid #3cc6a0}
    .t{text-align:right;max-width:980px}h1{font-size:60px;font-weight:800;line-height:1.1}h1 b{color:#ff7a45}
    p{font-size:28px;color:#56607a;margin-top:18px}.u{margin-top:22px;font-size:26px;font-weight:700}</style>
    <div class="t"><h1>Rates, clients and taxes for freelancers, <b>in plain numbers</b></h1>
    <p>Pricing, contracts, invoicing and the IRS, worked out step by step</p><p class="u">1099money.netlify.app</p></div>`],
  ['page-logo.png', 400, 400, `<style>${base}body{display:grid;place-items:center;height:400px}
    .m{width:300px;height:300px;font-size:120px;letter-spacing:-4px}</style><span class="m">1M</span>`],
];

const { chromium } = createRequire(import.meta.url)('playwright');
mkdirSync(out, { recursive: true });
const browser = await chromium.launch();
for (const [file, width, height, html] of images) {
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
  await page.setContent(`<!doctype html><html><head><meta charset="utf-8"></head><body style="width:${width}px;height:${height}px">${html}</body></html>`);
  const over = await page.evaluate(() => document.body.scrollWidth > innerWidth || document.body.scrollHeight > innerHeight
    || [...document.querySelectorAll('h1,p')].some((e) => e.getBoundingClientRect().left < 0));
  if (over) throw new Error(`${file} overflows`);
  await page.screenshot({ path: join(out, file) });
  await page.close();
}
await browser.close();
console.log(`rendered ${images.length} images`);
