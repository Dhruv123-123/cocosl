import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { clean, clientReference, tagLink, utmFrom, checkoutUtm, classify, rememberVisit, initTracking, EVENTS } from '../track.js';
import { APPS, ROOT, expected, sharedFiles } from '../../tools/sync-shared.mjs';
import { main, tagText, channelFor, bioLinks, wantsUtm } from '../../tools/utm.mjs';

// Expected values produced by the factory's funnel/attribution.py tag_link / client_reference,
// so links tagged in the browser match links tagged by the factory and its webhooks parse both.
const PY = [
  ['https://x.gumroad.com/l/kit', { source: 'pinterest', medium: 'social', campaign: 'pin-emergency-fund-3' },
    'https://x.gumroad.com/l/kit?utm_source=pinterest&utm_medium=social&utm_campaign=pin-emergency-fund-3'],
  ['https://moneymadesimple.netlify.app/blog/a/?ref=1#top', { source: 'Instagram Bio', medium: 'bio', campaign: '  launch week! ' },
    'https://moneymadesimple.netlify.app/blog/a/?ref=1&utm_source=Instagram-Bio&utm_medium=bio&utm_campaign=launch-week#top'],
  ['https://buy.stripe.com/abc123', { source: 'newsletter', medium: 'email', campaign: 'nl-2026-11-12' },
    'https://buy.stripe.com/abc123?utm_source=newsletter&utm_medium=email&utm_campaign=nl-2026-11-12&client_reference_id=newsletter__email__nl-2026-11-12'],
  ['https://x.com/?utm_source=keep&a=b c', { source: 'x', medium: 'social', campaign: 'c', content: 'ps' },
    'https://x.com/?utm_source=keep&a=b+c&utm_medium=social&utm_campaign=c&utm_content=ps'],
  ['mailto:hi@x.com', { source: 'x' }, 'mailto:hi@x.com'],
  ['https://buy.stripe.com/abc?client_reference_id=z', { source: 's', medium: 'm', campaign: 'c' },
    'https://buy.stripe.com/abc?client_reference_id=z&utm_source=s&utm_medium=m&utm_campaign=c'],
];

test('tagLink matches the factory attribution.py output', () => {
  for (const [url, utm, want] of PY) assert.equal(tagLink(url, utm), want);
  assert.equal(clientReference({ source: 'Pinterest', medium: 'social', campaign: 'pin_ef.3' }), 'Pinterest__social__pin-ef-3');
  assert.equal(clientReference({}), 'na__na__na');
  assert.equal(clean(' Héllo wörld!! '), 'H-llo-w-rld');
  assert.equal(clean('a'.repeat(80)).length, 60);
});

test('every app has an up-to-date copy of the shared modules', () => {
  for (const app of APPS) for (const f of sharedFiles()) {
    assert.equal(readFileSync(join(ROOT, app, 'lib', f), 'utf8'), expected(f), `${app}/lib/${f} is stale: run node tools/sync-shared.mjs`);
  }
});

test('checkout links carry the visit UTM, else the app', () => {
  assert.deepEqual(utmFrom('?utm_source=pinterest&utm_medium=social&utm_campaign=pin-1&x=2'), { source: 'pinterest', medium: 'social', campaign: 'pin-1' });
  assert.deepEqual(checkoutUtm({ source: 'pinterest', medium: 'social' }, 'budget', 'rate'), { source: 'pinterest', medium: 'social' });
  assert.deepEqual(checkoutUtm({}, 'money-calculators', 'debt-payoff'), { source: 'money-calculators', medium: 'app', campaign: 'debt-payoff' });
  assert.equal(classify('https://www.aura.com/x', 'sponsored noopener'), 'affiliate');
  assert.equal(classify('https://me.gumroad.com/l/kit'), 'product');
  assert.equal(classify('https://buy.stripe.com/x'), 'product');
  assert.equal(classify('https://ftc.gov'), '');
});

test('first UTM of the session wins', () => {
  const store = new Map();
  const storage = { getItem: (k) => store.get(k) ?? null, setItem: (k, v) => store.set(k, v) };
  assert.deepEqual(rememberVisit('', storage), {});
  assert.equal(rememberVisit('?utm_source=tiktok&utm_medium=bio', storage).source, 'tiktok');
  assert.equal(rememberVisit('?utm_source=pinterest', storage).source, 'tiktok');
  const broken = { getItem() { throw new Error('blocked'); } };
  assert.equal(rememberVisit('?utm_source=x', broken).source, 'x');
});

function fakePage(search = '') {
  const listeners = {};
  const head = [];
  const doc = {
    head: { append: (el) => head.push(el) },
    createElement: () => ({ dataset: {} }),
    addEventListener: (type, fn) => { listeners[type] = fn; },
  };
  const calls = [];
  const win = { location: { search }, sessionStorage: null };
  win.plausible = (...a) => calls.push(a);
  return { doc, win, head, calls, listeners };
}

