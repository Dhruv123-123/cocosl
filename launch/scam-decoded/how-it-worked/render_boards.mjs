// Render every out/*.html case board to a 1920x1080 PNG next to it.
import { readdirSync } from "node:fs";
import { join } from "node:path";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const dir = process.argv[2];
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
for (const f of readdirSync(dir).filter((f) => f.endsWith(".html"))) {
  await page.goto("file://" + join(dir, f));
  await page.screenshot({ path: join(dir, f.replace(/\.html$/, ".png")) });
}
await browser.close();
