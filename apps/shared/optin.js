// Email opt-in box, one component for every tool page. Mounted by initTracking (track.js), so a page
// gets it with no extra wiring. Shown under the tool, never as a popup (Google demotes mobile
// interstitials on pages people reach from search).
//
// TURN IT OFF everywhere: set OPTIN.enabled = false below, then `node tools/sync-shared.mjs`.
// GO LIVE: put the Sender form ID in OPTIN.senderFormId and set SENDER_API_TOKEN + SENDER_GROUP_ID in
// Netlify (see sender.js). Until the ID is filled in the box stays hidden; add ?optin=preview to any
// page to see it (the button is disabled in preview).
// A page that already has its own signup form (.signup, .signup-box, [data-no-optin]) doesn't get a second one.

export const OPTIN = {
  enabled: true,
  provider: 'sender',
  senderFormId: 'REPLACE_ME_SENDER_FORM_ID',
  endpoint: '/api/subscribe',
  skip: '.signup, .signup-box, form.signup, [data-no-optin], #mms-optin',
};

// Copy per brand. The first line names what they get now; the second the weekly email.
export const COPY = {
  mms: { en: ['Email me this plan', 'Get your numbers and the matching printable, plus one short money email a week. Unsubscribe any time.', 'Email me', 'Your email'], es: ['Envíame este plan', 'Recibe tus números y la hoja para imprimir, más un correo corto de dinero a la semana. Te das de baja cuando quieras.', 'Envíamelo', 'Tu correo'] },
  scam: { en: ['1 scam alert a week', 'Short enough to forward to your parents. The newest scams going around and how to spot them. Unsubscribe any time.', 'Sign me up', 'Your email'], es: ['1 alerta de estafa a la semana', 'Tan corta que la puedes reenviar a tus papás. Las estafas nuevas y cómo reconocerlas. Te das de baja cuando quieras.', 'Suscribirme', 'Tu correo'] },
  1099: { en: ['Get the freelancer tax calendar', 'Quarterly tax reminders a week before each due date, plus one short email a week for 1099 workers. Unsubscribe any time.', 'Send it', 'Your email'], es: ['Recibe el calendario de impuestos', 'Recordatorios de impuestos trimestrales una semana antes de cada fecha, más un correo corto a la semana. Te das de baja cuando quieras.', 'Envíamelo', 'Tu correo'] },
};
export const brandOf = (app) => (app === 'scam-checker' ? 'scam' : app === 'freelance-invoices' ? '1099' : 'mms');
export const live = (o = OPTIN) => o.enabled && typeof o.senderFormId === 'string' && o.senderFormId.length > 0 && !/REPLACE_ME/i.test(o.senderFormId);

/** 'live' | 'preview' | null (don't show). */
export function optinMode({ search = '', embedded = false, hasSignup = false, o = OPTIN } = {}) {
  if (!o.enabled || embedded || hasSignup) return null;
  if (live(o)) return 'live';
  return /(?:^|[?&])optin=preview(?:&|$)/.test(search) ? 'preview' : null;
}

const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
export function optinHtml({ app, lang = 'en', mode = 'live' }) {
  const [title, pitch, button, label] = COPY[brandOf(app)][lang === 'es' ? 'es' : 'en'];
  const preview = mode === 'preview';
  return `<h2 style="margin:0 0 6px;font-size:19px">${esc(title)}</h2><p style="margin:0 0 10px;opacity:.85">${esc(pitch)}</p>
<form style="display:flex;flex-wrap:wrap;gap:8px;align-items:center" novalidate>
<label for="mms-optin-email" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)">${esc(label)}</label>
<input id="mms-optin-email" name="email" type="email" autocomplete="email" required placeholder="${esc(label)}" style="flex:1 1 200px;min-width:0;min-height:44px;font:inherit;padding:8px 12px;border-radius:10px;border:1px solid rgba(127,127,127,.5);background:transparent;color:inherit">
<input name="website" tabindex="-1" autocomplete="off" aria-hidden="true" class="hp" style="position:absolute;left:-9999px;width:1px;height:1px">
<button type="submit" style="min-height:44px;font:inherit;font-weight:700;padding:8px 18px;border:0;border-radius:999px;background:#f2b134;color:#0b1d13;cursor:pointer"${preview ? ' disabled' : ''}>${esc(button)}</button>
</form><p class="mms-optin-msg" role="status" style="margin:8px 0 0;font-size:14px">${preview ? (lang === 'es' ? 'Vista previa: todavía no está conectado.' : 'Preview: not connected yet.') : ''}</p>`;
}

