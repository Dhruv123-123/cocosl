import { test } from 'node:test';
import assert from 'node:assert/strict';
import { OFFERS, COPY, PLACEMENT, offerFor, offerMode, offerHtml } from '../offers.js';

const live = { ...OFFERS, links: { ...OFFERS.links, hysa: 'https://partner.example/hysa?ref=mms' } };

test('every placement points at an offer with English and Spanish copy and a link slot', () => {
  for (const [k, id] of Object.entries(PLACEMENT)) {
    assert.ok(COPY[id]?.en?.length === 3 && COPY[id]?.es?.length === 3, k);
    assert.ok(OFFERS.links[id], k);
  }
  for (const id of Object.keys(OFFERS.links)) assert.ok(COPY[id], id);
});

test('matched offers: savings tools, 1099 tools, scam guides; none on medical bills or the scam checker', () => {
  assert.equal(offerFor('budget', 'subscription-finder'), 'hysa');
  assert.equal(offerFor('freelance-invoices', 'app-quarterly'), 'taxes');
  assert.equal(offerFor('scam-checker', 'link-checker'), 'passwords');
  assert.equal(offerFor('scam-checker', 'toll-text-scam'), 'identity');
  assert.equal(offerFor('scam-checker', 'mensaje-peaje-sin-pagar'), 'identity');
  assert.equal(offerFor('scam-checker', 'checker'), null);
  assert.equal(offerFor('scam-checker', 'vendor-check'), null);
  assert.equal(offerFor('medical-bills', 'letters'), null);
  assert.equal(offerFor('money-calculators', 'debt-payoff'), null);
  assert.equal(offerFor('budget', 'pricing'), null);
});

test('switches: off everywhere, off per page or app', () => {
  assert.equal(offerFor('budget', 'budget', { ...OFFERS, enabled: false }), null);
  assert.equal(offerFor('budget', 'budget', { ...OFFERS, off: ['budget/budget'] }), null);
  assert.equal(offerFor('budget', 'checkup', { ...OFFERS, off: ['budget'] }), null);
  assert.equal(offerFor('budget', 'checkup', { ...OFFERS, off: ['budget/budget'] }), 'hysa');
});

test('hidden until the link is real; preview with ?offers=preview; never inside an embed', () => {
  assert.equal(offerMode({ id: 'hysa' }), null);
  assert.equal(offerMode({ id: 'hysa', search: '?offers=preview' }), 'preview');
  assert.equal(offerMode({ id: 'hysa', o: live }), 'live');
  assert.equal(offerMode({ id: 'hysa', o: live, embedded: true }), null);
  assert.equal(offerMode({ id: null, o: live }), null);
});

test('the box is labelled as an affiliate link, discloses, and marks the link sponsored', () => {
  const en = offerHtml({ id: 'hysa', app: 'budget', page: 'budget', o: live });
  assert.match(en, /Affiliate link/);
  assert.match(en, /may earn a commission/);
  assert.match(en, /rel="sponsored noopener"/);
  assert.match(en, /partner\.example\/hysa\?ref=mms/);
  const es = offerHtml({ id: 'taxes', app: 'freelance-invoices', page: 'rate', lang: 'es', mode: 'preview' });
  assert.match(es, /Enlace de afiliado/);
  assert.match(es, /href="#"/);
  assert.ok(!/REPLACE_ME/.test(es));
});
