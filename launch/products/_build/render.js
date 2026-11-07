// Render HTML to PDF (Letter) or PNG.
//   node render.js pdf  in.html out.pdf
//   node render.js png  in.html out.png 1600 1200
const path = require('path');
const { chromium } = require(process.env.PW_PATH || 'playwright');

(async () => {
  const [mode, input, output, w, h] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage(mode === 'png'
    ? { viewport: { width: +w || 1600, height: +h || 1200 }, deviceScaleFactor: 1 }
    : {});
  await page.goto('file://' + path.resolve(input), { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  if (mode === 'pdf') {
    await page.emulateMedia({ media: 'print' });
    await page.pdf({ path: output, printBackground: true, preferCSSPageSize: true });
    // report pages whose content overflows (helps catch text running into footers)
    const over = await page.evaluate(() => {
      const out = [];
      document.querySelectorAll('.page').forEach((p, i) => {
        const folio = p.querySelector('.folio');
        const limit = folio ? folio.getBoundingClientRect().top - 4 : p.getBoundingClientRect().bottom - 30;
        let maxBottom = 0;
        p.querySelectorAll(':scope > *:not(.folio):not(.bg)').forEach(el => {
          const st = getComputedStyle(el);
          if (st.position === 'absolute') return;
          maxBottom = Math.max(maxBottom, el.getBoundingClientRect().bottom);
        });
        if (maxBottom > limit) out.push(`page ${i + 1}: content ends ${Math.round(maxBottom - limit)}px past limit`);
      });
      return out;
    });
    if (over.length) console.log('OVERFLOW\n' + over.join('\n'));
    else console.log('no overflow');
  } else {
    await page.screenshot({ path: output, fullPage: false });
  }
  await browser.close();
})();
