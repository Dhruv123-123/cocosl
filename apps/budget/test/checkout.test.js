import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import * as C from '../lib/checkout.js';
import { PLANS } from '../lib/plans.js';
import config from '../config.js';
import { createState, setIncome, thisMonth } from '../lib/budget.js';

const read = (f) => readFileSync(new URL(`../${f}`, import.meta.url), 'utf8');

test('checkout options: live links only, none in store builds', () => {
  const cfg = { pricing: {
    monthly: { label: '$3/month', url: 'https://mms.lemonsqueezy.com/buy/abc' },
    lifetime: { label: '$29 once', url: 'https://REPLACE_ME.lemonsqueezy.com/buy/x', best: true },
    stripe: { label: 'Card', url: '' },
    gum: { label: 'Gumroad', url: 'http://insecure.gumroad.com/l/x' },
  } };
  assert.deepEqual(C.checkoutOptions(cfg).map((o) => o.id), ['monthly']);
  assert.deepEqual(C.checkoutOptions({ ...cfg, distribution: 'play' }), []);
  assert.deepEqual(C.checkoutOptions(config), [], 'shipped config has placeholder links, so nothing is sold by accident');
});

test('license key handed back after checkout', () => {
  assert.equal(C.keyFromUrl('?session_id=cs_test_1'), 'cs_test_1');
  assert.equal(C.keyFromUrl('?license_key=38b1460a-5104-4067-a91d-77b872934d51&x=1'), '38b1460a-5104-4067-a91d-77b872934d51');
  assert.equal(C.keyFromUrl('?from=goals'), '');
  assert.equal(C.keyFromUrl(`?license_key=${'a'.repeat(201)}`), '');
  assert.match(C.reasonText('subscription_ended'), /ended/);
  assert.match(C.reasonText('lemonsqueezy_not_configured'), /not set up/);
  assert.equal(C.reasonText('weird'), 'That key did not work.');
});

test('comparison table and limit prompts come from PLANS', () => {
  const rows = C.compareRows();
  const cats = rows.find((r) => r.label === 'Budget categories');
  assert.deepEqual([cats.free, cats.pro], [String(PLANS.free.maxCategories), 'Unlimited']);
  assert.deepEqual(rows.find((r) => r.label.startsWith('Backup')).free, 'Yes');
  assert.match(C.limitPrompt('bills'), new RegExp(`tracks ${PLANS.free.bills} bills`));
  assert.match(C.limitPrompt('goals'), /1 savings goal/);
  for (const k of Object.keys(C.LIMIT_PROMPTS)) assert.ok(C.limitPrompt(k).length > 20, k);
  assert.equal(C.pricingHref('goals'), 'pricing.html?from=goals');
  assert.equal(C.pricingHref(), 'pricing.html');
});

test('onboarding: 50/30/20 starter plan adds up to take-home pay', () => {
  const s = createState();
  const plan = C.starterPlan(s.categories, 3201);
  const byGroup = (g) => s.categories.filter((c) => c.group === g).reduce((t, c) => t + plan[c.id], 0);
  assert.deepEqual([byGroup('needs'), byGroup('wants'), byGroup('savings')], [1601, 960, 640]);
  assert.equal(Object.values(plan).reduce((a, b) => a + b, 0), 3201);
  assert.ok(Object.values(plan).every((v) => Number.isInteger(v) && v >= 0));
  assert.deepEqual(Object.values(C.starterPlan(s.categories, -5)).filter(Boolean), []);
});

test('onboarding shows once, and only on a fresh budget', () => {
  const s = createState();
  assert.equal(C.needsOnboarding(s, null), true);
  assert.equal(C.needsOnboarding(s, '2026-11-07T00:00:00Z'), false);
  setIncome(s, thisMonth(), 2500);
  assert.equal(C.needsOnboarding(s, null), false, 'existing users never see it');
});

test('pages: every upgrade link is tracked and goes to the pricing page', () => {
  const html = read('pricing.html');
  assert.match(html, /<title>Pricing: The 20-Minute Budget/);
  assert.match(html, /"@type":"FAQPage"/);
  assert.match(html, /id="license-form"/);
  for (const f of ['bills.html', 'deals.html']) assert.match(read(f), /href="pricing\.html\?from=badge" data-upgrade="badge"/, f);
  assert.match(read('page.js'), /data-upgrade=/);
  assert.match(read('index.html'), /id="welcome"/);
  assert.match(read('sw.js'), /'pricing\.html'/);
  assert.doesNotMatch(read('pricing.html'), /REPLACE_ME/);
});
