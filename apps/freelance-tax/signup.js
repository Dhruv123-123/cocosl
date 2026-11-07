// Email signup shared by the calculator and the /free/ pages. Netlify Forms by default;
// any other provider posts to email.action from config.js. Thanks page comes from data-thanks.
import config from './config.js';

export function setupSignup() {
  const e = config.email;
  document.querySelectorAll('.signup-pitch').forEach((p) => { p.textContent = e.pitch; });
  document.querySelectorAll('form.signup').forEach((form) => {
    if (e.provider === 'none') { form.parentElement.hidden = true; return; }
    if (e.provider !== 'netlify') {
      form.removeAttribute('data-netlify');
      form.action = e.action || '#';
      form.querySelector('input[type=email]').name = e.emailField || 'email';
    }
    form.addEventListener('submit', async (ev) => {
      ev.preventDefault();
      if (form.website.value) return; // honeypot
      if (e.provider !== 'netlify' && !e.action) { alert('Email signup is not connected yet: set email.action in config.js.'); return; }
      const btn = form.querySelector('button'); btn.disabled = true; btn.textContent = 'Sending…';
      try {
        await fetch(e.provider === 'netlify' ? '/' : form.action, {
          method: 'POST', mode: e.provider === 'netlify' ? 'same-origin' : 'no-cors',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: new URLSearchParams(new FormData(form)).toString(),
        });
        location.href = form.dataset.thanks || 'free/thanks/';
      } catch { form.submit(); }
    });
  });
}
