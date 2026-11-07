import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { buildDebtLetter, normalize, LIMITS } from '../lib/debt.js';

const BASE = { name: 'Sam Rivera', address: '4 Oak Ave, Tulsa, OK 74103', collector: 'Apex Recovery LLC', collectorAddress: 'PO Box 9, Dallas, TX 75201', reference: 'AR-2219', creditor: 'Metro Bank Card', amount: '1,240.00', noticeDate: 'October 28, 2026', date: 'November 7, 2026' };

test('required details', () => {
  assert.throws(() => normalize({ ...BASE, name: '' }), /your name/);
  assert.throws(() => normalize({ ...BASE, collector: '' }), /collector/);
  assert.throws(() => normalize({ ...BASE, reference: '' }), /reference number/);
  assert.throws(() => buildDebtLetter('other', BASE), /Pick a letter/);
});

test('validation letter disputes, asks for proof and admits nothing', () => {
  const l = buildDebtLetter('validation', { ...BASE, limits: ['mailOnly', 'noWork', 'bogus'] });
  assert.match(l, /^Sam Rivera\n4 Oak Ave, Tulsa, OK 74103\n\nNovember 7, 2026\n\nApex Recovery LLC\nPO Box 9, Dallas, TX 75201\n\nRe: I dispute this debt and request validation\nYour reference number: AR-2219\nOriginal creditor \(as you stated\): Metro Bank Card\nAmount you say is owed: \$1,240.00\nDate of your letter to me: October 28, 2026/);
  assert.match(l, /I dispute this debt/);
  assert.match(l, /stop collection until you have sent me the verification/);
  assert.match(l, /name and address of the original creditor/);
  assert.match(l, /itemization/);
  assert.match(l, /not an acknowledgment that I owe this debt, and it is not a promise to pay/);
  assert.match(l, new RegExp(LIMITS.mailOnly.replace(/[.,]/g, '.')));
  assert.match(l, /workplace/);
  assert.doesNotMatch(l, /bogus|I will pay|guarantee/i);
});

test('cease letter, and no blank lines from missing optional fields', () => {
  const l = buildDebtLetter('cease', { name: 'Sam Rivera', collector: 'Apex Recovery LLC', reference: 'AR-2219', date: 'November 7, 2026' });
  assert.match(l, /^Sam Rivera\n\nNovember 7, 2026\n\nApex Recovery LLC\n\nRe: Stop contacting me about this debt\nYour reference number: AR-2219\n\nTo whom it may concern:/);
  assert.match(l, /stop communicating with me/);
  assert.match(l, /specific action that the law allows/);
  assert.match(l, /not an acknowledgment/);
  assert.doesNotMatch(l, /\n\n\n\n/);
});

test('page is framed as not legal advice and explains the limits of a stop letter', () => {
  const html = readFileSync(new URL('../debt.html', import.meta.url), 'utf8');
  assert.match(html, /Not legal advice/);
  assert.match(html, /the debt still exists/);
  assert.match(html, /If you're sued/);
});
