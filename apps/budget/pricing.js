// Pricing page (pricing.html): free vs Pro, buy buttons from config.pricing, license activation.
import config from './config.js';
import { initTracking, trackEvent, EVENTS } from './lib/track.js';
import { verifyLicense, isActive } from './lib/license.js';
import { checkoutOptions, compareRows, reasonText, keyFromUrl, limitPrompt, LIMIT_PROMPTS } from './lib/checkout.js';
import { $, esc, store } from './page.js';

const LKEY = 'mms-budget-license';
const from = new URLSearchParams(location.search).get('from') || 'pricing';
let license = null;
try { license = JSON.parse(store.get(LKEY)); } catch { /* none */ }

initTracking({ config, app: 'budget', page: 'pricing' });

if (LIMIT_PROMPTS[from]) { $('#from').textContent = limitPrompt(from); $('#from').hidden = false; }
$('#price-line').textContent = config.priceLine || '';
$('#pro-features').innerHTML = config.proFeatures.map((f) => `<li>${esc(f)}</li>`).join('');
$('#compare').innerHTML = compareRows().map((r) => `<tr><td>${esc(r.label)}</td><td>${esc(r.free)}</td><td class="${r.pro === 'No' ? '' : 'yes'}">${esc(r.pro)}</td></tr>`).join('');
if (config.refundPolicy) {
  $('#refund-line').textContent = config.refundPolicy;
  $('#refund-text').textContent = config.refundPolicy;
  $('#refund-faq').hidden = false;
}
for (const a of document.querySelectorAll('#site-link')) a.href = config.siteUrl;

function renderBuy() {
  if (isActive(license)) {
    $('#buy').innerHTML = '<a class="btn" href="./">Pro is on. Open the app</a>';
    $('#no-checkout').hidden = true;
    return;
  }
  const links = checkoutOptions(config);
  $('#buy').innerHTML = links.map((p) => `<a class="btn${p.best ? '' : ' ghost'}" href="${esc(p.url)}" data-id="budget-pro-${esc(p.id)}" data-upgrade="${esc(from)}" target="_blank" rel="noopener">${esc(p.label)}${p.note ? `<small>${esc(p.note)}</small>` : ''}</a>`).join('');
  const inStore = (config.distribution || 'web') !== 'web';
  $('#no-checkout').textContent = inStore ? 'Buy Pro in the app store version, or enter a key below.' : "Checkout isn't connected yet (set pricing links in config.js).";
  $('#no-checkout').hidden = links.length > 0;
}

async function activate(key) {
  $('#license-msg').textContent = 'Checking…';
  license = await verifyLicense(key, { endpoint: config.verifyEndpoint, previous: license });
  store.set(LKEY, JSON.stringify(license));
  $('#license-msg').innerHTML = license.valid ? 'Pro is on in this browser. <a href="./">Open the app</a>.' : esc(reasonText(license.reason));
  renderBuy();
  return license.valid;
}

$('#license-form').addEventListener('submit', (e) => { e.preventDefault(); activate($('#license-key').value); });
const returned = keyFromUrl(location.search);
if (returned) { history.replaceState(null, '', location.pathname + '#activate'); activate(returned); }
renderBuy();
if (!isActive(license)) trackEvent(EVENTS.upgradeShown, { where: `pricing:${from}` });
