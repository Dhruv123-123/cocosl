// Renders HTML pages to PNG/PDF with Playwright. Called by build.py:
//   node render.mjs jobs.json    where jobs.json = [{"html": path, "out": path, "w": 1080, "h": 1080}]
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const jobs = JSON.parse(readFileSync(process.argv[2], "utf8"));
const browser = await chromium.launch();
for (const j of jobs) {
  const page = await browser.newPage({ viewport: { width: j.w, height: j.h }, deviceScaleFactor: 1 });
  await page.goto(pathToFileURL(j.html).href, { waitUntil: "load" });
  if (j.out.endsWith(".pdf")) await page.pdf({ path: j.out, format: "Letter", printBackground: true, preferCSSPageSize: true });
  else await page.screenshot({ path: j.out, clip: { x: 0, y: 0, width: j.w, height: j.h } });
  await page.close();
}
await browser.close();