export function mountOptin({ app, page = '', win = globalThis.window, doc = globalThis.document, o = OPTIN } = {}) {
  try {
    if (!win || !doc?.body) return false;
    const embedded = /(?:^|[?&])embed=1(?:&|$)/.test(win.location?.search || '') || win.self !== win.top;
    const mode = optinMode({ search: win.location?.search || '', embedded, hasSignup: !!doc.querySelector(o.skip), o });
    if (!mode) return false;
    const lang = (doc.documentElement.lang || '').startsWith('es') ? 'es' : 'en';
    const box = doc.createElement('section');
    box.id = 'mms-optin';
    box.className = 'mms-optin';
    box.setAttribute('aria-label', lang === 'es' ? 'Suscríbete por correo' : 'Email signup');
    box.style.cssText = 'position:relative;max-width:760px;margin:24px auto;padding:16px;border:1px solid rgba(127,127,127,.35);border-radius:16px;box-sizing:border-box;width:calc(100% - 32px)';
    box.innerHTML = optinHtml({ app, lang, mode });
    const anchor = doc.querySelector('footer');
    if (anchor?.parentNode) anchor.parentNode.insertBefore(box, anchor); else (doc.querySelector('main') || doc.body).append(box);
    const form = box.querySelector('form');
    const msg = box.querySelector('.mms-optin-msg');
    form.addEventListener('submit', async (ev) => {
      ev.preventDefault();
      if (mode !== 'live') return;
      const email = form.email.value.trim();
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { msg.textContent = lang === 'es' ? 'Escribe un correo válido.' : 'Enter a valid email address.'; form.email.focus(); return; }
      const btn = form.querySelector('button'); btn.disabled = true;
      try {
        const res = await win.fetch(o.endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, website: form.website.value, formId: o.senderFormId, brand: brandOf(app), app, page, lang }) });
        if (!res.ok) throw new Error(String(res.status));
        msg.textContent = lang === 'es' ? '¡Listo! Revisa tu correo para confirmar.' : 'Done! Check your inbox to confirm.';
        form.reset();
        try { win.plausible?.('Signup', { props: { app, page, brand: brandOf(app), where: 'optin' } }); } catch { /* analytics off */ }
      } catch {
        msg.textContent = lang === 'es' ? 'No se pudo enviar. Inténtalo de nuevo en un rato.' : 'That didn\'t go through. Please try again in a bit.';
      } finally { btn.disabled = false; }
    });
    return true;
  } catch { return false; }
}

/**
 * Send one of the older signup forms (form.signup with a Netlify form-name) when email.provider is 'sender':
 * POST to /api/subscribe so the address reaches Sender and its welcome email. While Sender isn't connected
 * (503, or 404 on a single-app site with no function) the address is kept in Netlify Forms instead, so nobody is lost. Returns 'sender' or 'netlify'.
 */
export async function submitSignup(form, { app = '', page = '', endpoint = OPTIN.endpoint, win = globalThis.window } = {}) {
  const data = new FormData(form);
  const res = await win.fetch(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email: String(data.get('email') || ''), website: String(data.get('website') || ''), brand: brandOf(app), app, page }) }).catch(() => null);
  if (res && res.ok) return 'sender';
  if (res && ![404, 503].includes(res.status)) throw new Error(`signup ${res.status}`);
  await win.fetch('/', { method: 'POST', mode: 'same-origin', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: new URLSearchParams(data).toString() });
  return 'netlify';
}
