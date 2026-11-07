import { test } from 'node:test';
import assert from 'node:assert/strict';
import { analyzeMessage, analyzeUrl, extractUrls, deLeet } from '../lib/scan.js';

const ids = (r) => r.signals.map((s) => s.id);

test('classic USPS smishing text is high risk', () => {
  const r = analyzeMessage('USPS: Your package is on hold due to an incomplete address. Pay the $1.99 redelivery fee within 24 hours: https://usps-redelivery.top/pay');
  assert.equal(r.level, 'high');
  assert.ok(ids(r).includes('delivery'));
  assert.ok(r.links[0].issues.some((i) => /USPS/.test(i.label)));
  assert.equal(r.category, 'Fake delivery notice');
});

test('unpaid toll text is flagged as a toll scam', () => {
  const r = analyzeMessage('E-ZPass: You have an unpaid toll of $4.15. Pay now to avoid a $50 late fee: ezpass-tollservices.com/pay. Reply Y then reopen this message to activate the link.');
  assert.equal(r.level, 'high');
  assert.equal(r.category, 'Unpaid toll scam');
  assert.ok(ids(r).includes('reply-to-activate'));
});

test('gift card demand from the "IRS" is high risk', () => {
  const r = analyzeMessage('This is the IRS. A warrant has been issued for your arrest. Pay immediately with Google Play gift cards and do not tell your bank.');
  assert.equal(r.level, 'high');
  for (const id of ['gift-card', 'threat', 'government', 'secrecy']) assert.ok(ids(r).includes(id), id);
});

test('code-sharing request is caught', () => {
  const r = analyzeMessage("Hi it's Sam from Facebook Marketplace, I just sent a code to your phone to verify you're real, can you send me the code?");
  assert.ok(ids(r).includes('code-request'));
  assert.notEqual(r.level, 'low');
});

test('a legitimate one-time-code text stays low', () => {
  const r = analyzeMessage('Your Chase verification code is 492013. Chase will never call you to ask for this code. Don\'t share it.');
  assert.equal(r.level, 'low');
});

test('ordinary messages stay low and steps say it is not proof of safety', () => {
  const r = analyzeMessage('Hey, are we still on for dinner at 7? I booked the table at the usual place.');
  assert.equal(r.level, 'low');
  assert.equal(r.score, 0);
  assert.ok(r.steps.some((s) => /doesn't prove/.test(s)));
});

test('official links are not flagged', () => {
  assert.equal(analyzeUrl('https://www.usps.com/tracking').points, 0);
  assert.equal(analyzeUrl('https://tools.usps.com/go/TrackConfirmAction').points, 0);
  assert.equal(analyzeUrl('https://www.irs.gov/payments').points, 0);
});

test('look-alike and risky links are flagged', () => {
  assert.ok(analyzeUrl('http://paypa1-secure.com/login').issues.some((i) => /Look-alike/.test(i.label)));
  assert.ok(analyzeUrl('https://amazon.account-verify.xyz').points >= 45);
  assert.ok(analyzeUrl('http://192.168.4.20/bank').points >= 30);
  assert.ok(analyzeUrl('https://xn--pypal-4ve.com').points >= 30);
  assert.ok(analyzeUrl('https://bit.ly/3abcd').points >= 15);
});

test('short brand names need word boundaries', () => {
  assert.equal(analyzeUrl('https://startups.com/jobs').points, 0);
  assert.equal(analyzeUrl('https://firstbank.com').points, 0);
  assert.ok(analyzeUrl('https://ups-parcel-help.com').points >= 35);
});

test('extracts bare domains but not sentence typos or prices', () => {
  const urls = extractUrls('Pay now.Then visit usps-help.top/fee or www.example.com. It costs 4.99 today.');
  assert.deepEqual(urls.sort(), ['usps-help.top/fee', 'www.example.com'].sort());
});

test('sender impersonation is flagged', () => {
  const r = analyzeMessage('Your account has been locked. Verify your account here.', { sender: 'PayPal Security <alerts@paypal-support-center.net>' });
  assert.ok(r.senderIssues.length > 0);
  assert.equal(r.level, 'high');
});

test('job and investment scams', () => {
  const job = analyzeMessage('Remote position! Earn $300/day liking videos on TikTok. Message our recruiter on WhatsApp.');
  assert.ok(ids(job).includes('job'));
  assert.notEqual(job.level, 'low');
  const inv = analyzeMessage('My mentor showed me a trading platform with guaranteed returns of 30% a week. Deposit USDT to start.');
  assert.equal(inv.level, 'high');
});

test('Spanish scam phrases are recognised', () => {
  const r = analyzeMessage('URGENTE: su cuenta bloqueada. Envíe el código que le enviamos y pague con tarjetas de regalo.');
  assert.equal(r.level, 'high');
});

test('deLeet maps common substitutions', () => {
  assert.equal(deLeet('PAYPA1'), 'paypal');
  assert.equal(deLeet('amaz0n'), 'amazon');
  assert.equal(deLeet('rnicrosoft'), 'microsoft');
});

test('score is bounded and empty input is safe', () => {
  assert.equal(analyzeMessage('').score, 0);
  const r = analyzeMessage('URGENT gift card bitcoin wire transfer anydesk arrest warrant you won the lottery verify your account password ssn guaranteed returns http://1.2.3.4');
  assert.ok(r.score <= 100);
});