test('initTracking stays off without a domain', () => {
  const p = fakePage();
  assert.equal(initTracking({ config: { analytics: { plausibleDomain: '' } }, app: 'x', doc: p.doc, win: p.win }), false);
  assert.equal(p.head.length, 0);
});

test('initTracking loads Plausible and sends click and signup events', () => {
  const p = fakePage('?utm_source=pinterest&utm_medium=social&utm_campaign=pin-ef-2');
  const config = { brand: 'Money Made Simple', analytics: { plausibleDomain: 'moneymadesimple.netlify.app' } };
  assert.equal(initTracking({ config, app: 'money-calculators', page: 'debt-payoff', doc: p.doc, win: p.win }), true);
  assert.equal(p.head[0].src, 'https://plausible.io/js/script.outbound-links.js');
  assert.equal(p.head[0].dataset.domain, 'moneymadesimple.netlify.app');

  const link = (href, rel = '', id) => ({ href, rel, dataset: id ? { id } : {} });
  const click = (a) => p.listeners.click({ target: { closest: () => a } });

  const product = link('https://me.gumroad.com/l/debt-planner');
  click(product);
  assert.equal(product.href, 'https://me.gumroad.com/l/debt-planner?utm_source=pinterest&utm_medium=social&utm_campaign=pin-ef-2');
  assert.deepEqual(p.calls.at(-1), [EVENTS.product, { props: { brand: 'Money Made Simple', app: 'money-calculators', link: 'me.gumroad.com' } }]);

  const aff = link('https://www.nerdwallet.com/x', 'sponsored noopener', 'debt');
  click(aff);
  assert.equal(aff.href, 'https://www.nerdwallet.com/x', 'affiliate links are never rewritten');
  assert.equal(p.calls.at(-1)[0], EVENTS.affiliate);
  assert.equal(p.calls.at(-1)[1].props.link, 'debt');

  const n = p.calls.length;
  click(link('https://consumer.ftc.gov/'));
  p.listeners.click({ target: { closest: () => null } });
  assert.equal(p.calls.length, n, 'plain links are left to the outbound-links script');

  p.listeners.submit({ target: { querySelector: () => ({}), getAttribute: () => 'debt-signup' } });
  assert.deepEqual(p.calls.at(-1), [EVENTS.signup, { props: { brand: 'Money Made Simple', app: 'money-calculators', form: 'debt-signup' } }]);
});

test('utm tool tags own links and checkout, never affiliate links', () => {
  const text = 'Read https://moneymadesimple.netlify.app/blog/x/. Buy https://me.gumroad.com/l/kit, or https://www.aura.com/?ref=1 and https://scamdecoded.netlify.app/?utm_source=keep';
  const { text: out, changed } = tagText(text, { source: 'pinterest', medium: 'social', campaign: 'pin-x-1' });
  assert.equal(changed.length, 2);
  assert.match(out, /blog\/x\/\?utm_source=pinterest&utm_medium=social&utm_campaign=pin-x-1\. Buy/);
  assert.match(out, /l\/kit\?utm_source=pinterest&utm_medium=social&utm_campaign=pin-x-1, or/);
  assert.match(out, /aura\.com\/\?ref=1 and/);
  assert.match(out, /\?utm_source=keep$/);
  assert.equal(wantsUtm('https://scamshield.netlify.app/scams/x/'), true);
});

test('bio links and channel names', () => {
  const mms = bioLinks()[0];
  assert.equal(mms.brand, 'Money Made Simple');
  assert.equal(mms.links.find((l) => l.platform === 'tiktok').url, 'https://moneymadesimple.netlify.app/links/?utm_source=tiktok&utm_medium=bio&utm_campaign=profile');
  assert.equal(channelFor({ source: 'pinterest', medium: 'social' }), 'pinterest');
  assert.equal(channelFor({ source: 'newsletter', medium: 'email' }), 'email');
  assert.equal(channelFor({ source: 'money-calculators', medium: 'app' }), 'apps');
  assert.equal(channelFor({ source: 'embed', medium: 'referral' }), 'referral');
  assert.equal(channelFor({}), 'direct');
});

test('utm CLI', () => {
  const out = [];
  assert.equal(main(['link', 'https://buy.stripe.com/x', '--source', 'x', '--medium', 'social', '--campaign', 'post-1'], (l) => out.push(l)), 0);
  assert.equal(out[0], 'https://buy.stripe.com/x?utm_source=x&utm_medium=social&utm_campaign=post-1&client_reference_id=x__social__post-1');
  assert.throws(() => main(['tag', 'f.md'], () => {}), /usage/);
  assert.equal(main([], () => {}), 0);
});
