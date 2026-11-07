import { test } from 'node:test';
import { createHmac } from 'node:crypto';
import assert from 'node:assert/strict';
import { settings, twilioSignature, validSignature, handleIncoming, memoryStore, upstashStore, twiml, fit, hashNumber, monthKey, MAX_REPLY } from '../sms/sms.mjs';
import { handle } from '../netlify/functions/sms.mjs';
import combined from '../../functions/sms.mjs';

const ENV = { TWILIO_AUTH_TOKEN: '12345', SMS_HASH_SALT: 'pepper', SMS_FREE_CHECKS: '2', SMS_UNLIMITED_NUMBERS: '+15550000001', SMS_UPGRADE_URL: 'https://scamshield.example/family', SMS_CHECKER_URL: 'scamshield.example' };
const SCAM = 'USPS: Your package is held due to an incomplete address. Pay $1.99 now to reschedule: http://usps-redeliver.top/pay';

test('Twilio signature: URL plus params sorted by name, HMAC-SHA1, base64', () => {
  const url = 'https://mycompany.com/myapp.php?foo=1&bar=2';
  const params = { CallSid: 'CA1234567890ABCDE', Caller: '+12349013030', Digits: '1234', From: '+12349013030', To: '+18005551212' };
  const data = `${url}CallSidCA1234567890ABCDECaller+12349013030Digits1234From+12349013030To+18005551212`;
  const want = createHmac('sha1', '12345').update(data).digest('base64');
  // Param order in the request doesn't matter
  const shuffled = Object.fromEntries(Object.entries(params).reverse());
  assert.equal(twilioSignature('12345', url, shuffled), want);
  assert.equal(validSignature('12345', url, params, want), true);
  assert.equal(validSignature('12345', url, { ...params, Digits: '9' }, want), false);
  assert.equal(validSignature('12345', `${url}&x=1`, params, want), false);
  assert.equal(validSignature('', url, params, 'x'), false);
});

test('a scam text gets a high-risk verdict that fits in two segments', async () => {
  const cfg = settings(ENV);
  const { reply, counted, level } = await handleIncoming({ From: '+15551112222', Body: SCAM }, { cfg, store: memoryStore() });
  assert.equal(counted, true);
  assert.equal(level, 'high');
  assert.match(reply, /^HIGH RISK: this looks like a scam/);
  assert.match(reply, /official app/);
  assert.ok(reply.length <= MAX_REPLY, reply.length);
  assert.match(reply, /^[\x20-\x7e\n]+$/, 'plain GSM-friendly text');
});

test('an ordinary text is never called safe', async () => {
  const { reply } = await handleIncoming({ From: '+15551112222', Body: 'Hey are we still on for dinner at 7?' }, { cfg: settings(ENV), store: memoryStore() });
  assert.match(reply, /^No common scam signs found\. That isn't proof it's safe/);
});

test('free checks per month, unlimited numbers, help and pictures', async () => {
  const cfg = settings(ENV);
  const store = memoryStore();
  const now = new Date('2026-11-07T12:00:00Z');
  const from = '+15553334444';
  assert.match((await handleIncoming({ From: from, Body: SCAM }, { cfg, store, now })).reply, /1 free checks left/);
  assert.match((await handleIncoming({ From: from, Body: SCAM }, { cfg, store, now })).reply, /0 free checks left/);
  const third = await handleIncoming({ From: from, Body: SCAM }, { cfg, store, now });
  assert.equal(third.counted, false);
  assert.match(third.reply, /used your 2 free checks.*https:\/\/scamshield\.example\/family/);
  // New month, fresh checks
  assert.equal((await handleIncoming({ From: from, Body: SCAM }, { cfg, store, now: new Date('2026-12-01T00:00:00Z') })).counted, true);
  // Family plan number never runs out and isn't told a count
  for (let i = 0; i < 4; i++) assert.doesNotMatch((await handleIncoming({ From: '+15550000001', Body: SCAM }, { cfg, store, now })).reply, /free checks/);
  // Keywords and pictures don't use a check
  assert.match((await handleIncoming({ From: from, Body: 'HELP' }, { cfg, store, now })).reply, /Reply STOP to opt out/);
  assert.match((await handleIncoming({ From: from, Body: '', NumMedia: '1' }, { cfg, store, now })).reply, /only read text/);
  // Counts are stored under a hash, never the phone number
  const key = monthKey(hashNumber(from, 'pepper'), now);
  assert.equal(await store.get(key), '2');
  assert.doesNotMatch(key, /5553334444/);
});

