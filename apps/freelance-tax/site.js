// Shared by every page: Plausible analytics, UTM on our own checkout links, and affiliate links from
// config.js. Follows docs/UTM.md: checkout links (Gumroad, Stripe, Lemon Squeezy) carry the visit's own
// UTM, or utm_source=freelance-tax&utm_medium=app&utm_campaign=<page> when the visit had none; affiliate
// links never get UTM and are counted with the "Affiliate Click" event instead. Nothing typed is sent.
import config from './config.js';

const APP = 'freelance-tax';
const BRAND = '1099-money';
const UTM_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content'];
const CHECKOUT = /(^|\.)(gumroad\.com|buy\.stripe\.com|lemonsqueezy\.com)$/;
export const live = (url) => typeof url === 'string' && /^https?:\/\//.test(url) && !url.includes('REPLACE_ME');

// The page name used as utm_campaign: "calculator", "free", "free-thanks", "compare-tax-software"...
export function pageName(path = location.pathname) {
  const parts = path.split('/').filter((p) => p && p !== 'index.html' && p !== 'apps' && p !== 'freelance-tax');
  return parts.length ? parts.join('-') : 'calculator';
}

function visitUtm() {
  const fromUrl = new URLSearchParams(location.search);
  const found = UTM_KEYS.filter((k) => fromUrl.get(k)).map((k) => [k, fromUrl.get(k)]);
  try {
    if (found.length) sessionStorage.setItem('fm-utm', JSON.stringify(found));
    else return JSON.parse(sessionStorage.getItem('fm-utm') || 'null');
  } catch { /* storage blocked */ }
  return found.length ? found : null;
}

// Adds UTM (and Stripe's client_reference_id) to a checkout URL. Never overrides UTM already present.
export function tagCheckout(href, utm, page) {
  const u = new URL(href);
  if (!CHECKOUT.test(u.hostname)) return href;
  const tags = utm && utm.length ? utm : [['utm_source', APP], ['utm_medium', 'app'], ['utm_campaign', page]];
  if (!UTM_KEYS.some((k) => u.searchParams.has(k))) for (const [k, v] of tags) u.searchParams.set(k, v);
  if (u.hostname === 'buy.stripe.com' && !u.searchParams.has('client_reference_id')) {
    const g = (k) => u.searchParams.get(k) || '';
    u.searchParams.set('client_reference_id', `${g('utm_source')}__${g('utm_medium')}__${g('utm_campaign')}`);
  }
  return u.toString();
}

function loadPlausible() {
  const a = config.analytics || {};
  if (!a.plausibleDomain || /^(localhost|127\.|0\.0\.0\.0|\[::1\])/.test(location.hostname)) return;
  window.plausible = window.plausible || function () { (window.plausible.q = window.plausible.q || []).push(arguments); };
  const s = document.createElement('script');
  s.defer = true;
  s.dataset.domain = a.plausibleDomain;
  s.src = `${a.plausibleHost || 'https://plausible.io'}/js/script.outbound-links.js`;
  document.head.appendChild(s);
}

// <a data-aff="keeper" data-site="https://keepertax.com">: the affiliate URL once it's real, else the homepage.
function wireAffiliates() {
  let any = false;
  document.querySelectorAll('a[data-aff]').forEach((a) => {
    const aff = config.affiliates[a.dataset.aff];
    if (aff && live(aff.url)) {
      a.href = aff.url;
      a.rel = 'sponsored noopener';
      a.dataset.paid = '1';
      a.closest('.pick')?.classList.add('paid');
      any = true;
    } else if (!a.dataset.site) {
      a.hidden = true;
    }
  });
  document.querySelectorAll('.aff-note').forEach((n) => { n.hidden = !any; });
}

function trackClicks(page, utm) {
  document.addEventListener('click', (ev) => {
    const a = ev.target.closest && ev.target.closest('a[href]');
    if (!a) return;
    let u;
    try { u = new URL(a.href); } catch { return; }
    if (CHECKOUT.test(u.hostname)) {
      a.href = tagCheckout(a.href, utm, page);
      window.plausible?.('Product Click', { props: { brand: BRAND, app: APP, link: u.pathname } });
    } else if (/\bsponsored\b/.test(a.rel)) {
      window.plausible?.('Affiliate Click', { props: { brand: BRAND, app: APP, link: a.dataset.aff || u.hostname } });
    }
  }, true);
}

export function setupSite() {
  const page = pageName();
  loadPlausible();
  wireAffiliates();
  trackClicks(page, visitUtm());
}
