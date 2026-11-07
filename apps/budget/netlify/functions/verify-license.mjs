// POST /api/verify-license  { "licenseKey": "..." }  ->  { valid, plan, reason }
// Netlify Function (free tier). Keys are checked against whichever provider is configured:
//
//   Gumroad: set GUMROAD_PRODUCT_ID (Gumroad > product > Content > License key, "product ID").
//            Buyers get a license key in their receipt and paste it into the app.
//   Stripe:  set STRIPE_SECRET_KEY (a restricted key with read access to Checkout Sessions and
//            Subscriptions is enough). Set the Payment Link's success URL to
//            https://YOUR-SITE/?session_id={CHECKOUT_SESSION_ID} and the app activates itself.
//
//   Lemon Squeezy: set LEMONSQUEEZY_STORE_ID (Settings > Stores, the number) and, optionally,
//            LEMONSQUEEZY_PRODUCT_IDS (comma-separated). Turn on "Generate license keys" on the
//            product; buyers get a key in their receipt. No API key is needed to validate.
//
// Nothing here takes payments; it only reads whether a purchase is valid.

const GUMROAD_URL = 'https://api.gumroad.com/v2/licenses/verify';
const LEMON_URL = 'https://api.lemonsqueezy.com/v1/licenses/validate';
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const STRIPE_URL = 'https://api.stripe.com/v1/checkout/sessions/';

export async function verifyGumroad(key, { productId, fetchImpl = fetch }) {
  const body = new URLSearchParams({ product_id: productId, license_key: key, increment_uses_count: 'false' });
  const res = await fetchImpl(GUMROAD_URL, { method: 'POST', body, headers: { 'Content-Type': 'application/x-www-form-urlencoded' } });
  const data = await res.json().catch(() => ({}));
  if (!data.success) return { valid: false, reason: 'not_found' };
  const p = data.purchase || {};
  if (p.refunded || p.chargebacked || p.disputed) return { valid: false, reason: 'refunded' };
  if (p.subscription_ended_at || p.subscription_cancelled_at || p.subscription_failed_at) {
    // Cancelled subscriptions stay valid until the end of the period Gumroad reports.
    const end = p.subscription_ended_at || p.subscription_failed_at;
    if (end && Date.parse(end) <= Date.now()) return { valid: false, reason: 'subscription_ended' };
  }
  return { valid: true, plan: p.recurrence ? `pro-${p.recurrence}` : 'pro-lifetime', email: p.email || null };
}

export const isLemonKey = (key) => UUID.test(String(key || '').trim());

export async function verifyLemonSqueezy(key, { storeId, productIds = [], fetchImpl = fetch }) {
  const body = new URLSearchParams({ license_key: key });
  const res = await fetchImpl(LEMON_URL, { method: 'POST', body, headers: { Accept: 'application/json', 'Content-Type': 'application/x-www-form-urlencoded' } });
  if (res.status >= 500) throw new Error(`lemonsqueezy ${res.status}`);
  const data = await res.json().catch(() => ({}));
  const meta = data.meta || {};
  // A key from somebody else's store must never unlock this app.
  if (String(meta.store_id ?? '') !== String(storeId)) return { valid: false, reason: 'not_found' };
  if (productIds.length && !productIds.includes(String(meta.product_id ?? ''))) return { valid: false, reason: 'not_found' };
  const status = data.license_key && data.license_key.status;
  if (status === 'expired') return { valid: false, reason: 'subscription_ended' };
  if (status === 'disabled') return { valid: false, reason: 'refunded' };
  if (!data.valid) return { valid: false, reason: 'not_found' };
  const expires = data.license_key && data.license_key.expires_at;
  return { valid: true, plan: expires ? 'pro-subscription' : 'pro-lifetime', email: meta.customer_email || null };
}

export async function verifyStripe(sessionId, { secretKey, fetchImpl = fetch }) {
  if (!/^cs_(test|live)_[A-Za-z0-9]+$/.test(sessionId)) return { valid: false, reason: 'not_found' };
  const res = await fetchImpl(`${STRIPE_URL}${encodeURIComponent(sessionId)}?expand[]=subscription`, {
    headers: { Authorization: `Bearer ${secretKey}` },
  });
  if (res.status === 404) return { valid: false, reason: 'not_found' };
  if (!res.ok) throw new Error(`stripe ${res.status}`);
  const s = await res.json();
  if (s.status !== 'complete') return { valid: false, reason: 'unpaid' };
  if (s.mode === 'subscription') {
    const status = s.subscription && s.subscription.status;
    if (!['active', 'trialing', 'past_due'].includes(status)) return { valid: false, reason: 'subscription_ended' };
    return { valid: true, plan: 'pro-subscription', email: s.customer_details?.email || null };
  }
  if (s.payment_status !== 'paid') return { valid: false, reason: 'unpaid' };
  return { valid: true, plan: 'pro-lifetime', email: s.customer_details?.email || null };
}

export async function verify(licenseKey, { env = process.env, fetchImpl = fetch } = {}) {
  const key = String(licenseKey || '').trim();
  if (!key || key.length > 200) return { status: 400, body: { valid: false, reason: 'missing_key' } };
  try {
    if (key.startsWith('cs_')) {
      if (!env.STRIPE_SECRET_KEY) return { status: 503, body: { valid: false, reason: 'stripe_not_configured' } };
      return { status: 200, body: await verifyStripe(key, { secretKey: env.STRIPE_SECRET_KEY, fetchImpl }) };
    }
    if (isLemonKey(key) && env.LEMONSQUEEZY_STORE_ID) {
      const productIds = String(env.LEMONSQUEEZY_PRODUCT_IDS || '').split(',').map((x) => x.trim()).filter(Boolean);
      return { status: 200, body: await verifyLemonSqueezy(key, { storeId: env.LEMONSQUEEZY_STORE_ID, productIds, fetchImpl }) };
    }
    if (!env.GUMROAD_PRODUCT_ID) {
      const reason = isLemonKey(key) ? 'lemonsqueezy_not_configured' : 'gumroad_not_configured';
      return { status: 503, body: { valid: false, reason } };
    }
    return { status: 200, body: await verifyGumroad(key, { productId: env.GUMROAD_PRODUCT_ID, fetchImpl }) };
  } catch (err) {
    return { status: 502, body: { valid: false, reason: 'provider_error' } };
  }
}

export default async (req) => {
  const headers = { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' };
  if (req.method !== 'POST') return new Response(JSON.stringify({ error: 'POST only' }), { status: 405, headers });
  let payload = {};
  try { payload = await req.json(); } catch { /* empty body */ }
  const { status, body } = await verify(payload.licenseKey);
  return new Response(JSON.stringify(body), { status, headers });
};

export const config = { path: '/api/verify-license' };
