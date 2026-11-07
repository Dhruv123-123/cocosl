import { test } from 'node:test';
import assert from 'node:assert/strict';
import { verifyLicense, isActive, needsRecheck, OFFLINE_GRACE_MS, RECHECK_MS } from '../lib/license.js';
import { verify, verifyGumroad, verifyStripe } from '../netlify/functions/verify-license.mjs';

const jsonRes = (data, status = 200) => ({ status, ok: status < 400, json: async () => data });

test('client: valid key is cached with a timestamp', async () => {
  const r = await verifyLicense('ABC', { endpoint: '/api', fetchImpl: async () => jsonRes({ valid: true, plan: 'pro-lifetime' }), now: 1000 });
  assert.deepEqual([r.valid, r.plan, r.checkedAt], [true, 'pro-lifetime', 1000]);
});

test('client: network failure keeps a paying user on Pro', async () => {
  const previous = { key: 'ABC', valid: true, checkedAt: 5 };
  const r = await verifyLicense('ABC', { endpoint: '/api', fetchImpl: async () => { throw new Error('offline'); }, previous });
  assert.equal(r.valid, true);
  assert.equal(r.offline, true);
  assert.equal(r.checkedAt, 5);
});

test('client: server error is treated like being offline, explicit invalid is not', async () => {
  const previous = { key: 'ABC', valid: true, checkedAt: 5 };
  assert.equal((await verifyLicense('ABC', { endpoint: '/', fetchImpl: async () => jsonRes({}, 502), previous })).valid, true);
  assert.equal((await verifyLicense('ABC', { endpoint: '/', fetchImpl: async () => jsonRes({ valid: false, reason: 'refunded' }), previous })).valid, false);
});

test('client: grace period and recheck timing', () => {
  const c = { key: 'k', valid: true, checkedAt: 0 };
  assert.equal(isActive(c, OFFLINE_GRACE_MS), true);
  assert.equal(isActive(c, OFFLINE_GRACE_MS + 1), false);
  assert.equal(needsRecheck(c, RECHECK_MS + 1), true);
  assert.equal(needsRecheck(c, 10), false);
  assert.equal(isActive(null), false);
});

test('gumroad: valid, refunded and ended subscriptions', async () => {
  const call = (purchase, success = true) => verifyGumroad('KEY', { productId: 'p1', fetchImpl: async (url, opts) => {
    assert.match(String(opts.body), /product_id=p1/);
    assert.match(String(opts.body), /increment_uses_count=false/);
    return jsonRes({ success, purchase });
  } });
  assert.deepEqual(await call({ email: 'a@b.c' }), { valid: true, plan: 'pro-lifetime', email: 'a@b.c' });
  assert.equal((await call({ recurrence: 'monthly' })).plan, 'pro-monthly');
  assert.equal((await call({ refunded: true })).valid, false);
  assert.equal((await call({ subscription_ended_at: '2020-01-01T00:00:00Z' })).valid, false);
  assert.equal((await call({ subscription_cancelled_at: '2020-01-01T00:00:00Z', subscription_ended_at: null })).valid, true, 'cancelled but still in paid period');
  assert.equal((await call({}, false)).valid, false);
});

test('stripe: paid one-off, active and cancelled subscriptions', async () => {
  const call = (session, status = 200) => verifyStripe('cs_test_abc123', { secretKey: 'rk_test', fetchImpl: async (url, opts) => {
    assert.match(url, /checkout\/sessions\/cs_test_abc123\?expand/);
    assert.equal(opts.headers.Authorization, 'Bearer rk_test');
    return jsonRes(session, status);
  } });
  assert.equal((await call({ status: 'complete', mode: 'payment', payment_status: 'paid' })).valid, true);
  assert.equal((await call({ status: 'open', mode: 'payment', payment_status: 'unpaid' })).valid, false);
  assert.equal((await call({ status: 'complete', mode: 'subscription', subscription: { status: 'active' } })).plan, 'pro-subscription');
  assert.equal((await call({ status: 'complete', mode: 'subscription', subscription: { status: 'canceled' } })).valid, false);
  assert.equal((await call({}, 404)).valid, false);
  assert.equal((await verifyStripe('not-a-session', { secretKey: 'x' })).valid, false);
});

test('endpoint routes by key type and reports missing config', async () => {
  assert.equal((await verify('', { env: {} })).status, 400);
  assert.equal((await verify('ABC-123', { env: {} })).body.reason, 'gumroad_not_configured');
  assert.equal((await verify('cs_test_x', { env: {} })).body.reason, 'stripe_not_configured');
  const r = await verify('ABC-123', { env: { GUMROAD_PRODUCT_ID: 'p' }, fetchImpl: async () => { throw new Error('down'); } });
  assert.equal(r.status, 502);
});
