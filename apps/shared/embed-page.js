// Embedded mode for any tool page (not the calculators, which have their own in money-calculators/app.js).
// A partner site adds the tool with apps/embed.js, which loads the page in an iframe with ?embed=1&frame=ID.
// Then this script: hides the page's own header, footer, sign-up box and FAQ; opens links in a new tab;
// keeps the iframe as tall as the tool (postMessage to the parent, the same message the calculators send);
// and adds a small credit link back to the full page. No cookies, no tracking, nothing sent anywhere else.
// Pages include it with <script type="module" src="lib/embed-page.js"></script> (path relative to the page).

export const HIDE = 'header.top, footer, .signup-box, .faq, section.faq, .offer-box, .signup, [data-embed-hide], .mms-optin';
export const BRANDS = { 'scam-checker': 'Scam Shield', 'freelance-invoices': '1099 Money' };

/** What the page should do for these URL parameters. frame ids are letters and digits only. */
export function embedState(search, pathname = '') {
  const p = new URLSearchParams(search);
  if (p.get('embed') !== '1') return null;
  const frame = /^[a-z0-9]{1,40}$/i.test(p.get('frame') || '') ? p.get('frame') : '';
  const app = Object.keys(BRANDS).find((a) => pathname.includes(`/${a}/`));
  const es = /\/es\/|\.es\.html$|-es\.html$|\/es\.html$|reto-ahorro|plan-quincena|tablero-dinero/.test(pathname);
  const brand = app ? BRANDS[app] : es ? 'Dinero Simple' : 'Money Made Simple';
  return { frame, brand, credit: es ? `Herramienta gratis de ${brand}` : `Free tool by ${brand}` };
}

if (typeof window !== 'undefined' && typeof document !== 'undefined') {
  const state = embedState(location.search, location.pathname);
  if (state) {
    document.documentElement.classList.add('mms-embedded');
    const style = document.createElement('style');
    style.textContent = `${HIDE}{display:none!important}body{margin:0}main{padding-top:8px!important;padding-bottom:0!important}
.mms-credit{text-align:center;font:13px/1.4 system-ui,sans-serif;margin:8px 0 4px;opacity:.85}.mms-credit a{color:inherit}`;
    document.head.append(style);
    const base = document.createElement('base');
    base.target = '_blank';
    document.head.append(base);
    const full = new URL(location.href);
    ['embed', 'frame'].forEach((k) => full.searchParams.delete(k));
    const credit = document.createElement('p');
    credit.className = 'mms-credit';
    const a = document.createElement('a');
    a.href = full.href; a.target = '_blank'; a.rel = 'noopener'; a.textContent = state.credit;
    credit.append(a);
    const place = () => (document.querySelector('main') || document.body).append(credit);
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', place); else place();
    if (state.frame && window.parent !== window) {
      let last = 0;
      const send = () => {
        const h = Math.ceil(document.documentElement.getBoundingClientRect().height);
        if (h !== last) { last = h; window.parent.postMessage({ type: 'mms-calc-height', id: state.frame, height: h }, '*'); }
      };
      new ResizeObserver(send).observe(document.documentElement);
      addEventListener('load', send);
    }
  }
}
