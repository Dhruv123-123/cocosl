// node render.mjs page.html --png out.png --size 1280x720   |   node render.mjs page.html --pdf out.pdf
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const [file, ...rest] = process.argv.slice(2);
const opt = (k) => { const i = rest.indexOf(k); return i >= 0 ? rest[i + 1] : null; };
const browser = await chromium.launch();
const size = (opt('--size') || '1280x720').split('x').map(Number);
const page = await browser.newPage({ viewport: { width: size[0], height: size[1] }, deviceScaleFactor: opt('--png') ? 2 : 1 });
await page.goto(pathToFileURL(file).href);
await page.waitForLoadState('networkidle');
if (opt('--png')) await page.screenshot({ path: opt('--png'), clip: { x: 0, y: 0, width: size[0], height: size[1] } });
else await page.pdf({ path: opt('--pdf'), format: 'Letter', printBackground: true, margin: { top: '0.6in', bottom: '0.6in', left: '0.6in', right: '0.6in' } });
await browser.close();
