// GENERATED from apps/shared/ by tools/sync-shared.mjs. Edit the shared copy, not this one.
// Affiliate offer box: one matched offer under each free tool's result. Mounted by initTracking (track.js),
// so a tool page gets it with no extra wiring.
//
// TURN IT OFF everywhere: OFFERS.enabled = false below, then `node tools/sync-shared.mjs`.
// Turn it off on one page: add 'app/page' to OFFERS.off (page = the name passed to initTracking).
// GO LIVE: paste each program's tracking link into OFFERS.links. A box stays hidden while its link
// contains REPLACE_ME. Add ?offers=preview to any page to see where the box sits.
//
// FTC: every box carries a visible "Affiliate link" label and a one-line disclosure next to the link,
// and links get rel="sponsored". Medical-bill pages get no offer (people there are in debt); money
// calculators and the Scam Shield checker already have their own offer boxes, so they're skipped too.

export const OFFERS = {
  enabled: true,
  off: [],
  links: {
    identity: 'https://REPLACE_ME/aura',
    passwords: 'https://REPLACE_ME/password-manager',
    vpn: 'https://REPLACE_ME/nordvpn',
    hysa: 'https://REPLACE_ME/hysa',
    taxes: 'https://REPLACE_ME/keeper',
    credit: 'https://REPLACE_ME/credit-monitoring',
    debt: 'https://REPLACE_ME/balance-transfer',
  },
};

// Copy per offer: [title, blurb, button]. Kept general so any program in that category fits.
export const COPY = {
  identity: {
    en: ['Protect your identity', 'Identity theft protection watches your SSN, bank and credit for misuse, and helps you recover if it happens.', 'See identity protection plans'],
    es: ['Protege tu identidad', 'La protección contra robo de identidad vigila tu número de Seguro Social, tu banco y tu crédito, y te ayuda a recuperarte si pasa algo.', 'Ver planes de protección'],
  },
  passwords: {
    en: ['Stop fake sites from getting your password', 'A password manager won\'t fill in your password on a look-alike site, and gives every account its own password.', 'Try a password manager'],
    es: ['Que los sitios falsos no obtengan tu contraseña', 'Un administrador de contraseñas no llena tu contraseña en un sitio que imita a otro, y le da a cada cuenta su propia contraseña.', 'Probar un administrador de contraseñas'],
  },
  vpn: {
    en: ['Block scam sites before they load', 'Some VPNs include threat protection that blocks known scam and malware sites, handy on public Wi-Fi.', 'Compare VPN plans'],
    es: ['Bloquea sitios de estafa antes de que carguen', 'Algunas VPN incluyen protección que bloquea sitios de estafa y malware conocidos, útil en Wi-Fi público.', 'Comparar planes de VPN'],
  },
  hysa: {
    en: ['Make this money earn more', 'Online high-yield savings accounts have paid far more than big-bank savings. Check the current APY and FDIC insurance before you open one.', 'Compare high-yield savings'],
    es: ['Haz que este dinero gane más', 'Las cuentas de ahorro de alto rendimiento en línea han pagado mucho más que las de los bancos grandes. Revisa el APY actual y el seguro de la FDIC antes de abrir una.', 'Comparar cuentas de ahorro'],
  },
  taxes: {
    en: ['Find the write-offs you\'re missing', 'Expense apps for 1099 workers scan your bank and card for deductible costs and get them ready for tax time.', 'Try a write-off finder'],
    es: ['Encuentra las deducciones que se te pasan', 'Las apps de gastos para trabajadores 1099 revisan tu banco y tarjeta en busca de gastos deducibles y los dejan listos para los impuestos.', 'Probar una app de deducciones'],
  },
  credit: {
    en: ['Keep an eye on your credit', 'Credit monitoring alerts you when something changes on your report, so a new error or fraud doesn\'t sit there for months.', 'See credit monitoring'],
    es: ['Vigila tu crédito', 'El monitoreo de crédito te avisa cuando algo cambia en tu reporte, para que un error o un fraude no se quede ahí por meses.', 'Ver monitoreo de crédito'],
  },
  debt: {
    en: ['Check balance transfer offers', 'Only worth it if the new rate is lower, the fee is small, and you stop adding to the old card.', 'Compare balance transfer cards'],
    es: ['Revisa ofertas de transferencia de saldo', 'Solo conviene si la nueva tasa es más baja, la comisión es pequeña y dejas de usar la tarjeta vieja.', 'Comparar tarjetas'],
  },
};

const LABEL = { en: ['Affiliate link', 'We may earn a commission if you sign up, at no cost to you. It never changes what our tools tell you.'], es: ['Enlace de afiliado', 'Podemos ganar una comisión si te registras, sin costo para ti. Nunca cambia lo que te dicen nuestras herramientas.'] };

