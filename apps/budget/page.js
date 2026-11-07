// Small helpers shared by the bill tracker and deal countdown pages.
import { isActive } from './lib/license.js';
import { planFor } from './lib/plans.js';
import { trackEvent, EVENTS } from './lib/track.js';
import { limitPrompt, pricingHref } from './lib/checkout.js';
import config from './config.js';

export const $ = (s, root = document) => root.querySelector(s);
export const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
export const money = (n) => (Number(n) || 0).toLocaleString('en-US', { style: 'currency', currency: 'USD' });
export const live = (u) => typeof u === 'string' && /^https:\/\//.test(u) && !/REPLACE_ME/i.test(u);

export const store = {
  get(k) { try { return localStorage.getItem(k); } catch { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); return true; } catch { return false; } },
};

/** Pro comes from the license the budget app saved (the key is entered there). */
export function currentPlan() {
  let license = null;
  try { license = JSON.parse(store.get('mms-budget-license')); } catch { /* none */ }
  const pro = isActive(license);
  return { pro, plan: planFor(pro ? license : null) };
}

export function download(name, text, type) {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([text], { type }));
  a.download = name;
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}

/**
 * The upgrade prompt shown when a free limit is hit, linking to the pricing page.
 * `where` names the limit (see LIMIT_PROMPTS) for the Upgrade Shown / Upgrade Click events.
 */
export function upsellHtml(where, plan) {
  trackEvent(EVENTS.upgradeShown, { where });
  return `${esc(limitPrompt(where, plan))} <a href="${pricingHref(where)}" data-upgrade="${esc(where)}">Get Pro</a> (${esc(config.priceLine || '$3/month or $29 once')}).`;
}
