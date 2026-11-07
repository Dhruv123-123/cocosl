// Email signup shared by the checker and the scam guides. Netlify Forms by default;
// any other provider posts to email.action from config.js.
import config from './config.js';

export function setupSignup(thanksBase = '') {
  const form = document.querySelector('form.signup');
  if (!form) return;
  const e = config.email;
  const pitch = document.querySelector('.signup-pitch');
  if (pitch) pitch.textContent = e.pitch;
  if (e.provider === 'none') { form.parentElement.hidden = true; return; }
  if (e.provider !== 'netlify') { form.removeAttribute('data-netlify'); form.action = e.action || '#'; form.querySelector('input[type=email]').name = e.emailField || 'email'; }
  form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    if (form.website.value) return; // honeypot
    if (e.provider !== 'netlify' && !e.action) { alert('Email signup is not connected yet: set email.action in config.js.'); return; }
    const btn = form.querySelector('button'); btn.disabled = true; btn.textContent = 'Sending…';
    try {
      await fetch(e.provider === 'netlify' ? '/' : form.action, { method: 'POST', mode: e.provider === 'netlify' ? 'same-origin' : 'no-cors', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: new URLSearchParams(new FormData(form)).toString() });
      location.href = /^https?:|^\//.test(e.thanksUrl) ? e.thanksUrl : thanksBase + e.thanksUrl;
    } catch { form.submit(); }
  });
}
