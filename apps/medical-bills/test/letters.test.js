import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { buildLetter, normalize, suggest, LETTERS, ERRORS } from '../lib/letters.js';

const BASE = {
  patient: 'Jordan Lee', address: '12 Elm St, Dayton, OH 45402', email: 'jordan@example.com',
  provider: 'Riverside General Hospital', providerAddress: 'PO Box 100, Dayton, OH 45401', account: 'RG-55821',
  serviceDates: 'March 3 to 5, 2026', amount: '4,812.50', insurer: 'Acme Health PPO', claim: 'C-778', date: 'November 7, 2026',
};

test('required fields are named plainly', () => {
  assert.throws(() => normalize({ ...BASE, patient: '' }), /your name/);
  assert.throws(() => normalize({ ...BASE, account: ' ' }), /account number/);
  assert.throws(() => buildLetter('nope', BASE), /Pick a letter/);
});

test('itemized bill request has the reference block, the codes ask and the collections hold', () => {
  const l = buildLetter('itemized', BASE);
  assert.match(l, /^Jordan Lee\n12 Elm St/);
  assert.match(l, /Re: Request for an itemized bill\nPatient: Jordan Lee\nAccount number: RG-55821\nDate\(s\) of service: March 3 to 5, 2026\nAmount billed: \$4,812.50\nInsurance: Acme Health PPO, claim number C-778/);
  assert.match(l, /CPT, HCPCS or revenue code/);
  assert.match(l, /not sent to collections/);
  assert.match(l, /or to jordan@example.com/);
  assert.match(l, /Sincerely,\n\n\nJordan Lee$/);
});

test('dispute letter lists the ticked problems and asks insurance to be billed', () => {
  assert.throws(() => buildLetter('dispute', BASE), /Tick at least one/);
  const l = buildLetter('dispute', { ...BASE, errors: ['duplicate', 'insurance', 'made-up'], details: 'CBC panel billed twice on March 3.' });
  assert.match(l, new RegExp(`- ${ERRORS.duplicate}`));
  assert.match(l, /Details:\nCBC panel billed twice/);
  assert.match(l, /submit the claim to my insurance \(Acme Health PPO\)/);
  assert.doesNotMatch(l, /made-up/);
});

test('financial assistance letter', () => {
  const l = buildLetter('assistance', { ...BASE, household: '3', income: '38000' });
  assert.match(l, /My household has 3 people, and our total yearly income is about \$38000\./);
  assert.match(l, /financial assistance policy/);
  assert.match(l, /start of my application/);
  assert.match(buildLetter('assistance', { ...BASE, household: '1' }), /has 1 person\./);
  assert.match(buildLetter('assistance', BASE), /hardship for me/);
});

test('surprise bill letters cover the three cases without promising an outcome', () => {
  const em = buildLetter('surprise', { ...BASE, surprise: 'emergency' });
  assert.match(em, /emergency care/);
  assert.match(em, /I believe this bill is covered by the federal No Surprises Act/);
  assert.match(em, /1-800-985-3059/);
  assert.match(buildLetter('surprise', { ...BASE, surprise: 'facility' }), /notice-and-consent/);
  const gfe = buildLetter('surprise', { ...BASE, surprise: 'estimate', estimate: '2,000', billDate: 'May 2, 2026' });
  assert.match(gfe, /Good Faith Estimate of \$2,000/);
  assert.match(gfe, /within 120 days of the date on the bill \(May 2, 2026\)/);
  for (const k of Object.keys(LETTERS)) {
    const text = buildLetter(k, { ...BASE, errors: ['paid'] });
    assert.doesNotMatch(text, /guarantee|you will win|legally required to cancel/i, k);
  }
});

test('which letters to send first', () => {
  assert.deepEqual(suggest({}), ['itemized']);
  assert.deepEqual(suggest({ haveItemized: true, cantAfford: true }), ['dispute', 'assistance']);
  assert.deepEqual(suggest({ surprise: true, cantAfford: true }), ['itemized', 'surprise', 'assistance']);
});

test('page says it is not legal advice and keeps data local', () => {
  const html = readFileSync(new URL('../index.html', import.meta.url), 'utf8');
  assert.match(html, /not legal or medical advice/);
  assert.match(html, /Nothing you type/);
});
