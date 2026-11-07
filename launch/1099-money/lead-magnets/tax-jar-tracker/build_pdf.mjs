// Renders tracker.html to the free download: apps/freelance-tax/downloads/tax-jar-tracker.pdf
//   node launch/1099-money/lead-magnets/tax-checklist/build_pdf.mjs     (needs Playwright)
import { createRequire } from 'node:module';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const out = join(here, '..', '..', '..', '..', 'apps', 'freelance-tax', 'downloads', 'tax-jar-tracker.pdf');
const { chromium } = createRequire(import.meta.url)('playwright');
const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto('file://' + join(here, 'tracker.html'));
// Fail if anything spills past the bottom of a page (each .page is a fixed Letter sheet).
const over = await page.evaluate(() => [...document.querySelectorAll('.page')].map((p, i) => {
  const limit = p.getBoundingClientRect().bottom - 0.55 * 96;
  return [...p.querySelectorAll('*:not(.folio):not(.folio *)')].some((e) => !p.classList.contains('cover') && e.getBoundingClientRect().bottom > limit) ? i + 1 : 0;
}).filter(Boolean));
if (over.length) throw new Error(`content runs into the footer on page(s) ${over.join(', ')}`);
await page.pdf({ path: out, format: 'Letter', printBackground: true, preferCSSPageSize: true });
await browser.close();
console.log('wrote', out);
