// Makes the Chrome Web Store images in dist/: two 1280x800 screenshots and a 440x280 promo tile.
//   node scam-extension/store-shots.mjs [build/scam-decoded]   (needs Playwright with full Chromium)
// With a brand build folder, images go to dist/<brand>/ in that brand's colours.
import { mkdirSync, readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const here0 = dirname(fileURLToPath(import.meta.url));
const here = process.argv[2] ? join(here0, process.argv[2]) : here0;
const { chromium } = createRequire(import.meta.url)('playwright');
const brandSlug = process.argv[2] ? process.argv[2].split('/').pop() : '';
const out = join(here0, 'dist', brandSlug);
mkdirSync(out, { recursive: true });
const brand = JSON.parse(readFileSync(join(here, 'manifest.json'), 'utf8')).short_name;
const icon = `data:image/svg+xml;base64,${readFileSync(join(here, 'icons', 'icon.svg')).toString('base64')}`;
// Slide background: the brand colour from the build's popup.css (Scam Shield blue by default).
const brandCss = /colours \(brands\/[^)]+\) \*\/\n:root \{ --brand: (#[0-9a-f]{6})/i.exec(readFileSync(join(here, 'popup.css'), 'utf8'));
const bg = brandSlug && brandCss ? `linear-gradient(135deg,#0d1b2a,${brandCss[1]})` : 'linear-gradient(135deg,#0e2a7a,#1f4fd1)';

const ctx = await chromium.launchPersistentContext('', { headless: true, channel: 'chromium', args: [`--disable-extensions-except=${here}`, `--load-extension=${here}`] });
const sw = ctx.serviceWorkers()[0] || await ctx.waitForEvent('serviceworker', { timeout: 10000 });
const popup = `chrome-extension://${new URL(sw.url()).host}/popup.html?window=1`;

const shots = [
  ['screenshot-1-text.png', 'Paste any text. Get a straight answer.', 'Toll, delivery, bank, job and crypto scams, checked on your device.', 'E-ZPass: You have an unpaid toll of $6.85. Pay within 24 hours to avoid a $50 late fee: https://ezpass-tollservice.top/pay'],
  ['screenshot-2-link.png', 'Right-click any link to check it first.', 'Spots look-alike addresses like amaz0n-secure.help before you click.', 'https://amaz0n-secure.help/login'],
];
for (const [file, title, sub, msg] of shots) {
  // Render the real popup first, then place that picture on the slide (extension pages can't be iframed).
  const p = await ctx.newPage();
  await p.setViewportSize({ width: 420, height: 700 });
  await p.goto(`${popup}#m=${encodeURIComponent(msg)}`);
  await p.waitForSelector('#result .score');
  const shot = `data:image/png;base64,${(await p.screenshot({ scale: 'device' })).toString('base64')}`;
  await p.close();
  const page = await ctx.newPage();
  await page.setViewportSize({ width: 1280, height: 800 });
  await page.setContent(`<style>body{margin:0;height:800px;display:flex;align-items:center;gap:56px;padding:0 80px;box-sizing:border-box;background:${bg};font-family:system-ui,sans-serif;color:#fff}
    .copy{flex:1}h1{font-size:52px;line-height:1.1;margin:0 0 20px}p{font-size:24px;opacity:.9;margin:0}.brand{display:flex;gap:12px;align-items:center;font-weight:700;font-size:24px;margin-bottom:28px}
    img.shot{width:420px;height:700px;border-radius:14px;background:#fff;box-shadow:0 20px 60px rgba(0,0,0,.35)}</style>
    <div class="copy"><div class="brand"><img src="${icon}" width="40" height="40">${brand}</div><h1>${title}</h1><p>${sub}</p></div>
    <img class="shot" src="${shot}">`);
  await page.screenshot({ path: join(out, file) });
  await page.close();
}
const tile = await ctx.newPage();
await tile.setViewportSize({ width: 440, height: 280 });
await tile.setContent(`<style>body{margin:0;height:280px;display:flex;flex-direction:column;justify-content:center;padding:0 36px;box-sizing:border-box;background:${bg};color:#fff;font-family:system-ui,sans-serif}
  h1{font-size:34px;margin:14px 0 6px}p{margin:0;font-size:17px;opacity:.9}</style><img src="${icon}" width="64" height="64"><h1>Is this a scam?</h1><p>${brand} checks texts and links in one click.</p>`);
await tile.screenshot({ path: join(out, 'promo-440x280.png') });
await ctx.close();
console.log(`Store images written to scam-extension/dist/${brandSlug}`);
