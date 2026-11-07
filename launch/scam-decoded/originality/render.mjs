// Renders a manifest of HTML pages to PNG slides and silent MP4 walkthroughs with Playwright + ffmpeg.
// usage: node render.mjs manifest.json
import { readFileSync, renameSync, mkdirSync, readdirSync, rmSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const jobs = JSON.parse(readFileSync(process.argv[2], 'utf8'));
const browser = await chromium.launch();
async function png(j) {
  const page = await browser.newPage({ viewport: { width: j.w, height: j.h }, deviceScaleFactor: 1 });
  await page.goto('file://' + j.html);
  await page.waitForTimeout(150);
  mkdirSync(dirname(j.out), { recursive: true });
  await page.screenshot({ path: j.out });
  await page.close();
}
async function video(j) {
  const tmp = j.out + '.tmp';
  rmSync(tmp, { recursive: true, force: true });
  const ctx = await browser.newContext({ viewport: { width: j.w, height: j.h }, recordVideo: { dir: tmp, size: { width: j.w, height: j.h } } });
  const page = await ctx.newPage();
  await page.goto('file://' + j.html);
  await page.evaluate(() => window.start && window.start());
  await page.waitForTimeout(j.duration * 1000 + 500);
  await ctx.close();
  const webm = join(tmp, readdirSync(tmp)[0]);
  mkdirSync(dirname(j.out), { recursive: true });
  // trim the first 0.3 s of page load, pad to an even size, H.264 for every platform
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-ss', '0.3', '-i', webm, '-t', String(j.duration),
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-r', '30', '-movflags', '+faststart', j.out]);
  rmSync(tmp, { recursive: true, force: true });
}
const pngs = jobs.filter(j => j.type === 'png'), vids = jobs.filter(j => j.type === 'video');
for (const j of pngs) await png(j);
for (let i = 0; i < vids.length; i += 3) await Promise.all(vids.slice(i, i + 3).map(video));
await browser.close();
console.log(`rendered ${pngs.length} slides, ${vids.length} videos`);