test('replies are XML-escaped and trimmed', () => {
  assert.equal(twiml('a < b & "c"'), '<?xml version="1.0" encoding="UTF-8"?><Response><Message>a &lt; b &amp; &quot;c&quot;</Message></Response>');
  assert.equal(twiml(''), '<?xml version="1.0" encoding="UTF-8"?><Response></Response>');
  const long = fit('word '.repeat(200));
  assert.ok(long.length <= MAX_REPLY && long.endsWith('...'));
  assert.equal(fit('It’s “fine” — ok'), 'It\'s "fine" - ok');
});

test('upstash store speaks the REST API', async () => {
  const calls = [];
  const fake = async (url, opts) => { calls.push([url, JSON.parse(opts.body), opts.headers.Authorization]); return { ok: true, json: async () => ({ result: calls.length === 1 ? null : 'OK' }) }; };
  const s = upstashStore('https://x.upstash.io/', 'tok', fake);
  assert.equal(await s.get('k'), null);
  await s.set('k', 3);
  assert.deepEqual(calls[0], ['https://x.upstash.io', ['GET', 'k'], 'Bearer tok']);
  assert.deepEqual(calls[1][1].slice(0, 3), ['SET', 'k', '3']);
});

function twilioRequest(body, { url = 'https://scamshield.example/api/sms', token = ENV.TWILIO_AUTH_TOKEN, sign = true } = {}) {
  const params = { From: '+15557778888', To: '+15550001111', Body: body, NumMedia: '0' };
  const headers = { 'Content-Type': 'application/x-www-form-urlencoded' };
  if (sign) headers['X-Twilio-Signature'] = twilioSignature(token, url, params);
  return new Request(url, { method: 'POST', headers, body: new URLSearchParams(params).toString() });
}

test('webhook: checks the signature, answers with TwiML', async () => {
  const ok = await handle(twilioRequest(SCAM), ENV, memoryStore());
  assert.equal(ok.status, 200);
  assert.match(ok.headers.get('content-type'), /text\/xml/);
  assert.match(await ok.text(), /<Message>HIGH RISK/);
  assert.equal((await handle(twilioRequest(SCAM, { sign: false }), ENV, memoryStore())).status, 403);
  assert.equal((await handle(twilioRequest(SCAM, { token: 'wrong' }), ENV, memoryStore())).status, 403);
  assert.equal((await handle(twilioRequest(SCAM), { ...ENV, TWILIO_AUTH_TOKEN: '' }, memoryStore())).status, 503);
  assert.equal((await handle(twilioRequest(SCAM), { ...ENV, SMS_HASH_SALT: '' }, memoryStore())).status, 503);
  assert.equal((await handle(new Request('https://x/api/sms'), ENV, memoryStore())).status, 405);
  // Behind a proxy or custom domain: sign against the configured public URL
  const viaProxy = twilioRequest(SCAM, { url: 'https://scamshield.example/api/sms' });
  const moved = new Request('https://internal.netlify/api/sms', { method: 'POST', headers: viaProxy.headers, body: await viaProxy.text() });
  assert.equal((await handle(moved, { ...ENV, TWILIO_WEBHOOK_URL: 'https://scamshield.example/api/sms' }, memoryStore())).status, 200);
  // A store failure still answers politely
  const broken = { get: async () => { throw new Error('down'); }, set: async () => {} };
  assert.match(await (await handle(twilioRequest(SCAM), ENV, broken)).text(), /something went wrong/);
  assert.equal(typeof combined, 'function');
});
