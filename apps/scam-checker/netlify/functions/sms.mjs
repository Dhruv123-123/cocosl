// POST /api/sms: Twilio "A message comes in" webhook for the text-us scam check.
// Setup (all config, no code): see scam-checker/sms/SMS_SETUP.md.
//   TWILIO_AUTH_TOKEN      required: every request's signature is checked with it
//   SMS_HASH_SALT          required: any long random string (usage counts use hashed numbers)
//   UPSTASH_REDIS_REST_URL + UPSTASH_REDIS_REST_TOKEN   shared usage counts (recommended)
//   SMS_FREE_CHECKS (5), SMS_UNLIMITED_NUMBERS, SMS_UPGRADE_URL, SMS_CHECKER_URL, TWILIO_WEBHOOK_URL
import { settings, validSignature, handleIncoming, twiml, memoryStore, upstashStore } from '../../sms/sms.mjs';

const memory = memoryStore();

export function storeFor(env) {
  if (env.UPSTASH_REDIS_REST_URL && env.UPSTASH_REDIS_REST_TOKEN) return upstashStore(env.UPSTASH_REDIS_REST_URL, env.UPSTASH_REDIS_REST_TOKEN);
  return memory; // counts reset when the function restarts: set up Upstash before going live
}

export async function handle(req, env = process.env, store = storeFor(env)) {
  const xmlHeaders = { 'Content-Type': 'text/xml; charset=utf-8' };
  if (req.method !== 'POST') return new Response('POST only', { status: 405 });
  const cfg = settings(env);
  if (!cfg.authToken && !cfg.skipSignature) return new Response('Not configured: set TWILIO_AUTH_TOKEN', { status: 503 });
  if (!cfg.salt) return new Response('Not configured: set SMS_HASH_SALT', { status: 503 });
  const params = Object.fromEntries(new URLSearchParams(await req.text()));
  if (!cfg.skipSignature && !validSignature(cfg.authToken, cfg.webhookUrl || req.url, params, req.headers.get('x-twilio-signature'))) {
    return new Response('Bad signature', { status: 403 });
  }
  try {
    const { reply } = await handleIncoming(params, { cfg, store });
    return new Response(twiml(reply), { status: 200, headers: xmlHeaders });
  } catch (err) {
    console.error('sms check failed:', err.message); // never log the message itself
    return new Response(twiml('Sorry, something went wrong on our side. Please try again in a few minutes.'), { status: 200, headers: xmlHeaders });
  }
}

export default (req) => handle(req);

export const config = { path: '/api/sms' };
