// Renders the 15 square post cards (1080x1080) from posts.json into cards/. Needs Playwright (Chromium).
//   node launch/1099-money/q4/render_cards.mjs
import { readFileSync, mkdirSync } from 'node:fs';
import { createRequire } from 'node:module';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const posts = JSON.parse(readFileSync(join(here, 'posts.json'), 'utf8'));
const esc = (s) => s.replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
const card = (p) => `<!doctype html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box;margin:0}body{width:1080px;height:1080px;background:#f7f3ea;color:#14213d;font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;padding:96px;display:flex;flex-direction:column;justify-content:space-between}
.k{font-size:30px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#56607a}
h1{font-size:92px;line-height:1.05;font-weight:800;margin-top:40px}
.l2{font-size:76px;font-weight:800;color:#ff7a45;margin-top:28px;line-height:1.1}
.l3{font-size:46px;font-weight:600;color:#14213d;margin-top:36px;line-height:1.25;border-left:10px solid #3cc6a0;padding-left:28px}
.f{display:flex;justify-content:space-between;align-items:center;font-size:30px;color:#56607a}
.m{display:inline-grid;place-items:center;width:64px;height:64px;border-radius:50%;background:#ff7a45;color:#14213d;font-weight:800;font-size:24px;margin-right:16px}
.b{display:flex;align-items:center;font-weight:700;color:#14213d}
</style></head><body>
<div><p class="k">${p.n} of 15 · ${esc(p.topic === '1099' ? '1099 season' : p.topic === 'jan15' ? 'Jan 15 payment' : p.topic === 'retirement' ? 'Retirement' : 'Year-end')}</p>
<h1>${esc(p.card[0])}</h1><p class="l2">${esc(p.card[1])}</p><p class="l3">${esc(p.card[2])}</p></div>
<div class="f"><span class="b"><span class="m">1M</span>1099 Money</span><span>2026 federal figures · not tax advice</span></div>
</body></html>`;

const { chromium } = createRequire(import.meta.url)('playwright');
mkdirSync(join(here, 'cards'), { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1080 }, deviceScaleFactor: 1 });
for (const p of posts) {
  await page.setContent(card(p));
  const over = await page.evaluate(() => document.body.scrollHeight > 1080 || document.body.scrollWidth > 1080);
  if (over) throw new Error(`card ${p.n} overflows`);
  await page.screenshot({ path: join(here, p.card_file) });
}
await browser.close();
console.log(`rendered ${posts.length} cards`);