// Which offer goes under which tool. Key: 'app/page' as passed to initTracking. Anything not listed gets none.
export const PLACEMENT = {
  'scam-checker/link-checker': 'passwords',
  'scam-checker/family-setup': 'identity',
  'scam-checker/guides': 'identity',
  'scam-checker/app-quiz': 'identity',
  'scam-checker/app-checklist': 'identity',
  'budget/subscription-finder': 'hysa',
  'budget/budget': 'hysa',
  'budget/sinking-funds': 'hysa', 'budget/fondos-ahorro': 'hysa',
  'budget/savings-challenge': 'hysa', 'budget/reto-ahorro': 'hysa',
  'budget/paycheck-plan': 'hysa', 'budget/plan-quincena': 'hysa',
  'budget/holiday-planner': 'hysa',
  'budget/wedding-budget': 'hysa', 'budget/presupuesto-boda': 'hysa',
  'budget/moving-cost': 'hysa', 'budget/costo-mudanza': 'hysa',
  'budget/first-paycheck': 'hysa',
  'budget/checkup': 'hysa',
  'budget/rate-my-budget': 'hysa',
  'budget/afford-checker': 'hysa',
  'budget/couples': 'hysa',
  'budget/split-bills': 'hysa', 'budget/dividir-gastos': 'hysa',
  'budget/net-worth': 'hysa',
  'budget/money-personality': 'hysa',
  'budget/credit-disputes': 'credit',
  'budget/deal-countdown': 'debt',
  'freelance-invoices/set-aside': 'taxes',
  'freelance-invoices/side-hustle': 'taxes',
  'freelance-invoices/invoice-tracker': 'taxes',
  'freelance-invoices/rate': 'taxes',
  'freelance-invoices/app-quarterly': 'taxes',
  'freelance-invoices/app-mileage': 'taxes',
  'freelance-invoices/app-deductions': 'taxes',
};

const isLive = (u) => typeof u === 'string' && /^https:\/\//.test(u) && !/REPLACE_ME/i.test(u);

export function offerFor(app, page, o = OFFERS) {
  if (!o.enabled || !app) return null;
  const key = `${app}/${page}`;
  if (o.off.includes(key) || o.off.includes(app)) return null;
  // Scam guide pages pass their slug (toll-text-scam, mensaje-peaje-sin-pagar...), so any other Scam Shield
  // page except the checker (it has its own offers), the vendor check (businesses) and the app gets the guide offer.
  const guide = app === 'scam-checker' && page && !['checker', 'vendor-check'].includes(page) && !page.startsWith('app-');
  const id = PLACEMENT[key] || (guide ? PLACEMENT['scam-checker/guides'] : null);
  return id && COPY[id] ? id : null;
}

/** 'live' | 'preview' | null. */
export function offerMode({ id, search = '', embedded = false, o = OFFERS }) {
  if (!id || embedded) return null;
  if (isLive(o.links[id])) return 'live';
  return /(?:^|[?&])offers=preview(?:&|$)/.test(search) ? 'preview' : null;
}

const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
export function offerHtml({ id, app, page, lang = 'en', mode = 'live', o = OFFERS }) {
  const l = lang === 'es' ? 'es' : 'en';
  const [title, blurb, button] = COPY[id][l];
  const [label, note] = LABEL[l];
  const href = mode === 'live' ? o.links[id] : '#';
  return `<p style="margin:0 0 6px"><span style="display:inline-block;font-size:12px;font-weight:700;letter-spacing:.02em;padding:2px 8px;border-radius:999px;border:1px solid currentColor;opacity:.8">${esc(label)}</span></p>
<h2 style="margin:0 0 6px;font-size:19px">${esc(title)}</h2><p style="margin:0 0 10px;opacity:.85">${esc(blurb)}</p>
<a href="${esc(href)}" rel="sponsored noopener" target="_blank" data-offer="${esc(id)}" data-app="${esc(app)}" data-page="${esc(page)}" style="display:inline-flex;align-items:center;min-height:44px;font-weight:700;padding:8px 18px;border-radius:999px;background:#f2b134;color:#0b1d13;text-decoration:none"${mode === 'preview' ? ' aria-disabled="true"' : ''}>${esc(button)}</a>
<p style="margin:8px 0 0;font-size:13px;opacity:.8">${esc(note)}${mode === 'preview' ? (l === 'es' ? ' (Vista previa: el enlace todavía no está puesto.)' : ' (Preview: no link set yet.)') : ''}</p>`;
}

export function mountOffer({ app, page = '', win = globalThis.window, doc = globalThis.document, o = OFFERS } = {}) {
  try {
    if (!win || !doc?.body || doc.getElementById('mms-offer')) return false;
    const id = offerFor(app, page, o);
    const embedded = /(?:^|[?&])embed=1(?:&|$)/.test(win.location?.search || '') || win.self !== win.top;
    const mode = offerMode({ id, search: win.location?.search || '', embedded, o });
    if (!mode || doc.querySelector('[data-no-offer]')) return false;
    const lang = (doc.documentElement.lang || '').startsWith('es') ? 'es' : 'en';
    const box = doc.createElement('aside');
    box.id = 'mms-offer';
    box.setAttribute('aria-label', lang === 'es' ? 'Oferta de afiliado' : 'Affiliate offer');
    box.style.cssText = 'position:relative;max-width:760px;margin:24px auto;padding:16px;border:1px solid rgba(127,127,127,.35);border-radius:16px;box-sizing:border-box;width:calc(100% - 32px)';
    box.innerHTML = offerHtml({ id, app, page, lang, mode, o });
    // Under the tool: just above the email box if there is one, otherwise above the footer.
    const anchor = doc.getElementById('mms-optin') || doc.querySelector('footer');
    if (anchor?.parentNode) anchor.parentNode.insertBefore(box, anchor); else (doc.querySelector('main') || doc.body).append(box);
    box.querySelector('a').addEventListener('click', (ev) => {
      if (mode !== 'live') { ev.preventDefault(); return; }
      try { win.plausible?.('Affiliate', { props: { offer: id, app, page } }); } catch { /* analytics off */ }
    });
    return true;
  } catch { return false; }
}
