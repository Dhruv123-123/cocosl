// GENERATED from apps/shared/ by tools/sync-shared.mjs. Edit the shared copy, not this one.
// Analytics and link tagging shared by every app. Canonical copy: apps/shared/track.js.
// `node tools/sync-shared.mjs` copies it to each app's lib/ (each app deploys on its own),
// and a test fails if a copy drifts.
//
// The UTM helpers mirror the factory's src/contentfactory/funnel/attribution.py so a link
// tagged here and one tagged by the factory look the same, and the webhooks parse both.
// Conventions: docs/UTM.md.

import { addAppHome } from './app-home.js';
import { mountOptin } from './optin.js';
import { mountOffer } from './offers.js';

const CLEAN = /[^A-Za-z0-9_.-]+/g;
export const UTM_KEYS = ['source', 'medium', 'campaign', 'content'];
export const REF_SEP = '__';
export const EVENTS = { affiliate: 'Affiliate Click', product: 'Product Click', signup: 'Signup', upgrade: 'Upgrade Click', upgradeShown: 'Upgrade Shown' };

export function clean(value, limit = 60) {
  return String(value ?? '').trim().replace(CLEAN, '-').replace(/^-+|-+$/g, '').slice(0, limit);
}

function split(url) {
  const hashAt = url.indexOf('#');
  const hash = hashAt >= 0 ? url.slice(hashAt) : '';
  const rest = hashAt >= 0 ? url.slice(0, hashAt) : url;
  const qAt = rest.indexOf('?');
  return { base: qAt >= 0 ? rest.slice(0, qAt) : rest, query: qAt >= 0 ? rest.slice(qAt + 1) : '', hash };
}

