// Small helpers shared by the bill tracker and deal countdown pages.
import { isActive } from './lib/license.js';
import { planFor } from './lib/plans.js';

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

/** A message with a link to upgrade in the budget app (index.html#upgrade opens the Pro dialog). */
export function upsellHtml(text) {
  return `${esc(text)} <a href="./#upgrade">Get Pro</a> ($3/month or $29 once).`;
}
