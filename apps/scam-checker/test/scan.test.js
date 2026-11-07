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

test('Spanish versions of common scams are caught', () => {
  const cases = [
    'USPS: Su paquete está retenido por dirección incompleta. Pague la tarifa de $1.99 en las próximas 24 horas: https://usps-entrega.top/pago',
    'Tiene un saldo de peaje pendiente de $6.99. Para evitar un cargo por mora, pague ahora: ezpass-pagos.vip',
    'Hola, soy reclutadora. Trabajo desde casa, gane $300 al día dando me gusta a videos. Escríbame por WhatsApp.',
    'Administración del Seguro Social: su número fue suspendido. Llame inmediatamente o habrá una orden de arresto.',
    'Le envié un código a su teléfono para verificar que es real, ¿me puede enviar el código?',
  ];
  for (const c of cases) assert.equal(analyzeMessage(c).level, 'high', c);
  assert.equal(analyzeMessage('Su código de verificación es 123456. No lo comparta con nadie.').level, 'low');
  assert.equal(analyzeMessage('¿Nos vemos el sábado para la comida de mamá?').level, 'low');
});

test('every rule, link issue, step and category has Spanish text', async () => {
  const { ES } = await import('../lib/i18n.js');
  const { STEPS, CATEGORIES, analyzeMessage: run } = await import('../lib/scan.js');
  for (const id of Object.keys(STEPS)) assert.ok(ES.steps[id], `step ${id}`);
  for (const [id] of CATEGORIES) assert.ok(ES.categories[id], `category ${id}`);
  // Trigger every rule and link check, then make sure each has a translation.
  const kitchenSink = 'URGENT gift card bitcoin zelle anydesk virus arrest you won package on hold fee unpaid toll refund earn $300/day guaranteed returns hi is this Sam? wrong number reply Y to activate the link whatsapp an agent will call you your SSN is suspended dear customer verify your account do not tell your bank stuck at customs need money send me the code password IRS $5 http://1.2.3.4 https://xn--pypal-4ve.com https://bit.ly/x http://user@paypa1-secure-login.a.b.c.top';
  const r = run(kitchenSink, { sender: 'PayPal <x@paypal-help.net>' });
  for (const s of r.signals) assert.ok(ES.signals[s.id], `signal ${s.id}`);
  for (const l of r.links) for (const i of l.issues) assert.ok(ES.links[i.code], `link ${i.code}`);
  for (const i of r.senderIssues) assert.ok(ES.links[i.code], `sender ${i.code}`);
});
