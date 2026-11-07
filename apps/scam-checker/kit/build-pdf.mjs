// Renders kit.html to family-scam-safety-kit.pdf with the preinstalled Chromium (Playwright).
// Run from apps/: node scam-checker/kit/build-pdf.mjs [output.pdf]
import { createRequire } from 'node:module';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const out = process.argv[2] || join(here, 'family-scam-safety-kit.pdf');
const { chromium } = createRequire(import.meta.url)('playwright');
const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto(pathToFileURL(join(here, 'kit.html')).href);
await page.pdf({ path: out, format: 'Letter', printBackground: true, preferCSSPageSize: true });
await browser.close();
console.log('Wrote', out);
