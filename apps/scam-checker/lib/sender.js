// GENERATED from apps/shared/ by tools/sync-shared.mjs. Edit the shared copy, not this one.
// POST /api/subscribe: adds an email from the opt-in box (optin.js) to a Sender (sender.net) group.
// Server side only (Netlify Functions import it); it's in shared/ so every app's copy stays the same.
// Netlify environment variables:
//   SENDER_API_TOKEN   Sender > Settings > API access tokens
//   SENDER_GROUP_ID    the group new subscribers join (its welcome automation and double opt-in run from there)
//   SENDER_GROUP_SCAM, SENDER_GROUP_1099   optional: a different group per brand (falls back to SENDER_GROUP_ID)
// Until the token and group are set it answers 503 and stores nothing. Check the request format against
// Sender's API docs (POST /v2/subscribers) before launch.

export const SENDER_URL = 'https://api.sender.net/v2/subscribers';
const EMAIL = /^[^\s@]{1,64}@[^\s@]{1,190}\.[^\s@]{2,24}$/;

export function groupFor(brand, env) {
  if (brand === 'scam' && env.SENDER_GROUP_SCAM) return env.SENDER_GROUP_SCAM;
  if (brand === '1099' && env.SENDER_GROUP_1099) return env.SENDER_GROUP_1099;
  return env.SENDER_GROUP_ID || '';
}

const json = (status, body) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

export async function handleSubscribe(req, env = {}, doFetch = globalThis.fetch) {
  if (req.method !== 'POST') return json(405, { error: 'POST only' });
  let body;
  try { body = await req.json(); } catch { return json(400, { error: 'bad request' }); }
  if (body?.website) return json(200, { ok: true }); // honeypot: pretend it worked
  const email = String(body?.email || '').trim().toLowerCase();
  if (!EMAIL.test(email)) return json(400, { error: 'invalid email' });
  const group = groupFor(body?.brand, env);
  if (!env.SENDER_API_TOKEN || !group) return json(503, { error: 'not connected' });
  const res = await doFetch(SENDER_URL, {
    method: 'POST',
    headers: { Authorization: `Bearer ${env.SENDER_API_TOKEN}`, 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ email, groups: [group], trigger_automation: true }),
  }).catch(() => null);
  if (!res || !res.ok) return json(502, { error: 'signup failed' }); // never echo the address in logs
  return json(200, { ok: true });
}
