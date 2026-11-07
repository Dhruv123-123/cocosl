// Checkout and upgrade logic shared by the budget app, the pricing page and the Pro pages.
// No DOM here so it can be tested. Payment links live in config.js (config.pricing).
//
// Any of these works as a pricing URL, and the license check (netlify/functions/verify-license.mjs)
// knows how to verify keys from each:
//   Lemon Squeezy  https://STORE.lemonsqueezy.com/buy/VARIANT-ID    (key: a UUID in the receipt)
//   Gumroad        https://STORE.gumroad.com/l/PRODUCT               (key: in the receipt)
//   Stripe         https://buy.stripe.com/LINK-ID                    (no key: the app reads ?session_id=)

import { PLANS } from './plans.js';

export const live = (u) => typeof u === 'string' && /^https:\/\//.test(u) && !/REPLACE_ME/i.test(u);

/** The buy buttons to show: live links only, none in app-store builds (stores need their own billing). */
export function checkoutOptions(config) {
  if ((config.distribution || 'web') !== 'web') return [];
  return Object.entries(config.pricing || {})
    .filter(([, p]) => p && live(p.url))
    .map(([id, p]) => ({ id, label: p.label, url: p.url, note: p.note || '', best: Boolean(p.best) }));
}

export const REASONS = {
  not_found: "We couldn't find that key. Check for typos, or copy it straight from your receipt.",
  refunded: 'That purchase was refunded or disabled.',
  subscription_ended: 'That subscription has ended. Renew it to turn Pro back on.',
  unpaid: "That payment hasn't gone through yet. Try again in a minute.",
  network: "Couldn't reach the license server. Try again in a minute.",
  missing_key: 'Paste the license key from your receipt.',
  gumroad_not_configured: 'License checks are not set up on this site yet.',
  stripe_not_configured: 'License checks are not set up on this site yet.',
  lemonsqueezy_not_configured: 'License checks are not set up on this site yet.',
};
export const reasonText = (reason) => REASONS[reason] || 'That key did not work.';

/**
 * A key handed back in the URL after checkout: Stripe's ?session_id=cs_..., or ?license_key=
 * for a provider whose thank-you redirect can include it. Returns '' when there is none.
 */
export function keyFromUrl(search) {
  const p = new URLSearchParams(search || '');
  const k = (p.get('session_id') || p.get('license_key') || '').trim();
  return k && k.length <= 200 ? k : '';
}

const fmt = (v) => (v === Infinity ? 'Unlimited' : v === true ? 'Yes' : v === false ? 'No' : String(v));

/** Rows for the free-vs-Pro table, read from PLANS so the page never disagrees with the app. */
export function compareRows(plans = PLANS) {
  const rows = [
    ['Budget categories', 'maxCategories'],
    ['Savings goals', 'goals'],
    ['Past and future months', 'history'],
    ['Import your bank CSV', 'csvImport'],
    ['Bills in the negotiation tracker', 'bills'],
    ['0% and deferred-interest deals', 'deals'],
    ['Calendar reminders (.ics)', 'reminders'],
    ['Backup and restore', 'backup'],
  ];
  return rows.map(([label, k]) => ({ label, free: fmt(plans.free[k]), pro: fmt(plans.pro[k]) }));
}

/**
 * The upgrade prompt for a free limit. `where` names the limit for the "Upgrade Click"
 * and "Upgrade Shown" events, so the owner can see which limit sells Pro.
 */
export const LIMIT_PROMPTS = {
  categories: (p) => `The free plan has ${p.maxCategories} categories. Pro has as many as you need.`,
  goals: (p) => `The free plan includes ${p.goals} savings goal. Pro has unlimited goals.`,
  history: () => 'Looking back and planning ahead month by month is a Pro feature.',
  csv: () => "Importing your bank's CSV export is a Pro feature.",
  bills: (p) => `The free plan tracks ${p.bills} bills. Pro tracks every bill.`,
  deals: (p) => `The free plan counts down ${p.deals} deal. Pro covers every card and loan.`,
  reminders: () => 'Calendar reminders are a Pro feature.',
};
export function limitPrompt(where, plan = PLANS.free) {
  const f = LIMIT_PROMPTS[where];
  return f ? f(plan) : 'Pro unlocks every bill and deal, calendar reminders, CSV import and more.';
}

/** Link to the pricing page that remembers which limit sent the person there. */
export const pricingHref = (where = '', base = 'pricing.html') => (where ? `${base}?from=${encodeURIComponent(where)}` : base);

// ---------- first-run onboarding ----------

/** Split take-home pay 50/30/20 across the starter categories (needs/wants/savings), whole dollars. */
export function starterPlan(categories, income) {
  const pay = Math.max(0, Number(income) || 0);
  const share = { needs: 0.5, wants: 0.3, savings: 0.2 };
  const out = {};
  for (const group of Object.keys(share)) {
    const ids = categories.filter((c) => c.group === group).map((c) => c.id);
    if (!ids.length) continue;
    const total = Math.round(pay * share[group]);
    const each = Math.floor(total / ids.length);
    ids.forEach((id, i) => { out[id] = i === 0 ? total - each * (ids.length - 1) : each; });
  }
  return out;
}

/** Show the welcome steps only on a fresh budget that hasn't seen them. */
export function needsOnboarding(state, seen) {
  if (seen) return false;
  const months = Object.values(state.months || {});
  const anyIncome = months.some((m) => Number(m.income) > 0);
  return !anyIncome && !(state.transactions || []).length && !(state.goals || []).length;
}
