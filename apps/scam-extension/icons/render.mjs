// Dev helper: renders icon.svg to the PNG sizes Chrome needs. Run once after changing the SVG.
//   node scam-extension/icons/render.mjs [folder]   (needs Playwright; folder defaults to this one,
//   e.g. scam-extension/brands/scam-decoded/icons for a brand's icons)
import { readFileSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const here = dirname(fileURLToPath(import.meta.url));
const { chromium } = createRequire(import.meta.url)('playwright');
const dir = process.argv[2] ? resolve(process.argv[2]) : here;
const svg = readFileSync(join(dir, 'icon.svg'), 'utf8');
const browser = await chromium.launch();
for (const size of [16, 32, 48, 128]) {
  const page = await browser.newPage({ viewport: { width: size, height: size } });
  await page.setContent(`<style>html,body{margin:0;background:transparent}svg{width:${size}px;height:${size}px;display:block}</style>${svg}`);
  await page.screenshot({ path: join(dir, `icon-${size}.png`), omitBackground: true });
  await page.close();
}
await browser.close();
console.log('Rendered icons');
