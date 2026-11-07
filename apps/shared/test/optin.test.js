import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { OPTIN, COPY, brandOf, live, optinMode, optinHtml } from '../optin.js';
import { handleSubscribe, groupFor, SENDER_URL } from '../sender.js';

const root = join(dirname(fileURLToPath(import.meta.url)), '..', '..');

test('the opt-in stays hidden until a Sender form ID is set, and has one off switch', () => {
  assert.equal(OPTIN.provider, 'sender');
  assert.equal(live(), false);
  assert.equal(optinMode({ search: '' }), null);
  assert.equal(optinMode({ search: '?optin=preview' }), 'preview');
  const on = { ...OPTIN, senderFormId: 'abc123' };
  assert.equal(optinMode({ o: on }), 'live');
  assert.equal(optinMode({ o: { ...on, enabled: false } }), null);
  assert.equal(optinMode({ o: on, embedded: true }), null);
  assert.equal(optinMode({ o: on, hasSignup: true }), null);
});

test('copy for every brand in both languages, with a label and honeypot', () => {
  for (const b of Object.values(COPY)) for (const l of ['en', 'es']) assert.equal(b[l].length, 4);
  assert.equal(brandOf('scam-checker'), 'scam');
  assert.equal(brandOf('freelance-invoices'), '1099');
  assert.equal(brandOf('budget'), 'mms');
  const html = optinHtml({ app: 'scam-checker', mode: 'preview' });
  assert.match(html, /1 scam alert a week/);
  assert.match(html, /<label for="mms-optin-email"/);
  assert.match(html, /name="website" tabindex="-1"/);
  assert.match(html, / disabled>/);
  assert.match(optinHtml({ app: 'money-calculators', lang: 'es' }), /Envíame este plan/);
});

test('every tool page gets it through initTracking, and embeds hide it', () => {
  assert.match(readFileSync(join(root, 'shared', 'track.js'), 'utf8'), /mountOptin\(\{ app, page, win, doc \}\)/);
  assert.match(readFileSync(join(root, 'shared', 'embed-page.js'), 'utf8'), /\.mms-optin/);
});

test('subscribe function: honeypot, validation, not connected, Sender call', async () => {
  const req = (body, method = 'POST') => new Request('https://x/api/subscribe', { method, body: method === 'POST' ? JSON.stringify(body) : undefined });
  assert.equal((await handleSubscribe(req({}, 'GET'))).status, 405);
  assert.equal((await handleSubscribe(req({ email: 'a@b.co', website: 'bot' }))).status, 200);
  assert.equal((await handleSubscribe(req({ email: 'nope' }))).status, 400);
  assert.equal((await handleSubscribe(req({ email: 'a@b.co' }), {})).status, 503);
  let sent;
  const fake = async (url, opts) => { sent = { url, opts }; return new Response('{}', { status: 200 }); };
  const env = { SENDER_API_TOKEN: 't', SENDER_GROUP_ID: 'g1', SENDER_GROUP_SCAM: 'g2' };
  assert.equal((await handleSubscribe(req({ email: 'A@B.co', brand: 'scam' }), env, fake)).status, 200);
  assert.equal(sent.url, SENDER_URL);
  assert.equal(sent.opts.headers.Authorization, 'Bearer t');
  assert.deepEqual(JSON.parse(sent.opts.body), { email: 'a@b.co', groups: ['g2'], trigger_automation: true });
  assert.equal(groupFor('mms', env), 'g1');
  const failing = async () => new Response('', { status: 422 });
  assert.equal((await handleSubscribe(req({ email: 'a@b.co' }), env, failing)).status, 502);
});

test('older signup forms: Sender first, Netlify Forms while Sender is not connected', async () => {
  const { submitSignup } = await import('../optin.js');
  const form = { _d: [['form-name', 'scam-alerts'], ['email', 'a@b.co'], ['website', '']] };
  globalThis.FormData = class { constructor(f) { this.d = f._d; } get(k) { return (this.d.find((x) => x[0] === k) || [])[1] ?? null; } [Symbol.iterator]() { return this.d[Symbol.iterator](); } };
  const calls = [];
  const win = (status) => ({ fetch: async (url, opts) => { calls.push([url, opts]); return new Response('{}', { status: url === '/' ? 200 : status }); } });
  assert.equal(await submitSignup(form, { app: 'scam-checker', win: win(200) }), 'sender');
  assert.deepEqual(JSON.parse(calls[0][1].body), { email: 'a@b.co', website: '', brand: 'scam', app: 'scam-checker', page: '' });
  calls.length = 0;
  assert.equal(await submitSignup(form, { app: 'budget', win: win(503) }), 'netlify');
  assert.equal(calls[1][0], '/');
  assert.match(calls[1][1].body, /form-name=scam-alerts&email=a%40b.co/);
  assert.equal(await submitSignup(form, { app: 'budget', win: win(404) }), 'netlify');
  await assert.rejects(submitSignup(form, { app: 'budget', win: win(422) }));
});

test('every older signup form uses Sender', () => {
  for (const f of ['scam-checker/config.js', 'money-calculators/config.js', 'budget/config.js', 'medical-bills/config.js']) assert.match(readFileSync(join(root, f), 'utf8'), /provider: 'sender'/, f);
  for (const f of ['scam-checker/signup.js', 'money-calculators/app.js', 'budget/subscriptions.js', 'medical-bills/app.js']) assert.match(readFileSync(join(root, f), 'utf8'), /submitSignup\(form/, f);
});
