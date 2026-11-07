// Render the Spanish guide to PDF and report spare space per page (negative = text overflows the page).
// node launch/dinero-simple/src/render_pdf.js $PWD/launch/dinero-simple/product/el-presupuesto-de-20-minutos.html $PWD/launch/dinero-simple/product/El-Presupuesto-de-20-Minutos.pdf
const { chromium } = require('playwright');
(async () => {
  const [src, out] = process.argv.slice(2);
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + src); await p.waitForTimeout(500);
  const r = await p.evaluate(() => [...document.querySelectorAll('.page')].map((e,i)=>{
    const f=e.querySelector('.folio'); let maxB=0;
    for (const c of e.children){ if(c.classList.contains('folio')) continue; maxB=Math.max(maxB,c.getBoundingClientRect().bottom);}
    const lim = f ? f.getBoundingClientRect().top : e.getBoundingClientRect().bottom;
    return [i+1, Math.round(lim-maxB)];}));
  console.log(JSON.stringify(r));
  if (out) await p.pdf({ path: out, format: 'Letter', printBackground: true, preferCSSPageSize: true });
  await b.close();
})();
