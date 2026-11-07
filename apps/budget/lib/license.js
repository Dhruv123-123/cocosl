// Pro license handling in the browser. The key is checked by a tiny serverless function
// (netlify/functions/verify-license.mjs) so the payment provider's secrets never reach the page.
// The result is cached; we re-check weekly and keep Pro working offline for a grace period.

export const RECHECK_MS = 7 * 24 * 3600 * 1000;
export const OFFLINE_GRACE_MS = 30 * 24 * 3600 * 1000;

export function needsRecheck(cached, now = Date.now()) {
  if (!cached || !cached.key) return false;
  return now - (cached.checkedAt || 0) > RECHECK_MS;
}

/** Is a cached license still good to use right now (including offline grace)? */
export function isActive(cached, now = Date.now()) {
  if (!cached || !cached.valid) return false;
  return now - (cached.checkedAt || 0) <= OFFLINE_GRACE_MS;
}

/**
 * Ask the verify endpoint about a key. Network failures keep the previous answer
 * (so a flaky connection never downgrades a paying user), but an explicit "invalid" does.
 */
export async function verifyLicense(key, { endpoint, fetchImpl = fetch, previous = null, now = Date.now() } = {}) {
  key = String(key || '').trim();
  if (!key) return { key: '', valid: false, checkedAt: now, reason: 'empty' };
  try {
    const res = await fetchImpl(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ licenseKey: key }) });
    if (res.status >= 500 || res.status === 429) throw new Error(`server ${res.status}`);
    const data = await res.json();
    return { key, valid: Boolean(data.valid), plan: data.plan || null, checkedAt: now, reason: data.reason || null, email: data.email || null };
  } catch (err) {
    if (previous && previous.key === key) return { ...previous, offline: true };
    return { key, valid: false, checkedAt: now, reason: 'network', offline: true };
  }
}
