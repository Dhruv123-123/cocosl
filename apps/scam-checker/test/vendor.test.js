import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import * as V from '../lib/vendor.js';
import config from '../config.js';

test('domain of an email, a display-name address or a website', () => {
  assert.equal(V.domainOf('Billing <AR@Acme-Supply.com>'), 'acme-supply.com');
  assert.equal(V.domainOf('https://www.acmesupply.com/contact'), 'acmesupply.com');
  assert.equal(V.domainOf('not an address'), '');
});

test('sender compared with the vendor in your records', () => {
  const r = (k, s) => V.compareDomains(k, s).result;
  assert.equal(r('billing@acmesupply.com', 'jo@acmesupply.com'), 'match');
  assert.equal(r('acmesupply.com', 'ar@billing.acmesupply.com'), 'subdomain');
  assert.equal(r('acmesupply.com', 'ar@acme-supply.com'), 'lookalike', 'hyphen added');
  assert.equal(r('acmesupply.com', 'ar@acmesupply.co'), 'lookalike', 'different ending');
  assert.equal(r('acmesupply.com', 'ar@acmesuppply.com'), 'lookalike', 'one letter added');
  assert.equal(r('summitsupply.com', 'ar@summ1tsupply.com'), 'lookalike', 'digit for a letter');
  assert.equal(r('acmesupply.com', 'acme.ar@gmail.com'), 'freemail');
  assert.equal(r('acmesupply.com', 'ar@northwind.com'), 'different');
  assert.equal(r('', 'ar@acmesupply.com'), 'unknown');
  assert.equal(r('jo.plumber@gmail.com', 'jo.plumber@gmail.com'), 'match', 'a vendor that really uses Gmail');
});

test('a bank change is always held, even from the right address', () => {
  const r = V.checkRequest({ kind: 'bank-change', known: 'ar@acmesupply.com', sender: 'ar@acmesupply.com', flags: [] });
  assert.equal(r.hold, true);
  assert.ok(r.reasons.some((x) => /hacked real mailbox/.test(x.why)));
  const ok = V.checkRequest({ kind: 'invoice', known: 'ar@acmesupply.com', sender: 'ar@acmesupply.com', flags: [] });
  assert.deepEqual([ok.level, ok.hold, ok.reasons.length], ['low', false, 0]);
});

test('classic fraud scores high, and a mismatched reply-to is caught', () => {
  const r = V.checkRequest({ kind: 'bank-change', known: 'accounts@summitsupply.com', sender: 'accounts@summit-supply.co', replyTo: 'summit.ar.dept@gmail.com', flags: ['changedBank', 'urgent', 'bogus'] });
  assert.equal(r.level, 'high');
  assert.equal(r.score, 100);
  assert.ok(r.reasons.some((x) => /different address/.test(x.label)));
  assert.equal(V.checkRequest({ kind: 'boss', flags: ['giftCards'] }).level, 'high');
  assert.equal(V.checkRequest({ kind: 'nonsense' }).kind, 'invoice');
});

test('verify steps, if-paid steps and the written rule', () => {
  assert.match(V.VERIFY_STEPS.join(' '), /number you already had/);
  assert.match(V.IF_PAID.join(' '), /ic3\.gov/);
  assert.match(V.policyText('Prairie Dental'), /^Payment verification rule for Prairie Dental\n/);
  assert.match(V.policyText(''), /for our business/);
});

test('page: private, lead form for the B2B pack, pack hidden until its link is real', () => {
  const html = readFileSync(new URL('../vendor/index.html', import.meta.url), 'utf8');
  assert.match(html, /name="vendor-check"[^>]*data-netlify="true"/);
  assert.match(html, /<input type="hidden" name="form-name" value="vendor-check">/);
  assert.match(html, /Nothing you type leaves this browser/);
  assert.equal(config.vendorForm, 'vendor-check');
  assert.match(config.teamPack.url, /REPLACE_ME/);
  assert.match(readFileSync(new URL('../build.mjs', import.meta.url), 'utf8'), /'vendor\/'/);
});