export function hostOf(url) {
  const m = /^https?:\/\/([^/?#]+)/i.exec(String(url || ''));
  return m ? m[1].replace(/^.*@/, '').replace(/:\d+$/, '').toLowerCase() : '';
}

/** Append utm_* params that aren't on the URL yet. Non-http URLs come back unchanged. */
export function withUtm(url, { source = '', medium = '', campaign = '', content = '' } = {}) {
  if (!url || !/^https?:\/\//i.test(url)) return url;
  const { base, query, hash } = split(url);
  const params = new URLSearchParams(query);
  const values = { source, medium, campaign, content };
  for (const k of UTM_KEYS) {
    const v = clean(values[k]);
    if (v && !params.has(`utm_${k}`)) params.append(`utm_${k}`, v);
  }
  const q = params.toString();
  return base + (q ? `?${q}` : '') + hash;
}

export function isStripeLink(url) {
  const h = hostOf(url);
  return h === 'buy.stripe.com' || h.endsWith('.buy.stripe.com');
}

export function isGumroadLink(url) {
  const h = hostOf(url);
  return h === 'gumroad.com' || h.endsWith('.gumroad.com') || h === 'gum.co';
}

export function isLemonLink(url) {
  const h = hostOf(url);
  return h === 'lemonsqueezy.com' || h.endsWith('.lemonsqueezy.com');
}

export const isCheckoutLink = (url) => isGumroadLink(url) || isStripeLink(url) || isLemonLink(url);

/** `pinterest__social__pin-emergency-fund-3`: Stripe-safe form of the three UTM values. */
export function clientReference({ source = '', medium = '', campaign = '' } = {}) {
  return [source, medium, campaign]
    .map((v) => clean(v, 60).replace(/[^A-Za-z0-9-]+/g, '-').replace(/^-+|-+$/g, '') || 'na')
    .join(REF_SEP).slice(0, 200);
}

/**
 * withUtm, plus a field the checkout keeps on the order (checkouts drop utm_* on the receipt):
 * client_reference_id on Stripe Payment Links, checkout[custom][ref] on Lemon Squeezy.
 */
export function tagLink(url, utm = {}) {
  let out = withUtm(url, utm);
  if (!(utm.source || utm.medium || utm.campaign)) return out;
  const field = isStripeLink(out) ? 'client_reference_id' : isLemonLink(out) ? 'checkout[custom][ref]' : '';
  if (field) {
    const { base, query, hash } = split(out);
    const params = new URLSearchParams(query);
    if (!params.has(field)) params.append(field, clientReference(utm));
    out = `${base}?${params}${hash}`;
  }
  return out;
}

/** The utm_* values on a query string, cleaned. {} when there are none. */
export function utmFrom(search) {
  const p = new URLSearchParams(search || '');
  const out = {};
  for (const k of UTM_KEYS) { const v = clean(p.get(`utm_${k}`)); if (v) out[k] = v; }
  return out;
}

/**
 * The UTM a checkout link should carry: the visit's own UTM when it arrived with one
 * (so a sale from a pin is credited to the pin, not to the app), else the app itself.
 */
export function checkoutUtm(visit, app, page = '') {
  if (visit && visit.source) return visit;
  return { source: clean(app), medium: 'app', campaign: clean(page) || clean(app) };
}

/** What a click on this link means: 'affiliate', 'product' or '' (other links). */
export function classify(href, rel = '') {
  if (/\bsponsored\b/i.test(rel)) return 'affiliate';
  if (isCheckoutLink(href)) return 'product';
  return '';
}

const state = { win: null, base: {} };

/** Send a custom event once initTracking has run (no-op otherwise), e.g. 'Upgrade Shown'. */
export function trackEvent(name, props = {}) {
  if (!state.win || typeof state.win.plausible !== 'function') return false;
  state.win.plausible(name, { props: { ...state.base, ...props } });
  return true;
}

/** Remember the first UTM seen in this browser session; returns the one to use. */
export function rememberVisit(search, storage) {
  const now = utmFrom(search);
  try {
    const saved = JSON.parse(storage?.getItem('utm_visit') || 'null');
    if (saved && saved.source) return saved;
    if (now.source) storage?.setItem('utm_visit', JSON.stringify(now));
  } catch { /* storage blocked: use this page's UTM only */ }
  return now;
}

/**
 * Turn on analytics for an app page. Does nothing until config.analytics.plausibleDomain is set.
 * - Loads Plausible's outbound-links script (cookieless; counts page views and outbound clicks).
 * - Sends "Affiliate Click", "Product Click", "Signup" and "Upgrade Click" events with brand/app props.
 * - Tags Gumroad, Stripe and Lemon Squeezy links with UTM at click time so sales are attributed (see checkoutUtm).
 */
export function initTracking({ config, app, page = '', win = globalThis.window, doc = globalThis.document } = {}) {
  addAppHome(win, doc); // Home button when opened inside the installed app (app-home.js)
  mountOptin({ app, page, win, doc }); // email opt-in box (optin.js); hidden until Sender is connected
  mountOffer({ app, page, win, doc }); // one matched affiliate offer (offers.js); hidden until its link is set
  const a = config?.analytics || {};
  if (!a.plausibleDomain || !win || !doc) return false;
  win.plausible = win.plausible || function plausible() { (win.plausible.q = win.plausible.q || []).push(arguments); };
  const s = doc.createElement('script');
  s.defer = true;
  s.dataset.domain = a.plausibleDomain;
  s.src = `${(a.plausibleHost || 'https://plausible.io').replace(/\/$/, '')}/js/script.outbound-links.js`;
  doc.head.append(s);

  let storage = null;
  try { storage = win.sessionStorage; } catch { /* blocked */ }
  const visit = rememberVisit(win.location?.search, storage);
  const base = { brand: config.brand || '', app };

  state.win = win;
  state.base = base;
  doc.addEventListener('click', (ev) => {
    // Any button or link marked data-upgrade="<where>" counts as an upgrade click.
    const up = ev.target?.closest?.('[data-upgrade]');
    if (up?.dataset && 'upgrade' in up.dataset) win.plausible(EVENTS.upgrade, { props: { ...base, where: up.dataset.upgrade || page || app } });
    const link = ev.target?.closest?.('a[href]');
    if (!link) return;
    const kind = classify(link.href, link.rel);
    if (!kind) return;
    if (kind === 'product') link.href = tagLink(link.href, checkoutUtm(visit, app, page));
    win.plausible(EVENTS[kind], { props: { ...base, link: link.dataset.id || hostOf(link.href) } });
  }, true);

  doc.addEventListener('submit', (ev) => {
    if (ev.target?.querySelector?.('input[type=email]')) win.plausible(EVENTS.signup, { props: { ...base, form: ev.target.getAttribute('name') || '' } });
  }, true);
  return true;
}
