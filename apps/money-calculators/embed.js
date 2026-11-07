// Drop-in loader for partner sites:
//   <div class="mms-calc" data-calc="debt-payoff" data-lang="en" data-accent="#1f6feb"></div>
//   <script src="https://YOUR-CALCULATORS-SITE/embed.js" async></script>
// Creates a responsive iframe for each div and keeps its height in sync. No cookies, no tracking.
(function () {
  var script = document.currentScript;
  var base = script ? script.src.replace(/embed\.js(\?.*)?$/, '') : '';
  var frames = {};
  document.querySelectorAll('.mms-calc:not([data-ready])').forEach(function (el, i) {
    var id = 'mms' + Date.now().toString(36) + i;
    var lang = el.getAttribute('data-lang') === 'es' ? 'es/' : '';
    var calc = (el.getAttribute('data-calc') || 'debt-payoff').replace(/[^a-z-]/g, '');
    var f = document.createElement('iframe');
    var q = '?embed=1&frame=' + id + (el.getAttribute('data-brand') === '0' ? '&brand=0' : '');
    // Styling and licence: data-accent="#1f6feb" data-theme="light|dark" data-radius="8" data-licence="KEY".
    ['accent', 'theme', 'radius', 'licence'].forEach(function (k) {
      var v = el.getAttribute('data-' + k);
      if (v) q += '&' + k + '=' + encodeURIComponent(v.replace(/^#/, ''));
    });
    // Starting numbers: data-values="salary=70000&state=CA" (letters, digits and . only).
    (el.getAttribute('data-values') || '').split('&').forEach(function (pair) {
      var m = /^([a-zA-Z0-9]{1,30})=([a-zA-Z0-9.]{1,20})$/.exec(pair.trim());
      if (m && ['embed', 'frame', 'brand', 'accent', 'theme', 'radius', 'licence'].indexOf(m[1]) < 0) q += '&' + m[1] + '=' + m[2];
    });
    f.src = base + lang + calc + '/' + q;
    f.title = el.getAttribute('data-title') || 'Money calculator';
    f.loading = 'lazy';
    f.style.cssText = 'width:100%;border:0;height:640px;display:block';
    el.setAttribute('data-ready', '1');
    el.appendChild(f);
    frames[id] = f;
  });
  window.addEventListener('message', function (e) {
    var d = e.data;
    if (!d || d.type !== 'mms-calc-height' || !frames[d.id]) return;
    if (base && e.origin !== new URL(base, location.href).origin) return;
    frames[d.id].style.height = Math.min(Math.max(d.height, 200), 4000) + 'px';
  });
})();
