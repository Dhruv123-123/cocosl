// "Text it to us" scam check: someone forwards a suspicious text (or pastes an email) to our
// Twilio number and gets a short verdict back. Runs the same checks as the website
// (lib/scan.js). Server-side only (Node): the Netlify Function in netlify/functions/sms.mjs
// wires it to Twilio.
//
// Privacy: message text is checked in memory and never stored or logged. Usage counts are
// keyed by a salted hash of the phone number, never the number itself.
import { createHmac, createHash, timingSafeEqual } from 'node:crypto';
import { analyzeMessage } from '../lib/scan.js';

export const MAX_REPLY = 320; // two SMS segments of plain (GSM-7) text

export function settings(env = process.env) {
  const list = (v) => String(v || '').split(',').map((s) => s.trim()).filter(Boolean);
  return {
    authToken: env.TWILIO_AUTH_TOKEN || '',
    webhookUrl: env.TWILIO_WEBHOOK_URL || '', // the exact URL set in Twilio, if req.url differs (custom domain, proxy)
    freeChecks: Math.max(0, Number(env.SMS_FREE_CHECKS ?? 5) || 0),
    unlimited: new Set(list(env.SMS_UNLIMITED_NUMBERS)), // family-plan numbers, E.164 (+15551234567)
    upgradeUrl: env.SMS_UPGRADE_URL || '',
    checkerUrl: env.SMS_CHECKER_URL || '',
    salt: env.SMS_HASH_SALT || '',
    brand: env.SMS_BRAND || 'Scam Shield',
    skipSignature: env.SMS_SKIP_SIGNATURE === '1', // local testing only
  };
}

/** Twilio's X-Twilio-Signature: base64(HMAC-SHA1(authToken, url + sorted key+value pairs)). */
export function twilioSignature(authToken, url, params) {
  const data = url + Object.keys(params).sort().map((k) => k + params[k]).join('');
  return createHmac('sha1', authToken).update(Buffer.from(data, 'utf8')).digest('base64');
}

export function validSignature(authToken, url, params, header) {
  if (!authToken || !header) return false;
  const want = Buffer.from(twilioSignature(authToken, url, params));
  const got = Buffer.from(String(header));
  return want.length === got.length && timingSafeEqual(want, got);
}

export const hashNumber = (number, salt) => createHash('sha256').update(`${salt}|${number}`).digest('hex').slice(0, 32);

export function xml(s) {
  return String(s).replace(/[<>&'"]/g, (c) => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', "'": '&apos;', '"': '&quot;' })[c]);
}
export const twiml = (message) => `<?xml version="1.0" encoding="UTF-8"?><Response>${message ? `<Message>${xml(message)}</Message>` : ''}</Response>`;

// Keep replies in the GSM-7 alphabet so each segment holds 160 characters, not 70.
export function plain(s) {
  return String(s).replace(/[‘’]/g, "'").replace(/[“”]/g, '"').replace(/[–—]/g, '-').replace(/…/g, '...').replace(/[^\x20-\x7e\n]/g, '');
}

export function fit(s, max = MAX_REPLY) {
  s = plain(s).trim();
  if (s.length <= max) return s;
  return `${s.slice(0, max - 3).replace(/[\s,;:.]+\S*$/, '')}...`;
}

const KEYWORDS = /^\s*(help|info|start|unstop|yes)\s*$/i;

/** The reply text for one check result. Never claims certainty. */
export function verdictText(result, cfg, maxFlags = 2) {
  const flags = result.signals.slice(0, maxFlags).map((s) => s.label.replace(/\.$/, ''));
  for (const l of result.links) if (flags.length < maxFlags && l.issues.length) flags.push(l.issues[0].label);
  const more = cfg.checkerUrl ? ` Details: ${cfg.checkerUrl}` : '';
  if (result.level === 'high') {
    return `HIGH RISK: this looks like a scam${result.category ? ` (${result.category.toLowerCase()})` : ''}. ${flags.length ? `Red flags: ${flags.join('; ')}. ` : ''}Don't tap links, reply or call back. If it's about a real account, use the official app or the number on your card.${more}`;
  }
  if (result.level === 'medium') {
    return `SUSPICIOUS: some scam signs${flags.length ? `: ${flags.join('; ')}` : ''}. Don't use its links or numbers. Check with the company through its official app or website.${more}`;
  }
  return `No common scam signs found. That isn't proof it's safe: if it asks for money, a code or a login, contact the company through its official app or number.${more}`;
}

export function helpText(cfg) {
  return `${cfg.brand}: forward a suspicious text or paste an email here and we'll check it for scam signs. ${cfg.freeChecks} free checks a month. Reply STOP to opt out. Msg & data rates may apply.`;
}

/** In-memory usage store (per function instance). Fine for testing; use a shared store live. */
export function memoryStore() {
  const m = new Map();
  return { async get(k) { return m.get(k) ?? null; }, async set(k, v) { m.set(k, v); } };
}

/** Upstash Redis over its REST API (free tier, no npm package needed). */
export function upstashStore(url, token, fetchImpl = fetch) {
  const call = async (...cmd) => {
    const res = await fetchImpl(url.replace(/\/$/, ''), { method: 'POST', headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }, body: JSON.stringify(cmd) });
    if (!res.ok) throw new Error(`upstash ${res.status}`);
    return (await res.json()).result;
  };
  return {
    async get(k) { const v = await call('GET', k); return v == null ? null : String(v); },
    async set(k, v) { await call('SET', k, String(v), 'EX', String(40 * 24 * 3600)); },
  };
}

export const monthKey = (hash, now = new Date()) => `sms:${hash}:${now.toISOString().slice(0, 7)}`;

/**
 * Handle one incoming message. params: Twilio's form fields (From, Body, NumMedia...).
 * Returns { reply, counted } where reply is the SMS text (or '' for no reply).
 */
export async function handleIncoming(params, { cfg, store, now = new Date() }) {
  const from = String(params.From || '');
  const body = String(params.Body || '').trim();
  if (!from) return { reply: '', counted: false };
  if (KEYWORDS.test(body)) return { reply: fit(helpText(cfg)), counted: false };
  if (!body) {
    return { reply: fit(Number(params.NumMedia || 0) > 0
      ? "We can only read text, not pictures. Copy the message's words (and any link) and send them here."
      : 'Send us the text of the suspicious message and we\'ll check it.'), counted: false };
  }
  const unlimited = cfg.unlimited.has(from);
  const key = monthKey(hashNumber(from, cfg.salt), now);
  const used = Number(await store.get(key)) || 0;
  if (!unlimited && used >= cfg.freeChecks) {
    return { reply: fit(`You've used your ${cfg.freeChecks} free checks this month. ${cfg.upgradeUrl ? `Family plan, unlimited checks: ${cfg.upgradeUrl}` : 'They reset on the 1st.'} You can always check for free at our website.`), counted: false };
  }
  const result = analyzeMessage(body);
  await store.set(key, String(used + 1));
  const left = unlimited ? '' : ` (${Math.max(0, cfg.freeChecks - used - 1)} free checks left this month)`;
  // Fewer red flags before dropping the count: both matter more than a long list.
  let reply = '';
  for (const n of [2, 1, 0]) { reply = plain(verdictText(result, cfg, n)) + left; if (reply.length <= MAX_REPLY) break; }
  return { reply: fit(reply), counted: true, level: result.level };
}
