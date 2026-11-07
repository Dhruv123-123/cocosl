// Vendor payment check (vendor/index.html): a small business gets a payment request or a
// "we changed our bank details" email and checks it before paying. This is how business email
// compromise (BEC) works: a fake or hijacked vendor email redirects a real payment.
// Rule-based and private: runs in the browser, nothing is uploaded. It can't prove a request is
// safe; the answer is always "verify by phone on a number you already had".
import { deLeet } from './scan.js';

export const FREE_MAIL = ['gmail.com', 'googlemail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'live.com', 'aol.com', 'icloud.com', 'me.com', 'proton.me', 'protonmail.com', 'gmx.com', 'mail.com', 'zoho.com', 'yandex.com'];

export const KINDS = {
  'bank-change': 'The vendor says their bank details have changed',
  invoice: 'An invoice or payment request from a vendor',
  boss: 'Someone senior asks for an urgent payment or gift cards',
  new: 'A new vendor wants to be paid for the first time',
};

// [id, points, label, why]
export const FLAGS = [
  ['changedBank', 35, 'New bank account or payment details', 'Changed bank details are the core of vendor payment fraud. Treat every change as unverified until you call.'],
  ['urgent', 15, 'Pressure to pay today or "before the cutoff"', 'Urgency is there to stop you from checking.'],
  ['secrecy', 20, 'Asks you to keep it quiet or not to call', '"Don\'t call, I\'m in meetings" or "keep this between us" is a classic tell.'],
  ['emailOnly', 10, 'The request came only by email or text', 'Fraudsters avoid the phone because a call to the real person ends the scam.'],
  ['newPhone', 20, 'Gives a new phone number to call for confirmation', 'A number from the same email reaches the fraudster. Use the number you already had.'],
  ['replyTo', 20, 'Replies go to a different address than the sender', 'A mismatched reply-to sends your answer to the fraudster even if the From line looks right.'],
  ['newContact', 10, 'A different person from the one you usually deal with', 'New contacts and "my colleague is out" stories cover for a stranger.'],
  ['nameMismatch', 25, 'The account holder name doesn\'t match the vendor', 'A payment to a person or a different company name is a strong sign the money is being redirected.'],
  ['overseas', 15, 'Account in a different country or bank than before', 'Moving to an unfamiliar bank or country makes the money hard to get back.'],
  ['unusualAmount', 10, 'Amount or timing isn\'t normal for this vendor', 'Odd amounts, extra invoices or early payment requests deserve a second look.'],
  ['giftCards', 40, 'Asks for gift cards, crypto or a payment app', 'No real vendor or manager needs gift cards or crypto. This is a scam.'],
  ['loginLink', 20, 'Invoice is behind a link that asks you to sign in', 'Fake "view invoice" pages steal email passwords, which lets fraudsters read your real threads.'],
];

const POINTS = Object.fromEntries(FLAGS.map(([id, p]) => [id, p]));
const KIND_POINTS = { 'bank-change': 15, invoice: 0, boss: 15, new: 5 };

const lev = (a, b) => {
  const dp = Array.from({ length: a.length + 1 }, (_, i) => [i, ...Array(b.length).fill(0)]);
  for (let j = 1; j <= b.length; j++) dp[0][j] = j;
  for (let i = 1; i <= a.length; i++) for (let j = 1; j <= b.length; j++) {
    dp[i][j] = Math.min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
  }
  return dp[a.length][b.length];
};

/** The domain of an email address or web address ('' if there isn't one). */
export function domainOf(s) {
  const v = String(s || '').trim().toLowerCase().replace(/^.*<([^>]+)>.*$/, '$1');
  const m = /@([a-z0-9.-]+\.[a-z]{2,})$/.exec(v) || /^(?:https?:\/\/)?(?:www\.)?([a-z0-9.-]+\.[a-z]{2,})(?:[/:?#].*)?$/.exec(v);
  return m ? m[1].replace(/^www\./, '') : '';
}

const TWO_PART = ['co.uk', 'com.au', 'co.nz', 'com.mx', 'co.in', 'com.br'];
const registrable = (d) => {
  const p = d.split('.');
  return TWO_PART.includes(p.slice(-2).join('.')) ? p.slice(-3).join('.') : p.slice(-2).join('.');
};
const nameOf = (d) => registrable(d).split('.')[0];

/**
 * Compare the address a request came from with the vendor's address in your own records.
 * match | subdomain | lookalike | freemail | different | unknown
 */
export function compareDomains(known, sender) {
  const k = domainOf(known);
  const s = domainOf(sender);
  if (!s) return { result: 'unknown', known: k, sender: s };
  if (FREE_MAIL.includes(s) && !FREE_MAIL.includes(k)) return { result: 'freemail', known: k, sender: s };
  if (!k) return { result: 'unknown', known: k, sender: s };
  if (s === k) return { result: 'match', known: k, sender: s };
  if (registrable(s) === registrable(k)) return { result: 'subdomain', known: k, sender: s };
  const a = nameOf(k);
  const b = nameOf(s);
  const close = a === b // same name, different ending (.com vs .co)
    || deLeet(a) === deLeet(b)
    || a.replace(/-/g, '') === b.replace(/-/g, '')
    || b.includes(a) || a.includes(b)
    || (Math.min(a.length, b.length) >= 4 && lev(a, b) <= 2);
  return { result: close ? 'lookalike' : 'different', known: k, sender: s };
}

const DOMAIN_POINTS = { match: 0, subdomain: 5, unknown: 0, freemail: 30, different: 25, lookalike: 45 };
const DOMAIN_TEXT = {
  match: 'The sender address matches the one in your records. That is good, but a hacked real mailbox looks exactly like this, so changed bank details still need a call.',
  subdomain: 'The sender is on a part of the vendor\'s own domain. Probably fine, but still verify any change by phone.',
  freemail: 'The request came from a free email account, not the vendor\'s business address.',
  different: 'The sender\'s domain is different from the vendor\'s domain in your records.',
  lookalike: 'The sender\'s domain looks like your vendor\'s but isn\'t the same. Look-alike domains are made for this scam.',
  unknown: '',
};

/**
 * Score a request. values: { kind, known, sender, replyTo, flags: [ids] }
 * Returns { score 0-100, level 'low'|'medium'|'high', hold, reasons: [{label, why}], domain }.
 */
export function checkRequest(values = {}) {
  const flags = new Set((values.flags || []).filter((f) => f in POINTS));
  const domain = compareDomains(values.known, values.sender);
  if (values.replyTo && domainOf(values.replyTo) && domain.sender && domainOf(values.replyTo) !== domain.sender) flags.add('replyTo');
  const kind = KINDS[values.kind] ? values.kind : 'invoice';
  let score = (KIND_POINTS[kind] || 0) + DOMAIN_POINTS[domain.result];
  const reasons = [];
  if (DOMAIN_TEXT[domain.result] && domain.result !== 'match') reasons.push({ label: `Sender: ${domain.sender}${domain.known ? ` (your records: ${domain.known})` : ''}`, why: DOMAIN_TEXT[domain.result] });
  for (const [id, pts, label, why] of FLAGS) if (flags.has(id)) { score += pts; reasons.push({ label, why }); }
  score = Math.min(100, score);
  const level = score >= 50 ? 'high' : score >= 20 ? 'medium' : 'low';
  // Any change of payment details, or any gift card/crypto request, means hold until verified.
  const hold = level !== 'low' || flags.has('changedBank') || kind === 'bank-change' || flags.has('giftCards');
  if (domain.result === 'match' && (kind === 'bank-change' || flags.has('changedBank'))) reasons.push({ label: 'Right address, still unverified', why: DOMAIN_TEXT.match });
  return { score, level, hold, kind, reasons, domain };
}

export const VERIFY_STEPS = [
  'Don\'t reply to the email and don\'t use any phone number or link in it.',
  'Call the vendor on a number you already had: an old invoice, your contract, their website you type in yourself, or your accounting system.',
  'Ask for the person you normally deal with, and read back the new account details. Ask them to confirm the old ones too.',
  'Have a second person approve any change of bank details before the first payment goes out.',
  'Write down who confirmed it, when and on which number, and keep it with the invoice.',
];

export const IF_PAID = [
  'Call your bank\'s fraud line now and ask them to recall the payment. The first 24 to 72 hours matter most.',
  'Report it to the FBI at ic3.gov. For large wires, the FBI can sometimes help freeze the money.',
  'Change the passwords on your business email and turn on 2-step verification: fraudsters often read real email threads to time these requests.',
  'Tell the real vendor. Their mailbox may be the one that was hacked, and other customers may be targeted.',
];

/** A short written rule for the office wall or the finance folder. */
export function policyText(business = '') {
  const who = String(business || '').trim().slice(0, 80) || 'our business';
  return [
    `Payment verification rule for ${who}`,
    '',
    '1. We never change a vendor\'s bank details based on an email, text or letter alone.',
    '2. Every change is confirmed by phone on a number we already had, not one in the request.',
    '3. A second person approves the change before the first payment.',
    '4. We never pay with gift cards, crypto or payment apps, whoever asks, including the owner.',
    '5. Urgency or "keep this quiet" means we slow down, not speed up.',
    '6. If money went out by mistake: call the bank\'s fraud line at once, then report at ic3.gov.',
  ].join('\n');
}
